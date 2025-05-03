from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
# Import models from the 'mchezo' app (assuming they are defined there)
from mchezo.models import Group, Member, Payment, Invite

# Import models defined in the current app ('multisyncbalance')
from .models import Balance, Provider
from .forms import GroupForm, PaymentForm, ReportIssueForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
from twilio.rest import Client
from django.conf import settings
import datetime
import json

@login_required
def dashboard(request):
    # Fetch all balances for the user
    balances = Balance.objects.filter(user=request.user).order_by('-date')

    # Calculate performance metrics
    total_commissions = 0
    for balance in balances:
        if balance.float_end is not None and balance.cash_end is not None:
            net_start = balance.cash_start + balance.float_start
            net_end = balance.cash_end + balance.float_end
            commission = net_end - net_start  # Net change in balance
            total_commissions += commission

    total_transactions = balances.count()

    # Calculate float growth as a percentage (considering both cash and float)
    float_growth = 0
    if balances.exists():
        first_balance = balances.first()
        if first_balance.cash_start + first_balance.float_start > 0:
            net_start = first_balance.cash_start + first_balance.float_start
            net_end = (first_balance.cash_end or 0) + (first_balance.float_end or 0)
            float_growth = ((net_end - net_start) / net_start * 100) if net_start > 0 else 0

    # Prepare chart data (net change over time)
    chart_labels = []
    chart_data = []
    for balance in balances:
        chart_labels.append(balance.date.strftime('%Y-%m-%d'))
        if balance.cash_end is not None and balance.float_end is not None:
            net_start = balance.cash_start + balance.float_start
            net_end = balance.cash_end + balance.float_end
            net_change = net_end - net_start
        else:
            net_change = 0
        chart_data.append(float(net_change))

    # Reverse the lists for chronological display
    chart_labels = chart_labels[::-1]
    chart_data = chart_data[::-1]

    # Convert to JSON for safe embedding in the template
    chart_labels_json = json.dumps(chart_labels)
    chart_data_json = json.dumps(chart_data)

    performance = {
        'commissions': total_commissions,
        'transactions': total_transactions,
        'float_growth': round(float_growth, 2)
    }

    return render(request, 'multisyncbalance/dashboard.html', {
        'chart_labels_json': chart_labels_json,
        'chart_data_json': chart_data_json,
        'performance': performance
    })

@login_required
def admin_dashboard(request, group_id):
    group = get_object_or_404(Group, id=group_id, admin=request.user)
    members = group.members.all()
    today = timezone.now().date()
    if request.GET.get('today'):
        payments = Payment.objects.filter(member__group=group, date=today)
    else:
        payments = Payment.objects.filter(member__group=group)
    return render(request, 'mchezo/admin_dashboard.html', {'group': group, 'members': members, 'payments': payments, 'today': today})

@login_required
def create_group(request):
    if request.method == 'POST':
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.admin = request.user
            group.save()
            Member.objects.create(group=group, user=request.user)
            invite = Invite.objects.create(group=group)
            invite_url = request.build_absolute_uri(f"/mchezo/join/{invite.token}/")
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Join {group.name}: {invite_url}",
                from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
                to=f"whatsapp:{request.user.phone_number}"
            )
            messages.success(request, 'Group created and invite sent via WhatsApp')
            return redirect('mchezo:dashboard')
    else:
        form = GroupForm()
    return render(request, 'mchezo/create_group.html', {'form': form})

@login_required
def join_group(request, token):
    invite = get_object_or_404(Invite, token=token, expires_at__gt=timezone.now())
    if Member.objects.filter(group=invite.group, user=request.user).exists():
        messages.error(request, 'You are already a member of this group')
        return redirect('mchezo:dashboard')
    Member.objects.create(group=invite.group, user=request.user)
    messages.success(request, 'Joined group successfully')
    return redirect('mchezo:dashboard')

@login_required
def log_payment(request, member_id):
    member = get_object_or_404(Member, id=member_id, group__admin=request.user)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.member = member
            payment.save()
            member.total_paid += payment.amount
            member.save()
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Your {payment.amount} TZS payment for {member.group.name} was logged on {payment.date}.",
                from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
                to=f"whatsapp:{member.user.phone_number}"
            )
            messages.success(request, 'Payment logged successfully')
            return redirect('mchezo:admin_dashboard', group_id=member.group.id)
    else:
        form = PaymentForm()
    return render(request, 'mchezo/log_payment.html', {'form': form, 'member': member})

@login_required
def report_issue(request, payment_id):
    payment = get_object_or_404(Payment, id=payment_id, member__user=request.user)
    if request.method == 'POST':
        form = ReportIssueForm(request.POST)
        if form.is_valid():
            issue = form.cleaned_data['issue']
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            client.messages.create(
                body=f"Issue reported for payment of {payment.amount} TZS on {payment.date}: {issue}",
                from_=f"whatsapp:{settings.TWILIO_PHONE_NUMBER}",
                to=f"whatsapp:{payment.member.group.admin.phone_number}"
            )
            messages.success(request, 'Issue reported successfully')
            return redirect('mchezo:dashboard')
    else:
        form = ReportIssueForm()
    return render(request, 'mchezo/report_issue.html', {'form': form, 'payment': payment})

@login_required
def export_pdf(request, group_id):
    group = get_object_or_404(Group, id=group_id, admin=request.user)
    members = group.members.all()
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    p.drawString(100, 800, f"{group.name} - Financial Report")
    y = 750
    for member in members:
        p.drawString(100, y, f"{member.user.phone_number}: Paid {member.total_paid} TZS, Debt {member.debt} TZS")
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{group.name}_report.pdf"'
    return response
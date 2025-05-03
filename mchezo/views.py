from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from .models import Group, Member, Payment, Invite
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
    member_groups = Member.objects.filter(user=request.user).select_related('group')
    admin_groups = Group.objects.filter(admin=request.user)

    # Prepare member data with progress percentages
    member_data = []
    for member in member_groups:
        progress_percentage = (
            (member.cycles_completed / member.group.max_members * 100)
            if member.group.max_members > 0 else 0
        )
        member_data.append({
            'group_name': member.group.name,
            'total_paid': float(member.total_paid),
            'debt': float(member.debt),
            'payments': [
                {'amount': float(payment.amount), 'date': payment.date.strftime('%Y-%m-%d')}
                for payment in member.payments.all()[:3]
            ],
            'progress_percentage': round(progress_percentage, 2),
            'last_payment_id': member.payments.last().id if member.payments.exists() else None
        })

    # Convert member_data to JSON
    member_data_json = json.dumps(member_data)

    return render(request, 'mchezo/dashboard.html', {
        'member_data_json': member_data_json,
        'admin_groups': admin_groups
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
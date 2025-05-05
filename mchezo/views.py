from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from .models import Group, Member, Payment, Invite
from .forms import GroupForm, PaymentForm, ReportIssueForm
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO

@login_required
def dashboard(request):
    member_groups = Member.objects.filter(user=request.user).select_related('group')
    admin_groups = Group.objects.filter(admin=request.user)
    member_data = []
    for member in member_groups:
        percentage = (
            (member.cycles_completed / member.group.max_members * 100)
            if member.group.max_members > 0 else 0
        )
        percentage = round(max(0, min(100, percentage)), 2)
        member_data.append({
            'member': member,
            'percentage': percentage,
            'latest_payment': member.payments.order_by('-date').first()
        })
    return render(request, 'mchezo/dashboard.html', {
        'member_data': member_data,
        'admin_groups': admin_groups
    })

@login_required
def admin_dashboard(request, group_id):
    group = get_object_or_404(Group, id=group_id, admin=request.user)
    members = group.members.all()  # This should now work with related_name='members'
    today = timezone.now().date()
    if request.GET.get('today'):
        payments = Payment.objects.filter(member__group=group, date=today)
    else:
        payments = Payment.objects.filter(member__group=group)
    member_data = [
        {
            'member': member,
            'has_paid_today': member.payments.filter(date=today).exists()
        }
        for member in members
    ]
    latest_invite = group.invites.order_by('-created_at').first()
    invite_url = request.build_absolute_uri(f"/mchezo/join/{latest_invite.token}/") if latest_invite else None
    return render(request, 'mchezo/admin_dashboard.html', {
        'group': group,
        'member_data': member_data,
        'payments': payments,
        'today': today,
        'invite_url': invite_url
    })

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
            if request.user.email:
                send_mail(
                    subject=f"Invitation to Join {group.name}",
                    message=f"You have been invited to join {group.name}. Click here: {invite_url}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[request.user.email]
                )
            messages.success(request, 'Group created. Invite link sent to your email or copy from admin dashboard.')
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
    if invite.group.members.count() >= invite.group.max_members:
        messages.error(request, 'Group has reached maximum members')
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
            expected_payment = member.group.contribution_amount
            payment_date = payment.date
            if payment_date < timezone.now().date() - timezone.timedelta(days=7):
                member.debt += expected_payment - payment.amount
            member.save()
            if member.user.email:
                send_mail(
                    subject=f"Payment Logged for {member.group.name}",
                    message=f"Your payment of {payment.amount} TZS for {member.group.name} was logged on {payment.date}.",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[member.user.email]
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
            if payment.member.group.admin.email:
                send_mail(
                    subject=f"Issue Reported for Payment in {payment.member.group.name}",
                    message=f"Issue reported for payment of {payment.amount} TZS on {payment.date}: {issue}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[payment.member.group.admin.email]
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
    p.drawString(100, 780, f"Generated on {timezone.now().date()}")
    y = 750
    for member in members:
        p.drawString(100, y, f"{member.user.first_name or member.user.phone_number}: Paid {member.total_paid} TZS, Debt {member.debt} TZS")
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
    p.showPage()
    p.save()
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{group.name}_report.pdf"'
    return response
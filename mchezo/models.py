from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import User
import uuid

class Group(models.Model):
    name = models.CharField(max_length=100, verbose_name=_('Group Name'))
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_groups', verbose_name=_('Admin'))
    contribution_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Contribution Amount'))
    frequency = models.CharField(max_length=20, choices=[('weekly', _('Weekly')), ('monthly', _('Monthly'))], verbose_name=_('Frequency'))
    created_at = models.DateTimeField(auto_now_add=True)
    max_members = models.PositiveIntegerField(default=50, verbose_name=_('Max Members'))

    class Meta:
        verbose_name = _('Group')
        verbose_name_plural = _('Groups')

    def __str__(self):
        return self.name

    def clean(self):
        if self.max_members > 50:
            raise ValidationError(_('Maximum 50 members allowed'))

class Member(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='members', verbose_name=_('Group'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_('User'))
    joined_at = models.DateTimeField(auto_now_add=True)
    total_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cycles_completed = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('group', 'user')
        verbose_name = _('Member')
        verbose_name_plural = _('Members')

    def __str__(self):
        return f"{self.user.phone_number} - {self.group.name}"

class Payment(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payments', verbose_name=_('Member'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    date = models.DateField(default=timezone.now, verbose_name=_('Date'))
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_('Amount must be positive'))
        if self.date > timezone.now().date():
            raise ValidationError(_('Future dates not allowed'))

class Payout(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='payouts', verbose_name=_('Member'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    date = models.DateField(default=timezone.now, verbose_name=_('Date'))
    delivered = models.BooleanField(default=False, verbose_name=_('Delivered'))

    class Meta:
        verbose_name = _('Payout')
        verbose_name_plural = _('Payouts')

class Invite(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='invites', verbose_name=_('Group'))
    token = models.UUIDField(default=uuid.uuid4, unique=True, verbose_name=_('Token'))
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        verbose_name = _('Invite')
        verbose_name_plural = _('Invites')

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(hours=24)
        super().save(*args, **kwargs)
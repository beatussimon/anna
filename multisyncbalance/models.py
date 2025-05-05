from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import User

class Provider(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='providers', verbose_name=_('User'))
    name = models.CharField(max_length=50, verbose_name=_('Provider Name'))
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.5, verbose_name=_('Commission Rate (%)'))

    class Meta:
        unique_together = ('user', 'name')
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')

    def __str__(self):
        return self.name

    def clean(self):
        if self.commission_rate < 0 or self.commission_rate > 100:
            raise ValidationError(_('Commission rate must be between 0 and 100%'))

class Balance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='balances', verbose_name=_('User'))
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name='balances', verbose_name=_('Provider'))
    cash_start = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Starting Cash'))
    float_start = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Starting Float'))
    cash_end = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Ending Cash'))
    float_end = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name=_('Ending Float'))
    date = models.DateField(default=timezone.now, verbose_name=_('Date'))
    created_at = models.DateTimeField(auto_now_add=True)
    is_balanced = models.BooleanField(default=False, verbose_name=_('Is Balanced'))

    class Meta:
        verbose_name = _('Balance')
        verbose_name_plural = _('Balances')

    def clean(self):
        if self.cash_start < 0 or self.float_start < 0:
            raise ValidationError(_('Starting balances cannot be negative'))
        if self.cash_end is not None and self.cash_end < 0:
            raise ValidationError(_('Ending cash cannot be negative'))
        if self.float_end is not None and self.float_end < 0:
            raise ValidationError(_('Ending float cannot be negative'))
        if self.date > timezone.now().date():
            raise ValidationError(_('Future dates not allowed'))
        if self.cash_end is not None and self.float_end is not None:
            net_start = self.cash_start + self.float_start
            net_end = self.cash_end + self.float_end
            self.is_balanced = net_start == net_end
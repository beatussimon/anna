from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Provider, Balance
from django.utils import timezone

class BalanceForm(forms.ModelForm):
    provider = forms.ModelChoiceField(
        queryset=None,
        label=_('Provider'),
        widget=forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'})
    )

    class Meta:
        model = Balance
        fields = ['provider', 'cash_start', 'float_start', 'cash_end', 'float_end', 'date']
        labels = {
            'cash_start': _('Starting Cash (TZS)'),
            'float_start': _('Starting Float (TZS)'),
            'cash_end': _('Ending Cash (TZS)'),
            'float_end': _('Ending Float (TZS)'),
            'date': _('Date'),
        }
        widgets = {
            'cash_start': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'min': '0'}),
            'float_start': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'min': '0'}),
            'cash_end': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'min': '0'}),
            'float_end': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'min': '0'}),
            'date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded-lg', 'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['provider'].queryset = Provider.objects.filter(user=user)

    def clean_cash_start(self):
        cash_start = self.cleaned_data['cash_start']
        if cash_start < 0:
            raise forms.ValidationError(_('Starting cash cannot be negative'))
        return cash_start

    def clean_float_start(self):
        float_start = self.cleaned_data['float_start']
        if float_start < 0:
            raise forms.ValidationError(_('Starting float cannot be negative'))
        return float_start

    def clean_cash_end(self):
        cash_end = self.cleaned_data.get('cash_end')
        if cash_end is not None and cash_end < 0:
            raise forms.ValidationError(_('Ending cash cannot be negative'))
        return cash_end

    def clean_float_end(self):
        float_end = self.cleaned_data.get('float_end')
        if float_end is not None and float_end < 0:
            raise forms.ValidationError(_('Ending float cannot be negative'))
        return float_end

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise forms.ValidationError(_('Future dates are not allowed'))
        return date
    
class GroupForm(forms.BaseModelForm):
    pass

class PaymentForm(forms.BaseModelForm):
    pass

class ReportIssueForm(forms.BaseModelForm):
    pass

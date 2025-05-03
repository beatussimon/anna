from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Group, Payment
from django.utils import timezone

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'contribution_amount', 'frequency', 'max_members']
        labels = {
            'name': _('Group Name'),
            'contribution_amount': _('Contribution Amount (TZS)'),
            'frequency': _('Frequency'),
            'max_members': _('Maximum Members'),
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'contribution_amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'min': '1000'}),
            'frequency': forms.Select(attrs={'class': 'w-full p-2 border rounded-lg'}),
            'max_members': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'min': '2', 'max': '50'}),
        }

    def clean_contribution_amount(self):
        amount = self.cleaned_data['contribution_amount']
        if amount < 1000:
            raise forms.ValidationError(_('Contribution amount must be at least 1000 TZS'))
        return amount

    def clean_max_members(self):
        max_members = self.cleaned_data['max_members']
        if max_members < 2 or max_members > 50:
            raise forms.ValidationError(_('Maximum members must be between 2 and 50'))
        return max_members

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'date']
        labels = {
            'amount': _('Amount (TZS)'),
            'date': _('Date'),
        }
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'w-full p-2 border rounded-lg', 'min': '1000'}),
            'date': forms.DateInput(attrs={'class': 'w-full p-2 border rounded-lg', 'type': 'date'}),
        }

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if amount < 1000:
            raise forms.ValidationError(_('Amount must be at least 1000 TZS'))
        return amount

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > timezone.now().date():
            raise forms.ValidationError(_('Future dates are not allowed'))
        return date

class ReportIssueForm(forms.Form):
    issue = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full p-2 border rounded-lg', 'rows': 4}),
        label=_('Describe the Issue'),
        max_length=500
    )
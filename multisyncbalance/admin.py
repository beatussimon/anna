from django.contrib import admin
from .models import Provider, Balance

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'commission_rate')
    search_fields = ('user__phone_number', 'name')
    list_filter = ('name',)

@admin.register(Balance)
class BalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'provider', 'cash_start', 'float_start', 'cash_end', 'float_end', 'date', 'is_balanced')
    search_fields = ('user__phone_number', 'provider__name')
    list_filter = ('date', 'is_balanced')
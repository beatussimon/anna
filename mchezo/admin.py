from django.contrib import admin
from .models import Group, Member, Payment, Payout, Invite

@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'admin', 'contribution_amount', 'frequency', 'created_at')
    search_fields = ('name', 'admin__phone_number')
    list_filter = ('frequency',)

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'total_paid', 'debt', 'cycles_completed')
    search_fields = ('user__phone_number', 'group__name')
    list_filter = ('group',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'date', 'created_at')
    search_fields = ('member__user__phone_number',)
    list_filter = ('date',)

@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ('member', 'amount', 'date', 'delivered')
    search_fields = ('member__user__phone_number',)
    list_filter = ('delivered', 'date')

@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    list_display = ('group', 'token', 'created_at', 'expires_at')
    search_fields = ('group__name',)
    list_filter = ('expires_at',)
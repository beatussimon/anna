from django.contrib import admin
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('phone_number', 'first_name')
    list_filter = ('is_active', 'is_staff')
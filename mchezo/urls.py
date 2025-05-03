from django.urls import path
from . import views

app_name = 'mchezo'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('admin/<int:group_id>/', views.admin_dashboard, name='admin_dashboard'),
    path('create-group/', views.create_group, name='create_group'),
    path('join/<uuid:token>/', views.join_group, name='join_group'),
    path('log-payment/<int:member_id>/', views.log_payment, name='log_payment'),
    path('report-issue/<int:payment_id>/', views.report_issue, name='report_issue'),
    path('export-pdf/<int:group_id>/', views.export_pdf, name='export_pdf'),
]
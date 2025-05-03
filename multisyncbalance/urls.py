from django.urls import path
from . import views

app_name = 'multisyncbalance'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    #path('balance/', views.balance_form, name='balance_form'),
    #path('export_pdf/', views.export_csv, name='export_pdf'),
]
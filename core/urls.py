from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('settings/', views.settings_view, name='settings'),
    path('set-language/<str:lang>/', views.set_language, name='set_language'),
    path('set-theme/', views.set_theme, name='set_theme'),
    path('help/', views.help_view, name='help'),
]
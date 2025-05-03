from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.utils.translation import activate
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import os
from twilio.rest import Client
from django.conf import settings

def home(request):
    with open(os.path.join(settings.BASE_DIR, 'services.json')) as f:
        services = json.load(f)
    return render(request, 'core/home.html', {'services': services})

def login_view(request):
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        otp = request.POST.get('otp')
        user = authenticate(request, phone_number=phone_number, otp=otp)
        if user:
            login(request, user)
            return redirect('home')
        messages.error(request, 'Invalid phone number or OTP')
    return render(request, 'core/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def settings_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        request.user.first_name = first_name
        request.user.save()
        messages.success(request, 'Profile updated')
    return render(request, 'core/settings.html')

def set_language(request, lang):
    if lang in ['en', 'sw']:
        activate(lang)
        request.session['language'] = lang
    return redirect(request.META.get('HTTP_REFERER', 'home'))

@csrf_exempt
def set_theme(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        theme = data.get('theme', 'light')
        request.session['theme'] = theme
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def help_view(request):
    faqs = [
        {'question': 'How do I join a Mchezo group?', 'answer': 'Click the WhatsApp link sent by the group admin.'},
        {'question': 'How do I balance my floats?', 'answer': 'Enter starting and ending balances in Wakala Balance.'},
    ]
    return render(request, 'core/help.html', {'faqs': faqs})
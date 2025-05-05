from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import Provider, Balance
import json
from decimal import Decimal
from django.utils import timezone

class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)  # Convert Decimal to float for JSON serialization
        return super().default(obj)

@login_required
def dashboard(request):
    providers = Balance.objects.select_related('provider').order_by('-date')[:5]
    
    # Calculate performance metrics
    total_commissions = sum(provider.commissions for provider in providers)
    total_transactions = sum(provider.transactions for provider in providers)
    float_growth = (
        (providers[0].float_end - providers[0].float_start) / providers[0].float_start * 100
        if providers and providers[0].float_start else 0
    )

    performance = {
        'commissions': total_commissions,
        'transactions': total_transactions,
        'float_growth': float_growth,
    }

    # Prepare chart data
    chart_data = [
        {
            'date': str(provider.date),
            'float_growth': float((provider.float_end - provider.float_start) / provider.float_start * 100
                              if provider.float_start else 0),
        }
        for provider in providers
    ]

    return render(request, 'multisyncbalance/dashboard.html', {
        'providers': providers,
        'performance': performance,
        'chart_data_json': json.dumps(chart_data, cls=DecimalEncoder),
    })

@login_required
def balance_form(request):
    if request.method == 'POST':
        provider_id = request.POST.get('provider')
        provider = Provider.objects.get(id=provider_id)
        date = request.POST.get('date')
        cash_start = request.POST.get('cash_start')
        float_start = request.POST.get('float_start')
        cash_end = request.POST.get('cash_end')
        float_end = request.POST.get('float_end')
        transactions = request.POST.get('transactions')
        commissions = request.POST.get('commissions')

        balance = Balance(
            provider=provider,
            date=date,
            cash_start=cash_start,
            float_start=float_start,
            cash_end=cash_end,
            float_end=float_end,
            transactions=transactions,
            commissions=commissions,
            is_balanced=(float(cash_start) + float(float_start) == float(cash_end) + float(float_end))
        )
        balance.save()
        return redirect('multisyncbalance:dashboard')

    providers = Provider.objects.all()
    return render(request, 'multisyncbalance/balance_form.html', {
        'providers': providers,
        'today': timezone.now().date(),
    })

@login_required
def export_csv(request):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="balances.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Provider', 'Starting Cash', 'Starting Float', 'Ending Cash', 'Ending Float', 'Transactions', 'Commissions', 'Balanced'])

    balances = Balance.objects.all()
    for balance in balances:
        writer.writerow([
            balance.date,
            balance.provider.name,
            balance.cash_start,
            balance.float_start,
            balance.cash_end,
            balance.float_end,
            balance.transactions,
            balance.commissions,
            'Yes' if balance.is_balanced else 'No'
        ])

    return response
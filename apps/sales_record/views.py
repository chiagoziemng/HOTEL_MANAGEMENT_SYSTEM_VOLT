from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum

from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa

from datetime import datetime, timedelta
from django.utils import timezone
from django.contrib import messages

import datetime
import datetime as dt
from django.core.paginator import Paginator

from apps.inventory_management.models import Sale, Debt
from apps.inventory_management.forms import SaleForm, DebtForm

# Sale & Debt Table Views and we have eight views now:    

# _list : this view show all sales , it contains: Filter sales by date range, pagination.
# _create: this view creates a new sale.
# _update: this view updates the sale, if errors when entering the sale.
# _delete: this view remove a sale and delete it from the Sale table.
# sale_report: this view shows todays sales report. it contains: Filter sales by date range, Calculate total sales, Get total sales for each mode of payment and Generate PDF.



# debt_list : this view show all debt , it contains: Filter sales by date range, pagination.
# clear_debt: this view clear debts.
# debt_delete: this view remove a debt and delete it from the debt table.


@login_required
def sale_list(request):
    sales = Sale.objects.all().order_by('-sale_date')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    if start_date and end_date:
        sales = sales.filter(sale_date__range=[start_date, end_date])
    paginator = Paginator(sales, 11) # Show 10 sales per page
    page = request.GET.get('page')
    sales = paginator.get_page(page)
    context = {
        'sales': sales,
        'section': 'sale_list'
    }
    return render(request, 'sale_list.html', context)

#                                                              sale_create              #2
@login_required
def sale_create(request):
    if request.method == 'POST':
        form = SaleForm(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            if sale.mode_of_payment == 'DEBT':
                sale.debtor_name = request.POST.get('debtor_name')
            elif sale.mode_of_payment == 'COMPLIMENTARY':
                sale.customer_name = request.POST.get('customer_name')
            sale.save()
            drink = sale.drink
            drink.number_sold += sale.quantity
            drink.total_stock -= sale.quantity
            drink.save()
            return redirect('sale_list')
    else:
        form = SaleForm(instance=Sale())
    return render(request, 'sale_create.html', {'form': form})

#                                                         sale_update                       #3
@login_required
def sale_update(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        form = SaleForm(request.POST, instance=sale)
        if form.is_valid():
            new_sale = form.save()
            drink = new_sale.drink
            drink.number_sold += new_sale.quantity - sale.quantity
            drink.total_stock -= new_sale.quantity - sale.quantity
            drink.save()
            return redirect('sale_list')
    else:
        form = SaleForm(instance=sale)
    return render(request, 'sale_update.html', {'form': form, 'sale': sale})

#                                                       sale_delete                 #4
@login_required
def sale_delete(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    if request.method == 'POST':
        drink = sale.drink
        drink.number_sold -= sale.quantity
        drink.total_stock = drink.total_stock + sale.quantity
        drink.save()
        sale.delete()
        return redirect('sale_list')
    return render(request, 'sale_confirm_delete.html', {'sale': sale})

#                                                           sale_report             #5
@login_required
def sale_report(request):
    # Set default date range to past week
    # Get today's date and use it as the default date for filtering
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    date_from = request.GET.get('date_from', week_ago)
    date_to = request.GET.get('date_to', today)

    # Validate date format
    try:
        date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        date_from = today
    try:
        date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
    except (TypeError, ValueError):
        date_to = today

    # Filter sales by date range
    sales = Sale.objects.filter(sale_date__range=[date_from, date_to])

    # Calculate total sales for the selected date range
    total_sales = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0

    # Get total sales for each mode of payment
    pos_sales = sales.filter(mode_of_payment='POS').aggregate(Sum('total_price'))['total_price__sum'] or 0
    transfer_sales = sales.filter(mode_of_payment='TRANSFER').aggregate(Sum('total_price'))['total_price__sum'] or 0
    cash_sales = sales.filter(mode_of_payment='CASH').aggregate(Sum('total_price'))['total_price__sum'] or 0
    debt_sales = sales.filter(mode_of_payment='DEBT').aggregate(Sum('total_price'))['total_price__sum'] or 0
    complimentary_sales = sales.filter(mode_of_payment='COMPLIMENTARY').aggregate(Sum('total_price'))['total_price__sum'] or 0

    context = {
        'sales': sales,
        'total_sales': total_sales,
        'date_from': date_from,
        'date_to': date_to,
        'pos_sales': pos_sales,
        'transfer_sales': transfer_sales,
        'cash_sales': cash_sales,
        'debt_sales': debt_sales,
        'complimentary_sales': complimentary_sales,
        'section': 'sale_report'
        
    }

    if request.method == 'POST':
        date_filter = request.POST.get('date_filter')
        if date_filter:
            # Filter sales by selected date
            sales = Sale.objects.filter(date_created__date=date_filter)
            total_sales = sales.aggregate(Sum('total_price'))['total_price__sum'] or 0
            pos_sales = sales.filter(mode_of_payment='POS').aggregate(Sum('total_price'))['total_price__sum'] or 0
            transfer_sales = sales.filter(mode_of_payment='TRANSFER').aggregate(Sum('total_price'))['total_price__sum'] or 0
            cash_sales = sales.filter(mode_of_payment='CASH').aggregate(Sum('total_price'))['total_price__sum'] or 0
            debt_sales = sales.filter(mode_of_payment='DEBT').aggregate(Sum('total_price'))['total_price__sum'] or 0
            complimentary_sales = sales.filter(mode_of_payment='COMPLIMENTARY').aggregate(Sum('total_price'))['total_price__sum'] or 0


            context.update({
                'sales': sales,
                'total_sales': total_sales,
                'pos_sales': pos_sales,
                'transfer_sales': transfer_sales,
                'cash_sales': cash_sales,
                'debt_sales': debt_sales,
                'complimentary_sales': complimentary_sales,
                'date_filter': date_filter,
                
            })



    # Generate PDF
    if 'download_pdf' in request.GET:
        template_path = 'sale_report_pdf.html'
        context = {
            'sales': sales, 
            'date_from': date_from, 
            'date_to': date_to, 
            'total_sales': total_sales,
                'pos_sales': pos_sales,
                'transfer_sales': transfer_sales,
                'cash_sales': cash_sales,
                'debt_sales': debt_sales,
                'complimentary_sales': complimentary_sales,
            }
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="sale_report.pdf"'
        template = get_template(template_path)
        html = template.render(context)
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('Error while creating PDF: %s' % pisa_status.err)
        return response
       
    return render(request, 'sale_report.html', context)


#                                                           debt_list                           #6
@login_required
def debt_list(request, status=None):
    if status == 'cleared':
        debts = Debt.objects.filter(status='Cleared').order_by('-date')
    elif status == 'owing':
        debts = Debt.objects.exclude(status='Cleared').order_by('-date')
    else:
        debts = Debt.objects.all().order_by('-date')

    date_query = request.GET.get('date')
    if date_query:
        date_obj = dt.datetime.strptime(date_query, '%Y-%m-%d').date()
        debts = debts.filter(date=date_obj)

    paginator = Paginator(debts, 10) # Show 10 debts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'debt_list.html', {'page_obj': page_obj, 'status': status, 'date': date_query, 'debts': debts,'section': 'debt_list'})

#                                                   clear_debt                                  #7
def clear_debt(request, pk):
    debt = Debt.objects.get(pk=pk)

    if request.method == 'POST':
        cleared_on = request.POST['cleared_on']
        debt.status = 'Cleared'
        debt.cleared_on = cleared_on
        debt.save()
        return redirect('debt_list')

    context = {'debt': debt}
    return render(request, 'clear_debt.html', context)


#                                                   debt_delete                                 #8
@login_required
def debt_delete(request, pk):
    debt = get_object_or_404(Debt, pk=pk)
    if request.method == 'POST':
        debt.delete()
        return redirect('debt_list')
    return render(request, 'debt_confirm_delete.html', {'debt': debt})

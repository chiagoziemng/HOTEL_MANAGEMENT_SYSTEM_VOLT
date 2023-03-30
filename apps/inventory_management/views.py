from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required

from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.template.loader import get_template
import csv
from django.contrib import messages


from .models import Drink, Stock
from .forms import DrinkForm,  StockForm,  ReduceStockForm
from .utils import render_to_pdf


from django.shortcuts import render
from .models import Drink

# Drink Table Views and we have five views now:

# _list : this view show all drinks , it contains: Filter drink by category, pagination and Generate PDF & CSV
# _detail : this view shows detail of a drink 
# _create: this view creates a new drink
# _update: this view updates the drink 
# _delete: this view remove a drink and delete it from the drink table

@login_required
def drink_list(request):
    category_filter = request.GET.get('category', None)
    stock_filter = request.GET.get('stock', None)
    categories = Drink.CATEGORY_CHOICES

    drinks = Drink.objects.all().order_by('name')
    if category_filter:
        drinks = drinks.filter(category=category_filter)
    if stock_filter:
        # filter by stock, excluding drinks with no stock
        drinks = drinks.exclude(stock=None).filter(Q(stock__lte=10) if stock_filter == 'low' else Q(stock__gt=10))

    paginator = Paginator(drinks, 11, 1)# count from 1, 10 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if 'export_pdf' in request.GET:
        template = get_template('drink_pdf.html')
        context = {'drinks': drinks}
        html = template.render(context)
        pdf = render_to_pdf('drink_pdf.html', context)
        if pdf:
            response = HttpResponse(pdf, content_type='application/pdf')
            filename = "drink_list_%s.pdf" % page_number
            content = "inline; filename='%s'" % filename
            download = request.GET.get("download")
            if download:
                content = "attachment; filename='%s'" % filename
            response['Content-Disposition'] = content
            return response
    elif 'export_csv' in request.GET:
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="drink_list.csv"'
        writer = csv.writer(response)
        writer.writerow(['Name', 'Category', 'total_stock', 'price'])
        for drink in drinks:
            writer.writerow([drink.name,  drink.get_category_display(), drink.total_stock, drink.price ])
        return response

    context = {
        'drinks': drinks,
        'page_obj': page_obj,
        'category_filter': category_filter,
        'stock_filter': stock_filter,
        'categories': categories,
        'section': 'drink_list'
    }
    return render(request, 'drink_list.html', context)

#                                         drink_details                                 #2
@login_required
def drink_detail(request, pk):
    drink = get_object_or_404(Drink, pk=pk)
    return render(request, 'drink_detail.html', {'drink': drink})

#                                          drink_create                                     #3
@login_required
def drink_create(request):
    if request.method == 'POST':
        form = DrinkForm(request.POST, request.FILES)
        if form.is_valid():
            drink = form.save(commit=False)
            if 'image' in request.FILES:
                drink.image = request.FILES['image']
            drink.save()
            return redirect('drink_list')
    else:
        form = DrinkForm()
    return render(request, 'drink_create.html', {'form': form})

#                                           drink_update                            #4
@login_required
def drink_update(request, pk):
    drink = get_object_or_404(Drink, pk=pk)
    if request.method == 'POST':
        form = DrinkForm(request.POST, request.FILES, instance=drink)
        if form.is_valid():
            form.save()
            return redirect('drink_list')
    else:
        form = DrinkForm(instance=drink)
    return render(request, 'drink_update.html', {'form': form})

#                                               drink_delete                        #5
@login_required
def drink_delete(request, pk):
    drink = get_object_or_404(Drink, pk=pk)
    if request.method == 'POST':
        drink.delete()
        return redirect('drink_list')
    return render(request, 'drink_confirm_delete.html', {'drink': drink})



@login_required
def reduce_stock(request):
    if request.method == 'POST':
        form = ReduceStockForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f"Stock reduced successfully!.")
            return redirect('drink_list')
        else:
            messages.error(request, 'Error adding stock. Please try again.')
    else:
        form = ReduceStockForm()
    context = {
        'form': form,
    }
    return render(request, 'reduce_stock.html', context)

@login_required
def add_stock(request):
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save()
            # do something with the newly created stock object
            messages.success(request, 'Stock added successfully!')
            return redirect('drink_list')
        else:
            messages.error(request, 'Error adding stock. Please try again.')
    else:
        form = StockForm()
    return render(request, 'add_stock.html', {'form': form})
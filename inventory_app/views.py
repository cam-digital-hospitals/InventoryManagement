from django.shortcuts import render, redirect, get_object_or_404
from .forms import StockUpdateForm, StockAddForm
from .models import InventoryItem, ItemWithdrawal, OrderItem, Location
from django.http import JsonResponse
from django.http import HttpResponse
from io import BytesIO
from openpyxl import Workbook
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.db.models import F, ExpressionWrapper, fields
from django.db import transaction
from django.db.models import Count, Case, When, IntegerField, Sum, Max, Avg, F
from django.db.models.functions import Coalesce
from urllib.parse import unquote as urlunquote
from django.views.decorators.csrf import csrf_exempt



@csrf_exempt
def get_item_by_barcode(request):
    if request.method == 'POST':
        barcode = request.POST.get('barcode')
        try:
            item = InventoryItem.objects.get(item_id=barcode)
            data = {
                'item_id': item.id,
                'supplier': item.supplier,
                'units': item.unit,
                'minimum_units': item.minimum_unit,
                'cost': item.cost,
                # 'location_id': item.location.id,  # Location ID
                'location_name': item.location.name,  # Location name
            }
            return JsonResponse(data)
        except InventoryItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    return JsonResponse({'error': 'Invalid request'}, status=400)

def get_item_details(request, item_id):
    item = InventoryItem.objects.get(pk=item_id)
    locations = item.location_set.all()  # Assuming each item is linked to multiple locations
    
    data = {
        'supplier': item.supplier,
        'units': item.unit,
        'minimum_units': item.minimum_unit,
        'cost': item.cost,
        'locations': [{'id': loc.id, 'name': loc.name} for loc in locations]
    }
    
    return JsonResponse(data)

def home(request):
    items = InventoryItem.objects.all()  # Retrieve all inventory items

    # items_on_order = OrderItem.objects.filter(on_order__gt=0).count()
    items_on_order = OrderItem.objects.filter(on_order__gt=0, completed=False).count()
    items_below_minimum = InventoryItem.objects.annotate(difference=ExpressionWrapper(F('unit') - F('minimum_unit'), output_field=fields.IntegerField())).filter(difference__lt=0).count()
    items_5_more_than_minimum = InventoryItem.objects.annotate(difference=ExpressionWrapper(F('unit') - F('minimum_unit'), output_field=fields.IntegerField())).filter(difference=5).count()
    items_greater_than_5_more_than_minimum = InventoryItem.objects.annotate(difference=ExpressionWrapper(F('unit') - F('minimum_unit'), output_field=fields.IntegerField())).filter(difference__gt=5).count()


    items_below_minimum_by_location = InventoryItem.objects.annotate(
        below_minimum=Case(
            When(unit__lt=F('minimum_unit'), then=1),
            default=0,
            output_field=IntegerField()
        )
    ).values('location__name').annotate(total_below_minimum=Sum('below_minimum')).order_by('location__name')

    locations = [item['location__name'] for item in items_below_minimum_by_location]
    below_minimum_counts = [item['total_below_minimum'] for item in items_below_minimum_by_location]


    context = {
        'items': items,
        'items_on_order': items_on_order,
        'items_below_minimum': items_below_minimum,
        'items_5_more_than_minimum': items_5_more_than_minimum,
        'items_greater_than_5_more_than_minimum': items_greater_than_5_more_than_minimum,
        'locations': locations,
        'below_threshold_counts': below_minimum_counts,
    }

    return render(request, 'inventory_app/home.html', context)




def server_status(request):
    return JsonResponse({'status': 'alive'})




def analyse(request):
    items = InventoryItem.objects.all()  # Retrieve all inventory items

    # items_on_order = OrderItem.objects.filter(on_order__gt=0).count()
    items_on_order = OrderItem.objects.filter(on_order__gt=0, completed=False).count()
    items_below_minimum = InventoryItem.objects.annotate(difference=ExpressionWrapper(F('unit') - F('minimum_unit'), output_field=fields.IntegerField())).filter(difference__lt=0).count()
    items_5_more_than_minimum = InventoryItem.objects.annotate(difference=ExpressionWrapper(F('unit') - F('minimum_unit'), output_field=fields.IntegerField())).filter(difference=5).count()
    items_greater_than_5_more_than_minimum = InventoryItem.objects.annotate(difference=ExpressionWrapper(F('unit') - F('minimum_unit'), output_field=fields.IntegerField())).filter(difference__gt=5).count()


    items_below_minimum_by_location = InventoryItem.objects.annotate(
        below_minimum=Case(
            When(unit__lt=F('minimum_unit'), then=1),
            default=0,
            output_field=IntegerField()
        )
    ).values('location__name').annotate(total_below_minimum=Sum('below_minimum')).order_by('location__name')

    locations = [item['location__name'] for item in items_below_minimum_by_location]
    below_minimum_counts = [item['total_below_minimum'] for item in items_below_minimum_by_location]

    ##########################################
    one_week_ago = timezone.now() - timezone.timedelta(days=7)
    # Query to get the total units withdrawn for each item in the last week, then order by the total and take the top 5
    top_withdrawals = ItemWithdrawal.objects.filter(date_withdrawn__gte=one_week_ago).values('item__item').annotate(total_withdrawn=Sum('units_withdrawn')).order_by('-total_withdrawn')[:5]

    items_labels = [withdrawal['item__item'] for withdrawal in top_withdrawals]
    withdrawals_data = [withdrawal['total_withdrawn'] for withdrawal in top_withdrawals]


    ##########################################
    # Query to calculate lead time and get the top 5 items with the longest lead times
    # top_lead_times = OrderItem.objects.annotate(
    #     lead_time=ExpressionWrapper(F('order_lead_time') - F('oracle_order_date'), output_field=fields.DurationField())
    # ).order_by('-lead_time')[:5]

    # items_lead_time_labels = [item.item.item for item in top_lead_times]  # Adjust based on your model's structure
    #    = [item.lead_time.days for item in top_lead_times]
    top_lead_times = OrderItem.objects.annotate(
    lead_time=ExpressionWrapper(F('order_lead_time') - F('oracle_order_date'), output_field=fields.DurationField())
    ).values('item__item') \
    .annotate(max_lead_time=Max('lead_time')) \
    .order_by('-max_lead_time')[:5]

    items_lead_time_labels = [item['item__item'] for item in top_lead_times]
    lead_times = [item['max_lead_time'].days for item in top_lead_times]  # Extracting days from lead time


    ####################EXPERIMENTAL FORECASTING######################

    # Calculate one week ago from now
    one_week_ago = timezone.now() - timezone.timedelta(days=7)

    # Get the average daily withdrawal rate for each item over the last week
    avg_withdrawals_per_item = ItemWithdrawal.objects.filter(date_withdrawn__gte=one_week_ago) \
        .values('item_id') \
        .annotate(avg_daily_withdrawn=Avg('units_withdrawn'))

    # Convert to a dictionary for easier access
    avg_withdrawals_dict = {withdrawal['item_id']: withdrawal['avg_daily_withdrawn'] for withdrawal in avg_withdrawals_per_item}

    # For each inventory item, calculate net stock and estimate days until stock runs out
    items_forecast = []
    for item in InventoryItem.objects.all():
        item_id = item.id
        total_on_order = OrderItem.objects.filter(item_id=item_id, completed=False) \
            .aggregate(total_on_order=Coalesce(Sum('on_order'), 0))['total_on_order']
        
        net_stock = item.unit - total_on_order
        avg_daily_withdrawn = avg_withdrawals_dict.get(item_id, 0)
        # net_stock = item.unit - OrderItem.objects.filter(item_id=item_id, completed=False).aggregate(total_on_order=Sum('on_order'))['total_on_order'] or 0
        
        # Avoid division by zero
        days_until_out = (net_stock / avg_daily_withdrawn) if avg_daily_withdrawn else float('inf')
        
        items_forecast.append({
            'item': item,
            'net_stock': net_stock,
            'avg_daily_withdrawn': avg_daily_withdrawn,
            'days_until_out': days_until_out,
            
        })
        print(items_forecast)



    context = {
        'items': items,
        'items_on_order': items_on_order,
        'items_below_minimum': items_below_minimum,
        'items_5_more_than_minimum': items_5_more_than_minimum,
        'items_greater_than_5_more_than_minimum': items_greater_than_5_more_than_minimum,
        'locations': locations,
        'below_threshold_counts': below_minimum_counts,
        'items_labels': items_labels,
        'withdrawals_data': withdrawals_data,
        'items_lead_time_labels': items_lead_time_labels,
        'lead_times': lead_times,
        'items_forecast': items_forecast,
    }

    return render(request, 'inventory_app/analyse.html', context)


def user(request): #this is the base withdrawal page
    items = InventoryItem.objects.all().order_by('item')  # Adjust ordering as needed
    return render(request, 'inventory_app/user.html', {'items': items})

def stock_check(request):
    # items = InventoryItem.objects.all().order_by('item')
    locations = Location.objects.all().order_by('name')  # Get all locations, order by name
    return render(request, 'inventory_app/stockcheck.html', {'locations': locations})

def get_items_for_location(request, location_name):
    decoded_name = urlunquote(location_name)  # Decode the URL-encoded location name
    location = Location.objects.filter(name=decoded_name).first()
    if location:
        items = InventoryItem.objects.filter(location=location)
        items_data = [{'id': item.id, 'name': item.item, 'units': item.unit} for item in items]
        return JsonResponse({'items': items_data})
    else:
        return JsonResponse({'error': 'Location not found'}, status=404)
    


def update_units_by_location(request):
    if request.method == 'POST':
        print(request.POST)  # Print the data received to debug
        location_name = request.POST.get('location')
        location = Location.objects.filter(name=location_name).first()
        if not location:
            return JsonResponse({'status': 'error', 'message': 'Location not found'}, status=404)

        responses = []
        items = InventoryItem.objects.filter(location=location)

        for item in items:
            item_id = f'units_{item.id}'
            units_value = request.POST.get(item_id)
            if units_value is None:
                responses.append(f"No units provided for {item.item}.")
                continue
            try:
                new_units = int(units_value)
                if new_units != item.unit:
                    old_units = item.unit
                    item.unit = new_units
                    item.save()

                    # Calculate the difference and adjust the sign
                    units_difference = old_units - new_units
                    if units_difference < 0:
                        units_difference = units_difference  # Make negative differences positive
                    else:
                        units_difference = units_difference  # Make positive differences negative

                    # Create a record in ItemWithdrawal with the adjusted difference
                    ItemWithdrawal.objects.create(
                        item=item,
                        location=location,
                        date_withdrawn=timezone.now(),
                        units_withdrawn=units_difference,  # Use the adjusted difference
                        withdrawn_by="Stock Check Audit"
                    )
                    responses.append(f"Updated {item.item} to {new_units} units, change recorded as {units_difference}.")
            except ValueError:
                responses.append(f"Invalid units for {item.item}")

        return JsonResponse({'status': 'success', 'messages': responses})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

def order(request):
    items = InventoryItem.objects.all().order_by('item')
    orders = OrderItem.objects.all().order_by('item')   
    return render(request, 'inventory_app/order.html', {'items': items, 'orders':orders})


def track(request):
    withdrawals = ItemWithdrawal.objects.all()  # Retrieve all withdrawal records
    return render(request, 'inventory_app/track.html', {'withdrawals': withdrawals})




def admin_view(request):
    # Initialise forms outside of the if block to ensure they are available in the entire function scope
    add_form = StockAddForm()
    update_form = StockUpdateForm()

    if request.method == 'POST':
        if 'add' in request.POST:  # If the add operation is requested
            add_form = StockAddForm(request.POST)  # Reinitialise with posted data
            if add_form.is_valid():
                add_form.save()
                return redirect('admin_view')  # Redirect to avoid double posting
        elif 'update' in request.POST:  # If the update operation is requested
            update_form = StockUpdateForm(request.POST)  # Reinitialise with posted data
            if update_form.is_valid():
                update_form.save()
                return redirect('admin_view')  # Redirect to avoid double posting

    items = InventoryItem.objects.all()  # Fetch items regardless of POST or GET request

    # Check if forms are valid and set error messages if not
    if 'add' in request.POST and not add_form.is_valid():
        add_error_message = "Please fill out all required fields."
    else:
        add_error_message = None

    return render(request, 'inventory_app/adminpage.html', {
        'update_form': update_form,
        'add_form': add_form,
        'items': items,
        'add_error_message': add_error_message,
    })


def get_item_details(request, item_id):
    item = InventoryItem.objects.filter(pk=item_id).first()
    if item:
        data = {
            'supplier': item.supplier if item.supplier else '',
            'units': item.unit,
            'minimum_units': item.minimum_unit,
            'cost': item.cost,
        }
        return JsonResponse(data)
    else:
        return JsonResponse({'error': 'Item not found'}, status=404)


def get_item_locations(request, item_id):
    # Fetch the item
    item = InventoryItem.objects.filter(pk=item_id).first()
    if not item:
        return JsonResponse({'error': 'Item not found'}, status=404)
    
    locations = Location.objects.filter(inventory_items=item).values('id', 'name')
    
    return JsonResponse(list(locations), safe=False)

def submit_withdrawal(request):
    if request.method == 'POST':
        item_id = request.POST.get('item')
        location_id = request.POST.get('location')
        
        # Ensure location_id is provided
        if not location_id:
            messages.error(request, 'Please select a location.')
            return redirect('user')  # or however you want to handle this error

        units_withdrawn = request.POST.get('units_withdrawn')
        
        # Ensure units_withdrawn is provided
        if not units_withdrawn:
            messages.error(request, 'Please enter the units to be withdrawn.')
            return redirect('user')
        
        try:
            units_withdrawn = int(units_withdrawn)
        except ValueError:
            messages.error(request, 'Invalid units value.')
            return redirect('user')

        # Fetch the InventoryItem and Location instances
        item = get_object_or_404(InventoryItem, id=item_id)
        location = get_object_or_404(Location, id=location_id)
        
        # Update InventoryItem units
        item.unit -= units_withdrawn
        item.save()
        
        # Record the withdrawal
        ItemWithdrawal.objects.create(
            item=item,
            location=location,
            units_withdrawn=units_withdrawn,
            withdrawn_by=request.POST.get('withdrawn_by'),
            date_withdrawn=timezone.now()
        )
        
        messages.success(request, 'Successfully recorded.')
        return redirect('user')
    else:
        return HttpResponse("Invalid request", status=400)


# def submit_withdrawal(request):
#     if request.method == 'POST':
#         item_id = request.POST.get('item')
#         location_id= request.POST.get('location')
#         units_withdrawn = int(request.POST.get('units_withdrawn'))
#         withdrawn_by = request.POST.get('withdrawn_by')
        
#         # Update InventoryItem
#         # item = InventoryItem.objects.get(id=item_id)
#         # item.unit -= units_withdrawn
#         # item.save()

#         # Fetch the InventoryItem instance
#         item = get_object_or_404(InventoryItem, id=item_id)
        
#         # Fetch the Location instance
#         location = get_object_or_404(Location, id=location_id)
        
#         # Update InventoryItem units
#         item.unit -= units_withdrawn
#         item.save()
        
#         # Record the withdrawal with Location instance
#         ItemWithdrawal.objects.create(
#             item=item,
#             location=location,  # Assign the Location instance here
#             units_withdrawn=units_withdrawn,
#             withdrawn_by=withdrawn_by,
#             date_withdrawn=timezone.now()
#         )
        
#         messages.success(request, 'Successfully recorded.')
#         items = InventoryItem.objects.all().order_by('item')

#         return render(request, 'inventory_app/user.html', {'items': items})
#     else:
#         return HttpResponse("Invalid request", status=400)





def download_stock_report(request):
    # Fetch data from your database
    data = InventoryItem.objects.all().values_list()  # This fetches all Stock items as tuples

    # Fetch headers dynamically from the database
    headers = []
    for field in InventoryItem._meta.get_fields():
        if hasattr(field, 'verbose_name'):
            headers.append(field.verbose_name.capitalize())

    # Create a workbook
    wb = Workbook()
    ws = wb.active
    
    ws.append(headers)

    # Write data to worksheet
    for row in data:
        ws.append(row)

    # Save the workbook to a virtual file
    virtual_workbook = BytesIO()
    wb.save(virtual_workbook)
    virtual_workbook.seek(0)

    # Build the response
    response = HttpResponse(virtual_workbook.getvalue(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="stock_report.xlsx"'

    return response




def track_withdrawals(request):
    unique_withdrawn_by = ItemWithdrawal.objects.order_by('withdrawn_by').values_list('withdrawn_by', flat=True).distinct()
    unique_items = InventoryItem.objects.order_by('item').distinct()
    selected_items = request.GET.getlist('item')  # Fetch selected items from request


    if request.method == 'GET':
        withdrawn_by = request.GET.get('withdrawn_by')
        selected_items = request.GET.getlist('item')  # This method handles multiple values for 'item'
        
        if withdrawn_by and withdrawn_by != "All":
            withdrawals = withdrawals.filter(withdrawn_by__icontains=withdrawn_by)
        if selected_items:
            withdrawals = withdrawals.filter(item__item__in=selected_items)
        
        # For CSV export
        if 'export' in request.GET:
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename="withdrawals.xlsx"'
            
            wb = Workbook()
            ws = wb.active
            ws.append(['Item', 'Date Withdrawn', 'Units Withdrawn', 'Withdrawn By'])
            
            for withdrawal in withdrawals:
                ws.append([
                    withdrawal.item.item,
                    withdrawal.date_withdrawn.strftime('%Y-%m-%d %H:%M'),
                    withdrawal.units_withdrawn,
                    withdrawal.withdrawn_by
                ])
                
            virtual_workbook = BytesIO()
            wb.save(virtual_workbook)
            virtual_workbook.seek(0)
            response.write(virtual_workbook.getvalue())
            return response

    return render(request, 'inventory_app/track.html', {
        'unique_withdrawn_by': unique_withdrawn_by,
        'unique_items': unique_items,
        'withdrawals': withdrawals,
        'selected_items': selected_items,
    })



def get_locations_for_item(request, item_id):
    locations = Location.objects.filter(inventory_items__id=item_id).values('id', 'name')
    return JsonResponse(list(locations), safe=False)


def order_view(request):
    if request.method == 'POST':
        item_id = request.POST.get('item')
        location_id = request.POST.get('location')  # This will be the ID of the location
        supplier = request.POST.get('supplier')
        units = request.POST.get('units') 
        minimum_units = request.POST.get('minimum_units')
        cost = request.POST.get('cost')
        unit_ord = request.POST.get('unit_ord')  
        request_date = request.POST.get('request_date')
        requested_by = request.POST.get('requested_by')
        oracle_order_date = request.POST.get('oracle_order_date')
        oracle_po = request.POST.get('oracle_po')
        order_lead_time = request.POST.get('order_lead_time')

        item = get_object_or_404(InventoryItem, id=item_id)
        location = get_object_or_404(Location, id=location_id)  # Fetch the Location instance
        
        # Record the order item
        OrderItem.objects.create(
            item=item,
            location=location,  # Use the Location instance here
            supplier=supplier,
            on_order=int(unit_ord),
            quantity_per_unit=units,
            unit=int(units),  # Assuming 'units' refers to 'unit' here; adjust if needed
            minimum_unit=int(minimum_units),
            cost=cost,  # Make sure to convert the string to a Decimal
            request_date=request_date,
            requested_by=requested_by,
            oracle_order_date=oracle_order_date,
            oracle_po=oracle_po,
            order_lead_time=order_lead_time
        )

        messages.success(request, 'Order successfully recorded.')
        items = InventoryItem.objects.all().order_by('item')
        orders = OrderItem.objects.all().order_by('item')
        
        return render(request, 'inventory_app/order.html', {'items': items, 'orders': orders})
    else:
        return HttpResponse("Invalid request", status=400)




def consolidate_stock(request, order_id):
    if request.method == 'POST':
        order_item = get_object_or_404(OrderItem, id=order_id)
        inventory_item = order_item.item  # Assuming 'item' is a ForeignKey to InventoryItem
        if not order_item.completed:
            inventory_item.unit += order_item.on_order
            inventory_item.save()
            order_item.completed = True
            order_item.save()
            return JsonResponse({'success': True, 'message': 'Stock consolidated successfully.'})
        else:
            return JsonResponse({'success': False, 'message': 'Order already completed.'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})


def item_search(request):
    item_name = request.GET.get('name', '')
    if not item_name:
        return JsonResponse({'error': 'No item name provided'}, status=400)

    items = InventoryItem.objects.filter(item__icontains=item_name)
    if not items.exists():
        return JsonResponse({'error': 'No items found'}, status=404)

    data = [{
        'item_name': item.item,
        'location': item.location.name,
        'units': item.unit
    } for item in items]

    count = items.count()
    client_ip = get_client_ip(request)
    server_ip = get_server_ip()

    return JsonResponse({
        'items': data,
        'count': count,
        'client_ip': client_ip,
        'server_ip': server_ip
    }, safe=False)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_server_ip():
    hostname = socket.gethostname()
    server_ip = socket.gethostbyname(hostname)
    return server_ip

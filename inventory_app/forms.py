from django import forms
from .models import InventoryItem, Location
from django.forms.widgets import TextInput, NumberInput, DateTimeInput, DateInput


class StockUpdateForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    class Meta:
        model = InventoryItem
        fields = ['item', 'location', 'supplier', 'quantity_per_unit', 'unit', 'minimum_unit', 'cost', 'supplier_link']

        widgets = {
            'unit': NumberInput(attrs={'step': "1"}),  # Adjust step for appropriate increments
            'minimum_unit': NumberInput(attrs={'step': "1"}),
            'cost': NumberInput(attrs={'step': "0.01"}),
            'item': TextInput(attrs={'type': 'text'}),
            'location': TextInput(attrs={'type': 'text'}),
            'supplier': TextInput(attrs={'type': 'text'}),
            'quantity_per_unit': TextInput(attrs={'type': 'text'}),
            'supplier_link': TextInput(attrs={'type': 'text'}),
        }


class StockAddForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    class Meta:
        model = InventoryItem
        fields = ['item', 'location','supplier', 'quantity_per_unit', 'unit', 'minimum_unit', 'cost', 'supplier_link']

        widgets = {
            'unit': NumberInput(attrs={'step': "1"}),  # Adjust step for appropriate increments
            'minimum_unit': NumberInput(attrs={'step': "1"}),
            'cost': NumberInput(attrs={'step': "0.01"}),
            'item': TextInput(attrs={'type': 'text'}),
            'location': TextInput(attrs={'type': 'text'}),
            'item_id': TextInput(attrs={'type': 'text', 'autofocus': 'autofocus'}),
            'supplier': TextInput(attrs={'type': 'text'}),
            'quantity_per_unit': TextInput(attrs={'type': 'text'}),
            'supplier_link': TextInput(attrs={'type': 'text'}),
        }



class OrderForm(forms.ModelForm):
    location = forms.ModelChoiceField(queryset=Location.objects.all(), required=True)
    class Meta:
        model = InventoryItem 
        fields = ['item', 'location', 'supplier', 'quantity_per_unit', 'unit', 'minimum_unit', 'cost'] 

        widgets = {
            'unit': NumberInput(attrs={'step': "1"}),
            'minimum_unit': NumberInput(attrs={'step': "1"}),
            'cost': NumberInput(attrs={'step': "0.01"}),  # Consider allowing decimal steps for cost
            'item': TextInput(attrs={'type': 'text'}),
            'location': TextInput(attrs={'type': 'text'}),
            'supplier': TextInput(attrs={'type': 'text'}),  # Added missing field
            'quantity_per_unit': TextInput(attrs={'type': 'text'}),
        }

# class OrderForm(forms.ModelForm):
#     class Meta:
#         model = InventoryItem
#         fields = ['item', 'supplier', 'quantity_per_unit', 'unit', 'minimum_unit', 'cost', 'request_date',
#          'requested_by', 'oracle_order_date', 'oracle_ordered_by', 'oracle_po', 'order_lead_time', 'supplier_link']

#         widgets = {
#             'request_date': DateTimeInput(attrs={'type': 'datetime-local'}),
#             'oracle_order_date': DateTimeInput(attrs={'type': 'datetime-local'}),
#             'order_lead_time': DateTimeInput(attrs={'type': 'datetime-local'}),
#             'unit': NumberInput(attrs={'step': "1"}),  # Adjust step for appropriate increments
#             'minimum_unit': NumberInput(attrs={'step': "1"}),
#             'cost': NumberInput(attrs={'step': "1"}),
#             'item': TextInput(attrs={'type': 'text'}),
#             'supplier': TextInput(attrs={'type': 'text'}),
#             'quantity_per_unit': TextInput(attrs={'type': 'text'}),
#             'oracle_ordered_by': TextInput(attrs={'type': 'text'}),
#             'oracle_po': TextInput(attrs={'type': 'text'}),
#             'requested_by': TextInput(attrs={'type': 'text'}),
#             'supplier_link': TextInput(attrs={'type': 'text'}),
#         }
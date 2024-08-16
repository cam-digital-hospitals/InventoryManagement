
from django.db import models
from django.utils import timezone
from datetime import datetime, date


class Location(models.Model):
    name = models.CharField(max_length=255,  default='Stores')  # A descriptive name for the location
    #best update the location names in the django admin page at the onset of the project.

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    item = models.CharField(max_length=255)
    item_id = models.CharField(max_length=255, default='No barcode')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='inventory_items')
    supplier = models.CharField(max_length=255)
    quantity_per_unit = models.CharField(max_length=100)  # Assuming this is a descriptive field
    unit = models.IntegerField()
    minimum_unit = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    supplier_link = models.CharField(max_length=255)


    def __str__(self):
        return self.item

class ItemWithdrawal(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='withdrawals')
    withdrawal_item_id = models.ForeignKey(InventoryItem, on_delete=models.SET_NULL, null=True, blank=True, related_name='withdrawal_item')
    # item_id = models.CharField(max_length=255, default='No barcode')
    date_withdrawn = models.DateTimeField(default=timezone.now)
    units_withdrawn = models.IntegerField()
    withdrawn_by = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.item} - {self.units_withdrawn} units"


class OrderItem(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='order_items')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='order_locations')
    supplier = models.CharField(max_length=255)
    on_order = models.IntegerField(default=0)
    quantity_per_unit = models.CharField(max_length=100)  # Assuming this is a descriptive field
    unit = models.IntegerField()
    minimum_unit = models.IntegerField()
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    request_date = models.DateField()
    requested_by = models.CharField(max_length=255)
    oracle_order_date = models.DateField()
    oracle_po = models.CharField(max_length=255)
    order_lead_time = models.DateField()
    completed = models.BooleanField(default=False)

    def __str__(self):
        return str(self.item)

    def calculate_lead_time(self):
        if self.order_lead_time and self.oracle_order_date:
            return (self.order_lead_time - self.oracle_order_date).days
        return 0

    def days_since_oracle_order(self):
        return (date.today() - self.oracle_order_date).days if self.oracle_order_date else 0



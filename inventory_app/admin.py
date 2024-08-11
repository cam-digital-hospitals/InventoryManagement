from django.contrib import admin

from .models import InventoryItem, ItemWithdrawal, OrderItem, Location

admin.site.register(InventoryItem)
admin.site.register(ItemWithdrawal)
admin.site.register(OrderItem)
admin.site.register(Location)

# Register your models here.

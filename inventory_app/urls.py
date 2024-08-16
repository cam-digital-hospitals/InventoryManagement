from django.urls import path
from django.urls import re_path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('adminpage/', views.admin_view, name='admin_view'),
    path('adminpage/download_stock_report/', views.download_stock_report, name='download_stock_report'),
    path('get-item-details/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('get-item-locations/<int:item_id>', views.get_item_locations, name='get_item_locations'),
    path('user/', views.user, name='user'),
    path('stockcheck/', views.stock_check, name='stock_check'),
    re_path(r'^get-items-for-location/(?P<location_name>.+)$', views.get_items_for_location, name='get_items_for_location'),
    path('update-units-by-location/', views.update_units_by_location, name='update_units_by_location'),
    path('submit-withdrawal/', views.submit_withdrawal, name='submit_withdrawal'),
    path('track/', views.track, name='track'),
    path('track-withdrawals/', views.track_withdrawals, name='track_withdrawals'),
    path('order/', views.order, name='order'),
    path('order_view/', views.order_view, name='order_view'),
    path('consolidate-stock/<int:order_id>/', views.consolidate_stock, name='consolidate_stock'),
    path('get-locations-for-item/<int:item_id>/', views.get_locations_for_item, name='get-locations-for-item'),
    path('analyse/', views.analyse, name='analyse'),
    path('item/', views.item_search, name='item_search'),
    path('server-status/', views.server_status, name='server_status'),
    path('get-item-by-barcode/', views.get_item_by_barcode, name='get_item_by_barcode'),
    path('get-item-details/<int:item_id>/', views.get_item_details, name='get_item_details'),

    # Define other URLs for your app
]

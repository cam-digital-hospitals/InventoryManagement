from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('adminpage/', views.admin_view, name='admin_view'),
    path('adminpage/download_stock_report/', views.download_stock_report, name='download_stock_report'),
    path('get-item-details/<int:item_id>/', views.get_item_details, name='get_item_details'),
    path('get-item-locations/<int:item_id>', views.get_item_locations, name='get_item_locations'),
    path('user/', views.user, name='user'),
    path('submit-withdrawal/', views.submit_withdrawal, name='submit_withdrawal'),
    path('track/', views.track, name='track'),
    path('track-withdrawals/', views.track_withdrawals, name='track_withdrawals'),
    path('order/', views.order, name='order'),
    path('order_view/', views.order_view, name='order_view'),
    path('consolidate-stock/<int:order_id>/', views.consolidate_stock, name='consolidate_stock'),
    path('get-locations-for-item/<int:item_id>/', views.get_locations_for_item, name='get-locations-for-item'),
    path('analyze/', views.analyze, name='analyze'),

    # Define other URLs for your app
]

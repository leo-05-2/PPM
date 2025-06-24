from django.urls import path

from .views import *

app_name = 'cart'

urlpatterns = [

    path('', view_cart, name='view_cart'),
    path('add_item/', add_cart_item, name='add_cart_item'),
    path( 'update_item/<int:item_id>/', update_item, name='update_item'),
    path('remove_item/<int:item_id>/', remove_item, name='remove_item'),
    path('checkout/', checkout, name='checkout'),
    path('update_shipping/<str:method>/', update_shipping, name='update_shipping'),
    path ('checkout_success/', checkout_success, name='checkout_success'),
    path ('order_detail/<int:order_id>/', OrderDetailView.as_view(), name='order_detail'),
    path('order_history/', OrderHistoryView.as_view(), name='order_history'),
    path (' update_order_status/<int:order_id>/', update_order_status, name='update_order_status'),

]
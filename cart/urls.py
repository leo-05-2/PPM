from django.urls import path

from .views import (
    update_cart_address,
    view_cart,
    add_cart_item,
    update_item,
    remove_item,
    checkout,
    update_shipping
)

app_name = 'cart'

urlpatterns = [
    path('update_address/', update_cart_address, name='update_cart_address'),
    path('', view_cart, name='view_cart'),
    path('add_item/', add_cart_item, name='add_cart_item'),
    path( 'update_item/<int:item_id>/', update_item, name='update_item'),
    path('remove_item/<int:item_id>/', remove_item, name='remove_item'),
    path('checkout/', checkout, name='checkout'),
    path('update_shipping/<str:method>/', update_shipping, name='update_shipping'),
]
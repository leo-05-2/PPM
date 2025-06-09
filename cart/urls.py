from django.urls import path

from .views import (
    update_cart_address,
    view_cart,
)

app_name = 'cart'

urlpatterns = [
    path('update_address/', update_cart_address, name='update_cart_address'),
    path('', view_cart, name='view_cart'),
]
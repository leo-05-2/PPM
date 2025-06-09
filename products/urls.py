from django.urls import path
from .views import *
app_name = 'products'

urlpatterns = [
    path('product/<int:product_id>/', product_info, name='product_info'),

]

from django.urls import path
from .views import *
app_name = 'products'

urlpatterns = [
    path('product/<int:product_id>/', product_info, name='product_info'),
    path('product/<int:product_id>/', product_info, name='product_info_detail'),
    path('product_list_category/<int:category_id>/', product_list_category, name='product_list_category'),
    path('product_list_category/', product_list_category, name='product_list_by_category'),


]

from django.urls import path
from .views import *
app_name = 'products'

urlpatterns = [
    path('product/<int:product_id>/', product_info, name='product_info'),
    path('product/<int:product_id>/', product_info, name='product_info_detail'),
    path('product_list_category/<int:category_id>/', product_list_category, name='product_list_category'),
    path('product_list_category/', product_list_category, name='product_list_by_category'),

    path('manage/', ProductManageListView.as_view(), name='product_manage_list'),
    path('create/', ProductCreateView.as_view(), name='product_create'),
    path('<int:product_id>/edit/', ProductUpdateView.as_view(), name='product_edit'),
    path('<int:product_id>/delete/', ProductDeleteView.as_view(), name='product_delete'),
    path('product_list', product_list, name='product_list'),


]

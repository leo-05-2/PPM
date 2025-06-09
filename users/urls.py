from django.urls import path
from .views import (
    user_home_page,
    UserLoginView,
    UserSignUpView,
    UserLogoutView,
    UserAccountView,
    update_profile,
    change_password,
    add_address, delete_address,






)

app_name = 'users'

urlpatterns = [
    path('user_home_page/', user_home_page, name='user_home_page'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('sign_up/', UserSignUpView.as_view(), name='sign_up'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path( 'account/', UserAccountView.as_view(), name='account'),
    path('update_profile/', update_profile, name='update_profile'),
    path('change_password/', change_password, name='change_password'),
    path('add_address/', add_address, name='add_address'),
    path('delete_address/<int:address_id>/', delete_address, name='delete_address'),


]

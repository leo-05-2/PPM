from django.urls import path
from .views import (
    home_page,
    about_page,
    contact_page,
    privacy_policy_page,
    terms_of_service_page,
)
app_name = 'core'

urlpatterns = [
    path('', home_page, name='home'),
    path('about/', about_page, name='about'),
    path('contact/', contact_page, name='contact'),
    path('privacy_policy/', privacy_policy_page, name='privacy_policy'),
    path('terms_of_service/', terms_of_service_page, name='terms_of_service'),
]


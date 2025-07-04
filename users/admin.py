from django.contrib import admin
from  users.models import *
from django.contrib.auth.admin import UserAdmin
from users.forms import CustomUserCreationForm, CustomUserChangeForm

# Register your models here.



class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'phone_number'),
        }),
    )
class AddressAdmin(admin.ModelAdmin):
    list_display = ('nickname', 'street', 'city', 'postal_code', 'country')
    search_fields = ('nickname', 'street', 'city')
    list_filter = ('country',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Address)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('user', 'card_number', 'card_expiry', 'card_cvv')
    search_fields = ('user__username', 'card_number')
    list_filter = ('card_expiry',)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
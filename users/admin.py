from django.contrib import admin
from  users.models import CustomUser, AddressList
from django.contrib.auth.admin import UserAdmin

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(AddressList)

class CustomUserAdmin(UserAdmin):

    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser


    model = CustomUser

    list_display = UserAdmin.list_display + ('phone_number', 'payment_method')


    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('phone_number', 'payment_method',)}),
    )
    # Se vuoi aggiungere il campo anche quando crei un nuovo utente dal pannello admin
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('phone_number', 'payment_method',)}),
    )

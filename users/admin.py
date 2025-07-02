from django.contrib import admin
from  users.models import CustomUser, Address
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
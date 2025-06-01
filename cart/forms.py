from django import forms
from .models import Cart, AddressList

class CartForm(forms.ModelForm):

    class Meta:
        model = Cart
        fields = ['address']  # Assuming you want to allow users to select an address for their cart

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        self.fields['address'].queryset = AddressList.objects.filter(user=user)
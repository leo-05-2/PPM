from crispy_forms.helper import FormHelper
from django import forms
from .models import Cart, AddressList

class CartForm(forms.ModelForm):

    class Meta:
        model = Cart
        fields = ['address']  # Assuming you want to allow users to select an address for their cart

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user',None)
        super().__init__(*args, **kwargs)
        if user: self.fields['address'].queryset = AddressList.objects.filter(user=user)
        elif self.instance and self.instance.pk and self.instance.user:
            self.fields['address'].queryset = AddressList.objects.filter(user=self.instance.user)
        else:
            self.fields['address'].queryset = AddressList.objects.none()


        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input( forms.Submit('submit', 'Update Cart Address'))

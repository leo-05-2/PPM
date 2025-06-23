from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django import forms
from .models import *

class PriceFilterForm(forms.Form):
    min_price = forms.IntegerField(label='Prezzo minimo', required=False)
    max_price = forms.IntegerField(label='Prezzo massimo', required=False)

    def clean(self):
        cleaned_data = super().clean()
        min_price = cleaned_data.get('min_price')
        max_price = cleaned_data.get('max_price')

        if min_price is not None and max_price is not None and min_price > max_price:
            raise forms.ValidationError("Il prezzo minimo non può essere maggiore del prezzo massimo.")

        return cleaned_data

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'available', 'category'] # Aggiungi 'image' se hai un campo immagine
        widgets = {
            'category': forms.CheckboxSelectMultiple, # Per selezionare più categorie
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('description', css_class='form-control', rows=5),
            Field('price', css_class='form-control'),
            Field('stock', css_class='form-control'),
            Field('available', css_class='form-check-input'), # Per checkbox
            Field('category', css_class='form-check-input'), # Per CheckboxSelectMultiple
            #  campo immagine:
            # Field('image', css_class='form-control'),
            Submit('submit', 'Salva Prodotto', css_class='btn btn-primary mt-3')
        )

        for field_name, field in self.fields.items():
            if field_name not in ['available', 'category']: # Crispy forms gestisce  le checkbox
                field.widget.attrs['class'] = 'form-control'
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
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,  # opzionale se vuoi permettere nessuna categoria
        label='Categoria'
    )
    price = forms.DecimalField(min_value=0, label='Prezzo')

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'available', 'category'] # Aggiungi 'image' se hai un campo immagine
        widgets = {
            'category': forms.Select(attrs={'class': 'form-select'}),  # Selezione a tendina
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('description', css_class='form-control', rows=5),
            Field('price', css_class='form-control',min = 0),
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

   # todo: in attesa di decidere più categorie possono appartenere ad un prodotto
    def save(self, commit=True):
        product = super().save(commit=False)
        if commit:
            product.save()

            category = self.cleaned_data.get('category')
            if category:
                product.category.set([category])
            else:
                product.category.clear()
        else:
            self.save_m2m = lambda: product.category.set([self.cleaned_data['category']]) if self.cleaned_data.get(
                'category') else product.category.clear()
        return product
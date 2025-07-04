from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Submit
from django import forms
from .models import *
import os
from django.core.exceptions import ValidationError
from django.conf import settings
from django.core.files.storage import default_storage

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

def get_product_images():
    images_dir = os.path.join(settings.MEDIA_ROOT, 'product_images')
    choices = [('', 'Nessuna immagine')]  # Opzione vuota per nessuna immagine
    if not os.path.exists(images_dir):
        return choices
    choices += [
        (f'product_images/{f}', f)
        for f in os.listdir(images_dir)
        if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))
    ]
    return choices

class ProductForm(forms.ModelForm):

    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'form-select select2', 'multiple': 'multiple'}),
        required=True,
        label='Categoria'
    )
    price = forms.DecimalField(min_value=0, label='Prezzo')

    image_upload = forms.ImageField(
        required=False,
        label='Oppure carica nuova immagine',
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    image_choice = forms.ChoiceField(
        choices=get_product_images,
        required=False,
        label='Scegli un immagine tra quelle esistenti',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Product
        fields = ['name', 'description', 'price', 'stock', 'available', 'category','image']
        widgets = {
            'category': forms.SelectMultiple(attrs={'class': 'form-select select2', 'multiple': 'multiple'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Field('name', css_class='form-control'),
            Field('description', css_class='form-control', rows=5),
            Field('price', css_class='form-control',min = 0),
            Field('stock', css_class='form-control'),
            Field('available', css_class='form-check-input'),
            Field('category', css_class='form-select select2', multiple='multiple'),
            Field('image', css_class='form-control'),
            Submit('submit', 'Salva Prodotto', css_class='btn btn-primary mt-3')
        )

        for field_name, field in self.fields.items():
            if field_name not in ['available', 'category']:
                field.widget.attrs['class'] = 'form-control'

   # todo: in attesa di decidere più categorie possono appartenere ad un prodotto

    def save(self, commit=True):
        product = super().save(commit=False)
        image_file = self.cleaned_data.get('image_upload')
        image_choice = self.cleaned_data.get('image_choice')

        if image_file:


            path = default_storage.save(f'product_images/{image_file.name}', image_file)
            product.image = path
        elif image_choice:
            product.image = image_choice
        else:
            product.image = None




        if commit:
            product.save()
            self.save_m2m()
            product.category.set(self.cleaned_data['category'])
        return product

class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'list': 'category-suggestions',
            'placeholder': 'Inserisci o scegli una categoria',
            'class': 'form-control',
            'autocomplete': 'off',
            'required': True,
        }),
        label='Nome Categoria'
    )

    class Meta:
        model = Category
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('name', css_class='form-control mb-3'),
            Submit('submit', 'Aggiungi Categoria', css_class='btn btn-primary')
        )
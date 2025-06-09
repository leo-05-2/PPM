from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product, Category

# Create your views here.


def home_page(request):
    # Reindirizza utenti autenticati alla home personalizzata

    # Recupera gli ultimi prodotti pubblicati
    latest_products = Product.objects.all().order_by('-created')[:8]

    # Recupera alcune categorie principali
    categories = Category.objects.all()[:6]

    context = {
        'latest_products': latest_products,
        'categories': categories,
    }

    return render(request, 'core/home_page.html', context)


def about_page(request):
    return render(request, 'core/about.html')


def contact_page(request):
    return render(request, 'core/contact.html')


def privacy_policy_page(request):
    return render(request, 'core/privacy_policy.html')


def terms_of_service_page(request):
    return render(request, 'core/terms_of_service.html')
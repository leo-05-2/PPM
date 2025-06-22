from django.shortcuts import render

from cart.models import Cart
from products.models import Product, Category


# Create your views here.

def product_info(request, product_id):
    # Recupera il prodotto in base all'ID
    product = Product.objects.get(id=product_id)

    # Recupera le categorie associate al prodotto
    categories = product.category.all()

    name = product.name

    description = product.description

    price = product.price

    stock = product.stock

    related_products = Product.objects.filter(category__in=categories).exclude(id=product_id)[:4]

    source = request.GET.get('source')

    user = request.user if request.user.is_authenticated else None
    if user:
        cart, created = Cart.objects.get_or_create(user=user)
    else:
        cart = None

    context = {
        'product': product,
        'categories': categories,
        'name': name,
        'description': description,
        'price': price,
        'stock': stock,
        'related_products': related_products,
        'source': source,
        'cart': cart,

    }

    return render(request, 'products/product_info.html', context)



from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import CartForm
from django.contrib.auth.decorators import login_required

# Create your views here.

@login_required
def update_cart_address(request):
    cart ,created = Cart.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CartForm(request.POST, instance=cart, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('cart:cart_detail')  #todo: implement
    else:
        form = CartForm(instance=cart, user=request.user)

    return render(request, 'cart/update_cart_address.html', {'form': form, 'cart': cart})

def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)


    context = {
        'cart': cart,
        'items': cart.items.all(),
    }
    return render(request, 'cart/view_cart.html', context)

@login_required
def add_cart_item(request):

    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = get_object_or_404( Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})

        if not created:
            cart_item.quantity += quantity
        cart_item.save()

        # Restituisci risposta in base al flag di redirect
        return HttpResponse("prodotto aggiunto al carrello")

        return redirect('cart:view_cart')


@login_required
def update_item(request, item_id):

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        if 'increase' in request.POST:
            # Incrementa la quantità
            cart_item.quantity += 1
        elif 'decrease' in request.POST:
            # Decrementa la quantità, assicurandosi che non sia inferiore a 1
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
        elif 'quantity' in request.POST:
            # Imposta direttamente la quantità dal campo input
            try:
                quantity = int(request.POST.get('quantity'))
                if quantity > 0:
                    cart_item.quantity = quantity
            except ValueError:
                pass

        cart_item.save()

    return redirect('cart:view_cart')


@login_required
def remove_item(request, item_id):


    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        cart_item.delete()

    return redirect('cart:view_cart')



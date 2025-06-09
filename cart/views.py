from django.shortcuts import render, redirect
from .models import Cart
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

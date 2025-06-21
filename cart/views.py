from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import CartForm , CheckoutForm , ShippingForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from decimal import Decimal
from django.views.generic import DetailView , ListView
from django.contrib.auth.mixins import LoginRequiredMixin

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

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.all()

    old_shipping_method = request.session.get('shipping_method', 'standard')

    shipping_method_changed = False

    # Crea o recupera il form di spedizione
    if request.method == 'POST':
        shipping_form = ShippingForm(request.POST)
        if shipping_form.is_valid():
            new_shipping_method = shipping_form.cleaned_data['shipping_method']
            if old_shipping_method != new_shipping_method:
                shipping_method_changed = True
            request.session['shipping_method'] = new_shipping_method
    else:
        shipping_form = ShippingForm(initial={'shipping_method': old_shipping_method})

    shipping_method = request.session.get('shipping_method', 'standard')
    subtotal = cart.total_price()
    shipping_cost = Decimal('4.99')


    if shipping_method == 'standard':
        shipping_cost = Decimal('4.99')
    elif shipping_method == 'express':
        shipping_cost = Decimal('9.99')

    if subtotal >= 50:
        shipping_cost = Decimal('0.00')

    total = subtotal + shipping_cost


    delivery_date_str = request.session.get('delivery_date')
    if delivery_date_str is None or shipping_method_changed:
        today = datetime.now().date()
        if shipping_method == 'express':
            delivery_date = today + timedelta(days=2)
        else:
            delivery_date = today + timedelta(days=5)


        formatted_delivery_date = delivery_date.strftime('%d/%m/%Y')
        request.session['delivery_date'] = formatted_delivery_date
    else:
        formatted_delivery_date = delivery_date_str

    context = {
        'cart': cart,
        'items': items,
        'shipping_form': shipping_form,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'total': total,
        'delivery_date': formatted_delivery_date
    }
    request.session['checkout_data'] = {
        'subtotal': str(subtotal),
        'shipping_cost': str(shipping_cost),
        'total': str(total),
        'delivery_date': formatted_delivery_date,
        'shipping_method': shipping_method,
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
            if cart_item.quantity == 1:
                cart_item.delete()
        elif 'quantity' in request.POST:

            try:
                quantity = int(request.POST.get('quantity'))
                if quantity > 0:
                    cart_item.quantity = quantity
                    cart_item.save()
                else:
                    cart_item.delete()
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

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)


    checkout_data = request.session.get('checkout_data', {})
    subtotal = Decimal(checkout_data.get('subtotal', '0.00'))
    shipping_cost_view = Decimal(checkout_data.get('shipping_cost'))
    total = Decimal(checkout_data.get('total'))
    delivery_date = datetime.strptime(checkout_data.get('delivery_date'), '%d/%m/%Y').date()
    shipping_method = checkout_data.get('shipping_method', 'standard')

    user_addresses = request.user.addresses.all().order_by('nickname')

    if request.method == 'POST':
        form = CheckoutForm(request.POST, user=request.user)
        if form.is_valid():

            if form.cleaned_data['use_existing_address']:
                address = form.cleaned_data['address']
            else:
                # Crea nuovo indirizzo
                address = Address(
                    user=request.user,
                    street=form.cleaned_data['street'],
                    city=form.cleaned_data['city'],
                    postal_code=form.cleaned_data['postal_code'],
                    nickname=form.cleaned_data.get('nickname'),
                    country=form.cleaned_data.get('country', 'Italia')
                )
                address.save()


            order = Order.objects.create(
                user=request.user,
                address=address,
                city = address.city,
                delivery_date = delivery_date,
                delivered = False,
                shipped = False,
                shipping_cost = shipping_cost_view,
                shipping_method = shipping_method
            )


            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )

            prodotti_insufficienti = []

            for cart_item in cart.items.all():
                product = cart_item.product
                if product.stock < cart_item.quantity:
                    prodotti_insufficienti.append({
                        'nome': product.name,
                        'disponibili': product.stock,
                        'richiesti': cart_item.quantity
                    })

            # Se ci sono prodotti con stock insufficiente, mostra errori
            if prodotti_insufficienti:
                for prod in prodotti_insufficienti:
                    messages.error(
                        request,
                        f"Quantità insufficiente per {prod['nome']}. Disponibili: {prod['disponibili']}, Richiesti: {prod['richiesti']}"
                    )
                return redirect('cart:view_cart')

            # Altrimenti, procedi con l'aggiornamento dello stock
            for cart_item in cart.items.all():
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()


            cart.items.all().delete()

            if 'shipping_method' in request.session:
                del request.session['shipping_method']

            if 'checkout_data' in request.session:
                del request.session['checkout_data']

            return redirect('cart:checkout_success')


    else:

        initial_data = {}
        if user_addresses.exists():
            initial_data['use_existing_address'] = True
            initial_data['address'] = user_addresses.first().id

        form = CheckoutForm(user=request.user, initial=initial_data)

    context = {
        'cart': cart,
        'form': form,
        'user_addresses': user_addresses,
        'subtotal': subtotal,
        'shipping_cost': shipping_cost_view,
        'total': total,
        'shipping_method': shipping_method,
        'delivery_date': delivery_date.strftime('%d/%m/%Y')
    }

    return render(request, 'cart/checkout_cart.html', context)


@login_required
def update_shipping(request, method):
    # Verifica che il metodo sia valido
    if method not in ['standard', 'express']:
        method = 'standard'

    # Salva il metodo nella sessione
    request.session['shipping_method'] = method

    # Reindirizza alla pagina del carrello
    return redirect('cart:view_cart')

def checkout_success(request):

    return render(request, 'cart/checkout_success.html')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'cart/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'  # Parametro URL per l'ID dell'ordine

    def get_queryset(self):

        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['items'] = self.object.items.all()
        context['shipping_cost'] = self.object.shipping_cost
        context['subtotal'] = self.object.get_total_cost()
        context['delivery_date'] = self.object.delivery_date
        context['shipping_method'] = self.object.shipping_method
        context['address'] = self.object.address  #todo: consider using a foreing key
        context['total'] = context['subtotal'] + context['shipping_cost']



        return context


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'cart/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10  # 10 ordini per pagina

    def get_queryset(self):

        return Order.objects.filter(user=self.request.user).order_by('-created_at')

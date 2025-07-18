
from django.shortcuts import render, redirect, get_object_or_404, reverse
from .models import *
from .forms import CheckoutForm , ShippingForm , CartItemQuantityForm
from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from decimal import Decimal
from django.views.generic import DetailView , ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from users.views import is_store_manager
from django.contrib.auth.decorators import permission_required
from users.models import PaymentMethod, Address

# Create your views here.


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
    if (delivery_date_str is None or shipping_method_changed) or (subtotal >= 50):
        today = datetime.now().date()
        if shipping_method == 'express' or subtotal >= 50:
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


    return render(request, 'core/view_cart.html', context)

@login_required
def add_cart_item(request):

    if request.method == 'POST':
        cart, created = Cart.objects.get_or_create(user=request.user)
        product_id = request.POST.get('product_id')
        quantity = int(request.POST.get('quantity'))

        product = get_object_or_404( Product, id=product_id)

        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product, defaults={'quantity': quantity})
        source = request.POST.get('source', None)

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        messages.success(request, f"{product.name} è stato aggiunto al carrello.")

        redirect_url = f'/products/product/{product_id}/'
        if source:
            redirect_url += f'?source={source}'

        return redirect(redirect_url)





@login_required
def update_item(request, item_id): # Aggiorna la quantità di un elemento nel carrello

    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        if 'increase' in request.POST:
            # Incrementa la quantità
            if cart_item.quantity < cart_item.product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                messages.error(request, f"Quantità massima disponibile per {cart_item.product.name}: {cart_item.product.stock}")

        elif 'decrease' in request.POST:
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
            else:
                cart_item.delete()


        elif 'quantity' in request.POST:
            # Utilizzo del form per validare il valore di quantità inserito direttamente
            form = CartItemQuantityForm(
                request.POST,
                max_quantity=cart_item.product.stock
            )

            if form.is_valid():
                new_quantity = form.cleaned_data['quantity']

                if new_quantity == 0:
                    cart_item.delete()
                    messages.info(request, f"{cart_item.product.name} rimosso dal carrello.")
                else:
                    cart_item.quantity = new_quantity
                    cart_item.save()
                    messages.success(request, f"Quantità aggiornata a {new_quantity}.")
            else:
                # Gestione degli errori di validazione
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, error)



    return redirect('core:view_cart')


@login_required
def remove_item(request, item_id):


    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        cart_item.delete()

    return redirect('core:view_cart')

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
    saved_payments = PaymentMethod.objects.filter(user=request.user)


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

            if form.cleaned_data['use_existing_payment']:
                payment = form.cleaned_data['payment_method']
            else:
                # Crea nuovo metodo di pagamento
                payment = PaymentMethod.objects.create(
                    user=request.user,
                    card_number=form.cleaned_data['card_number'],
                    card_expiry=form.cleaned_data['card_expiry'],
                    card_cvv=form.cleaned_data['card_cvv'],
                )
                if not payment.card_number or not payment.card_expiry or not payment.card_cvv:
                    request.user.payment_method = payment
                    request.user.save()

            delivery_address = DeliveryAddress(
                street=address.street,
                city=address.city,
                postal_code=address.postal_code,
                country=address.country,
                # nickname=address.nickname if address.nickname else 'Indirizzo di spedizione',
                created_at= datetime.now()
            )
            delivery_address.save()


            order = Order.objects.create(
                user=request.user,
                address=delivery_address,

                delivery_date = delivery_date,
                status = 'pending',
                shipping_cost = shipping_cost_view,
                shipping_method = shipping_method,
                payment_method = payment.card_number

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
                return redirect('core:view_cart')


            for cart_item in cart.items.all():
                product = cart_item.product
                product.stock -= cart_item.quantity
                if product.stock == 0:
                    product.available = False
                product.save()


            cart.items.all().delete()

            if 'shipping_method' in request.session:
                del request.session['shipping_method']

            if 'checkout_data' in request.session:
                del request.session['checkout_data']

            return redirect('core:checkout_success')


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
        'delivery_date': delivery_date.strftime('%d/%m/%Y'),
        'saved_payments': saved_payments,

    }

    return render(request, 'core/checkout_cart.html', context)


@login_required
def update_shipping(request, method):


    if method not in ['standard', 'express']:
        method = 'standard'


    request.session['shipping_method'] = method

    if 'delivery_date' in request.session:
        del request.session['delivery_date']


    return redirect('core:view_cart')

def checkout_success(request):

    return render(request, 'core/checkout_success.html')


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'core/order_detail.html'
    context_object_name = 'order'
    pk_url_kwarg = 'order_id'  # Parametro URL per l'ID dell'ordine

    def get_queryset(self):
        if self.request.user.has_perm('core.change_order'):
            return Order.objects.all()
        return Order.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['items'] = self.object.items.all()
        context['shipping_cost'] = self.object.shipping_cost
        context['subtotal'] = self.object.get_total_cost()
        context['delivery_date'] = self.object.delivery_date
        context['shipping_method'] = self.object.shipping_method
        context['address'] = self.object.address
        context['total'] = context['subtotal'] + context['shipping_cost']
        context['store_manager'] = is_store_manager(self.request.user)
        context['payment_method'] = self.object.payment_method




        return context


class OrderHistoryView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'core/order_history.html'
    context_object_name = 'orders'
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user

        if user.has_perm('core.view_all_orders'):
            return Order.objects.all().order_by('-created_at')

        return Order.objects.filter(user=self.request.user).order_by('-created_at')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['store_manager'] = is_store_manager(self.request.user)
        return context


@permission_required('core.change_order', raise_exception=True)
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        new_status = request.POST.get("status")
        if new_status in ["pending", "shipped", "delivered", "cancelled"]:
            order.status = new_status
            order.save()
            messages.success(request, "Stato ordine aggiornato con successo.")
        else:
            messages.error(request, "Stato non valido.")
    redirect_url = reverse("users:store_manager_dashboard") + "?tab=shipping"
    return redirect(redirect_url)
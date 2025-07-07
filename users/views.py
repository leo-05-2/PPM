from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash, authenticate, login , password_validation
from django.contrib import messages

from review.models import Review
from products.models import Product, Category
from django.urls import reverse
from .forms import *
from django.views.generic import TemplateView
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import password_validators_help_texts
from django.views.decorators.http import require_POST
from django.contrib.auth.models import Group




from core.models import Order , OrderItem


# Create your views here.

@login_required
def user_home_page(request):
    user = request.user
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    categories = Category.objects.all()

    latest_products = Product.objects.all().order_by('-created')[:8]
    already_bought_products_list = recent_orders.first()
    already_bought_products =  OrderItem.objects.filter(order=already_bought_products_list)
    already_bought_products_category = Category.objects.filter(product__in=already_bought_products.values_list('product', flat=True))
    if already_bought_products_category.exists() and already_bought_products.exists():
        suggested_products = Product.objects.filter(category__in=already_bought_products_category).exclude(id__in=already_bought_products)[:4]
    else:
        suggested_products = Product.objects.all().order_by('-created')[:4]


    context = {
        'user': user,
        'recent_orders': recent_orders,
        'latest_products': latest_products,
        'categories': categories,
        'suggested_products': suggested_products

    }
    return render(request, 'users/user_home_page.html', context)

class StoreManagerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'users/store_manager_dashboard.html'


    def test_func(self):
        return is_store_manager(self.request.user)

    def get_context_data(self, **kwargs):
        user = self.request.user
        your_products = Product.objects.filter(added_by=user)
        your_products_reviews = Review.objects.filter(product__in=your_products)
        context = super().get_context_data(**kwargs)
        context['total_products'] = Product.objects.count()
        context['total_orders'] = Order.objects.count()
        context['pending_orders'] = Order.objects.filter(status = 'pending').count()
        context['latest_products'] = Product.objects.order_by('-created')[:5]
        context['all_orders'] = Order.objects.all().order_by('-created_at')[:5]
        context['shipped_not_delivered'] = Order.objects.filter(status = 'shipped')
        context['pending_orders_list'] = Order.objects.filter(status = 'pending').order_by('-created_at')[:5]
        context['shipped'] = Order.objects.filter(status='shipped').order_by('-created_at')[:5]
        context['all_products'] = Product.objects.all().order_by('-created')[:5]
        context['all_reviews'] = Review.objects.order_by('-created_at')[:5]
        context['your_products'] =  your_products
        context['your_products_reviews'] = your_products_reviews
        return context


def is_store_manager(user):
    return user.groups.filter(name='Store Managers').exists()


class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = LoginForm

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            if is_store_manager(user):
                return redirect('users:store_manager_dashboard')
            else:
                messages.success(self.request, f"Benvenuto, {user.username}!")
                return redirect('users:user_home_page')
        else:
            messages.error(self.request, "Credenziali non valide. Riprova.")
            return self.form_invalid(form)


class UserSignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/sign_up.html'
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        response = super().form_valid(form)
        customer_group, _ = Group.objects.get_or_create(name='Customers')
        self.object.groups.add(customer_group)
        return response

class UserLogoutView(LogoutView):
    template_name = 'users/logout_custom.html'
    next_page = reverse_lazy('core:home')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):


        response = super().get(request, *args, **kwargs)





        return response


class UserAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'users/account.html'
    permmission_required = 'users.view_user'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        context['addresses'] = Address.objects.filter(user=self.request.user)
        context['help_texts'] = password_validators_help_texts()
        context['user_reviews'] = Review.objects.filter(user=self.request.user).order_by('-created_at')
        context['favorite_products'] = self.request.user.favorite_list.all()
        context['form'] = UserProfileForm(instance=self.request.user)
        context['payment_form'] = PaymentMethodForm()
        context['address_form'] = AddressForm()



        return context


@login_required
def update_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            payment_method = form.cleaned_data.get('payment_method')
            if payment_method:
                PaymentMethod.objects.filter(user=user).update(is_default=False)
                payment_method.is_default = True
                payment_method.save()
            messages.success(request, 'Profilo aggiornato con successo!')
            return redirect('users:account')
        else:
            context = {
                'user': user,
                'orders': Order.objects.filter(user=user).order_by('-created_at'),
                'addresses': Address.objects.filter(user=user),
                'help_texts': password_validators_help_texts(),
                'user_reviews': Review.objects.filter(user=user).order_by('-created_at'),
                'favorite_products': user.favorite_list.all(),
                'form': form,
            }
            return render(request, 'users/account.html', context)

    return redirect('users:account')

@login_required
@require_POST
@permission_required('users.add_paymentmethod', raise_exception=True)
def add_payment_method(request):
    form = PaymentMethodForm(request.POST)
    if form.is_valid():
        payment = form.save(commit=False)
        payment.user = request.user
        payment.save()
        messages.success(request, "Carta aggiunta con successo.")
        return redirect('users:account')
    else:

        context = {
            'user': request.user,
            'orders': Order.objects.filter(user=request.user).order_by('-created_at'),
            'addresses': Address.objects.filter(user=request.user),
            'help_texts': password_validators_help_texts(),
            'user_reviews': Review.objects.filter(user=request.user).order_by('-created_at'),
            'favorite_products': request.user.favorite_list.all(),
            'form': UserProfileForm(instance=request.user),
            'address_form': AddressForm(),
            'payment_form': form,
            'open_payment_modal': True,
        }
        return render(request, 'users/account.html', context)

@login_required
@require_POST
@permission_required('users.delete_paymentmethod', raise_exception=True)
def delete_payment_method(request, card_id):
    card = get_object_or_404(PaymentMethod, id=card_id, user=request.user)
    card.delete()
    messages.success(request, "Carta eliminata.")
    return redirect('users:account')


@login_required
@permission_required('users.change_paymentmethod', raise_exception=True)
def change_password(request):
    if request.method == 'POST':
        user = request.user
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if  user.check_password(new_password):
            messages.error(request, 'La nuova password non può essere uguale alla password attuale')
        elif new_password != confirm_password:
            messages.error(request, 'Le nuove password non coincidono')
        else:
            try:
                password_validation.validate_password(new_password, user)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return redirect('users:account')

            user.set_password(new_password)
            user.save()
            messages.success(request, 'Password aggiornata con successo!')
            update_session_auth_hash(request, user)  # Mantiene la sessione attiva

    return redirect('users:account')


@login_required
@permission_required('users.add_address', raise_exception=True)
def add_address(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            return redirect('users:account')
        else:
            # Passa il form con errori e il flag per riaprire la modale
            context = {
                'user': request.user,
                'orders': Order.objects.filter(user=request.user).order_by('-created_at'),
                'addresses': Address.objects.filter(user=request.user),
                'help_texts': password_validators_help_texts(),
                'user_reviews': Review.objects.filter(user=request.user).order_by('-created_at'),
                'favorite_products': request.user.favorite_list.all(),
                'form': UserProfileForm(instance=request.user),
                'address_form': form,
                'payment_form': PaymentMethodForm(),
                'open_add_address_modal': True,
            }
            messages.error(request, 'Errore nella creazione dell\'indirizzo. Assicurati di compilare tutti i campi richiesti.')
            return render(request, 'users/account.html', context)
    return redirect('users:account')


@login_required
@permission_required('users.delete_address', raise_exception=True)
def delete_address(request, address_id):
    if request.method == 'POST':
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        messages.success(request, 'Indirizzo eliminato con successo!')
    return redirect(reverse('users:account'))

@login_required
@permission_required('users.change_address', raise_exception=True)
def update_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    if request.method == 'POST':
        # Recupera i valori dei campi
        street = request.POST.get('street', '').strip()
        city = request.POST.get('city', '').strip()

        postal_code = request.POST.get('postal_code', '').strip()
        country = request.POST.get('country', '').strip()
        nickname = request.POST.get('nickname', '').strip()

        # Verifica che tutti i campi siano compilati
        if not (street and city  and postal_code and country and nickname):
            messages.error(request, 'Tutti i campi sono obbligatori per aggiornare l\'indirizzo.')
        else:
            # Aggiorna l'indirizzo
            address.street = street
            address.city = city

            address.postal_code = postal_code
            address.country = country
            address.nickname = nickname
            address.save()
            messages.success(request, 'Indirizzo aggiornato con successo!')

    return redirect(reverse('users:account'))

@login_required
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    user = request.user
    base_url = reverse('products:product_info', args=[product.id])
    if product in user.favorite_list.all():
        user.favorite_list.remove(product)
        return redirect(f"{base_url}?fav=removed")
    else:
        user.favorite_list.add(product)
        return redirect(f"{base_url}?fav=added")

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

    return render(request, 'users/home_page.html', context)

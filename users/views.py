from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.template.context_processors import request
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash, authenticate, login , password_validation
from django.contrib import messages

from review.models import Review
from .models import *
from products.models import Product, Category
from django.urls import reverse
from core.models import Order
from .forms import *
from django.views.generic import TemplateView, View # Importa View
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import password_validators_help_texts




from core.models import Order


# Create your views here.

@login_required
def user_home_page(request):
    user = request.user
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    categories = Category.objects.all()

    latest_products = Product.objects.all().order_by('-created')[:8]
    context = {
        'user': user,
        'recent_orders': recent_orders,
        'latest_products': latest_products,
        'categories': categories,

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
        context['all_products'] = Product.objects.all().order_by('-created')
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
                messages.success(self.request, f"Benvenuto Store Manager, {user.username}!")
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

class UserLogoutView(LogoutView):
    template_name = 'users/logout_custom.html'
    next_page = reverse_lazy('core:home')
    http_method_names = ['get', 'post']

    def get(self, request, *args, **kwargs):


        response = super().get(request, *args, **kwargs)


        messages.success(request, "Sei stato disconnesso con successo!")


        return response


class UserAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'users/account.html'  # Specifica il template per la pagina dell'account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        context['addresses'] = Address.objects.filter(user=self.request.user)
        context['help_texts'] = password_validators_help_texts()
        context['user_reviews'] = Review.objects.filter(user=self.request.user).order_by('-created_at')

        return context


@login_required
def update_profile(request):
    if request.method == 'POST':
        user = request.user
        user.email = request.POST.get('email')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.phone_number = request.POST.get('phone_number')
        user.payment_method = request.POST.get('payment_method')
        user.save()
        messages.success(request, 'Profilo aggiornato con successo!')
    return redirect('users:account')


@login_required
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
def add_address(request):
    if request.method == 'POST':
        Address.objects.create(
            user=request.user,
            street=request.POST.get('street'),
            city=request.POST.get('city'),
            province=request.POST.get('province'),
            postal_code=request.POST.get('postal_code'),
            country=request.POST.get('country'),

            nickname=request.POST.get('nickname'),

        )
        messages.success(request, 'Indirizzo aggiunto con successo!')
    return redirect('users:account')


@login_required
def delete_address(request, address_id):
    if request.method == 'POST':
        address = get_object_or_404(Address, id=address_id, user=request.user)
        address.delete()
        messages.success(request, 'Indirizzo eliminato con successo!')
    return redirect(reverse('users:account'))

@login_required
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

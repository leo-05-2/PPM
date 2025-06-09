from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.template.context_processors import request
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import CustomUser, Address



from cart.models import Order
from .forms import CustomUserCreationForm

# Create your views here.

@login_required
def user_home_page(request):
    user = request.user
    recent_orders = Order.objects.filter(user=user).order_by('-created_at')[:5]
    context = {
        'user': user,
        'recent_orders': recent_orders,
    }
    return render(request, 'users/user_home_page.html', context)

class UserLoginView(LoginView):
    template_name = 'users/login.html' # Specifica il template per il login
    # redirect_authenticated_user = True # Opzionale: se un utente loggato visita la pagina di login, reindirizzalo
    def get_success_url(self):
        return reverse_lazy('users:user_home_page') # Reindirizza alla dashboard dopo il login

class UserSignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'users/sign_up.html' # Specifica il template per la registrazione
    success_url = reverse_lazy('users:login') # Reindirizza alla pagina di login dopo la registrazione

class UserLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')

class UserAccountView(LoginRequiredMixin, TemplateView):
    template_name = 'users/account.html'  # Specifica il template per la pagina dell'account

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['orders'] = Order.objects.filter(user=self.request.user).order_by('-created_at')
        context['addresses'] = Address.objects.filter(user=self.request.user)
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
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if not user.check_password(current_password):
            messages.error(request, 'La password attuale non è corretta')
        elif new_password != confirm_password:
            messages.error(request, 'Le nuove password non coincidono')
        else:
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

            nickname=request.POST.get('nickname'),

        )
        messages.success(request, 'Indirizzo aggiunto con successo!')
    return redirect('users:account')


@login_required
def delete_address(request, address_id):
    address = get_object_or_404(Address, id=address_id, user=request.user)
    address.delete()
    messages.success(request, 'Indirizzo eliminato con successo!')
    return redirect('core:home')

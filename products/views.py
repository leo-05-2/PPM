from django.contrib.auth.decorators import permission_required
from django.shortcuts import render, get_object_or_404

from core.models import Cart
from products.models import Product, Category
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.views.generic import CreateView, UpdateView, DeleteView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Avg
from review.models import Review
from .models import *
from django.shortcuts import redirect



# Create your views here.

def product_info(request, product_id):
    # Recupera il prodotto in base all'ID
    product = Product.objects.get(id=product_id)


    categories = product.category.all()

    name = product.name

    description = product.description

    price = product.price

    stock = product.stock

    related_products = Product.objects.filter(category__in=categories).exclude(id=product_id)[:8]

    source = request.GET.get('source')

    review = Review.objects.filter(product=product).order_by('-created_at')

    if review.exists():
        average_rating = review.aggregate(Avg('rating'))['rating__avg']
    else:
        average_rating = None


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
        'store_manager': is_store_manager(user) if user else False,
        'average_rating': average_rating,
        'reviews': review,
        'available': product.available,

    }

    return render(request, 'products/product_info.html', context)

def product_list_category(request, category_id = None):
    # Recupera la categoria in base all'ID




    # Recupera i prodotti associati alla categoria
    if category_id:
        products = Product.objects.filter(category=category_id)
    else:
        products = Product.objects.all()

    category = Category.objects.all()

    source = request.GET.get('source')

    min_price = None
    max_price = None



    selected_category = None

    category_param = request.GET.get('category')
    if category_param:
        try:
            selected_category = Category.objects.get(id=category_param)
            products = products.filter(category=selected_category)
        except Category.DoesNotExist:
            selected_category = None
    elif category_id:
        selected_category = get_object_or_404(Category, id=category_id)
        products = products.filter(category=selected_category)
    query = request.GET.get('q', '')

    if query:
        products = products.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )




    form = PriceFilterForm(request.GET or None)
    if form.is_valid():
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')

        if min_price is not None:
            products = products.filter(price__gte=min_price)
        if max_price is not None:
            products = products.filter(price__lte=max_price)

    context = {
        'category': category,
        'products': products,
        'source': source,
        'min_price': min_price,
        'max_price': max_price,
        'category_id': category_id,
        'selected_category': selected_category,
        'query': query,

    }

    return render(request, 'products/product_list_category.html', context)

def is_store_manager(user):
    return user.groups.filter(name='Store Managers').exists()


class ProductCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView, PermissionRequiredMixin):
    permission_required = 'products.add_product'
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    success_url = reverse_lazy('users:store_manager_dashboard')

    def test_func(self):
        return is_store_manager(self.request.user)

    def form_valid(self, form):
        form.instance.added_by = self.request.user
        messages.success(self.request, "Prodotto aggiunto con successo!")
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView, PermissionRequiredMixin):
    permission_required = 'products.change_product'
    model = Product
    form_class = ProductForm
    template_name = 'products/product_form.html'
    pk_url_kwarg = 'product_id'  # Assumi che l'URL usi product_id
    success_url = reverse_lazy('users:store_manager_dashboard')

    def test_func(self):
        return is_store_manager(self.request.user)

    def form_valid(self, form):

        form.instance.modified_by = self.request.user
        messages.success(self.request, "Prodotto aggiornato con successo!")
        return super().form_valid(form)


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView, PermissionRequiredMixin):
    permission_required = 'products.delete_product'
    model = Product
    template_name = 'products/product_confirm_delete.html'  # Crea un template per la conferma eliminazione
    pk_url_kwarg = 'product_id'
    success_url = reverse_lazy('users:store_manager_dashboard')

    def test_func(self):
        return is_store_manager(self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Prodotto eliminato con successo!")
        return super().form_valid(form)


# View per la lista completa dei prodotti gestibili dallo Store Manager
class ProductManageListView(LoginRequiredMixin, UserPassesTestMixin, ListView, PermissionRequiredMixin):
    permission_required = 'products.change_product'
    model = Product
    template_name = 'products/product_manage_list.html'
    context_object_name = 'products'
    paginate_by = 10  # Paginazione per grandi quantità di prodotti

    def test_func(self):
        return is_store_manager(self.request.user)

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query)
            )
        return queryset.order_by('name')  # Ordina i prodotti per nome

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
    #todo: add a template to use q
def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.all()

    # Gestione del filtro per prezzo


    context = {
        'products': products,
        'categories': categories,

    }

    return render(request, 'products/product_list.html', context)

def category_create(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('products:category_create')
    else:
        form = CategoryForm()

    return render(request, 'products/category_form.html', {
        'form': form,
        'categories': categories,
        'CATEGORY_CHOICES': CATEGORY_CHOICES
    })

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.contrib import messages
from .models import *
from django.db.models import Avg

from products.models import Product
from core.models import *


# Create your views here.

@login_required
def write_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    purchase_verified = False
    if request.user.is_authenticated:
        #  if the user has purchased the product
        purchases_list = Order.objects.filter(user=request.user)
        purchases = OrderItem.objects.filter(product=product, order__in=purchases_list)
        delivered_purchases = purchases.filter(order__status='delivered')
        if purchases.exists() and delivered_purchases.exists():
            purchase_verified = True

    if not purchase_verified:
        messages.error(request, 'Puoi scrivere una recensione solo se hai acquistato e ricevuto questo prodotto.')
        return redirect('products:product_info', product_id=product.id)



    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            messages.success(request, 'Your review has been submitted successfully.')
            return redirect('products:product_info', product_id=product.id)
    else:
        form = ReviewForm()

    context = {
        'form': form,
        'product': product,
        'purchase_verified': purchase_verified,
    }
    return render(request, 'reviews/write_review.html', context)

@login_required
def delete_review(request, review_id):

    review = get_object_or_404(Review, id = review_id)
    product = review.product


    if request.method == 'POST':
        # Check if the user is the owner of the review

        if review.user != request.user and not request.user.has_perm('review.delete_review'):
            messages.error(request, 'You are not authorized to delete this review.')
            return redirect('products:product_info', product_id=product.id)
        # If the user is authorized, delete the review

        elif request.user.has_perm('review.delete_review'):
            review.delete()
            return redirect('users:store_manager_dashboard')
        else:
            review.delete()
            return redirect('users:account', product_id=product.id)

    context = {
        'product': product,
        'review': review,
    }
    return render(request, 'reviews/delete_review.html', context)
@login_required
def see_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] if reviews.exists() else None

    context = {
        'product': product,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'reviews/see_reviews.html', context)

@permission_required('review.view_all_review', raise_exception=True)
def see_all_reviews(request):

    reviews = Review.objects.all().order_by('-created_at')
    products = Product.objects.all().order_by('-created')
    context = {
        'reviews': reviews,
        'products': products,

    }
    return render(request, 'reviews/see_all_reviews.html', context)
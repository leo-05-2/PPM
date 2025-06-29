from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.contrib import messages
from .models import *
from django.db.models import Avg

from products.models import Product
from cart.models import *


# Create your views here.

@login_required
def write_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    purchease_verified = False
    if request.user.is_authenticated:
        #  if the user has purchased the product
        purchases_list = Order.objects.filter(user=request.user)
        purchases = OrderItem.objects.filter(product=product, order__in=purchases_list)
        delivered_purchases = purchases.filter(order__status='delivered')
        if purchases.exists() and delivered_purchases.exists():
            purchease_verified = True



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
        'purchease_verified': purchease_verified,
    }
    return render(request, 'reviews/write_review.html', context)

@login_required
def delete_review(request, review_id):

    review = get_object_or_404(Review, id = review_id, user=request.user)
    product = review.product

    if request.method == 'POST':
        # Check if the user is the owner of the review
        if review.user != request.user:
            messages.error(request, 'You are not authorized to delete this review.')
            return redirect('products:product_info', product_id=product.id)
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

@permission_required('reviews.view_all_review', raise_exception=True)
def see_all_reviews(request):

    reviews = Review.objects.all().order_by('-created_at')
    products = Product.objects.all().order_by('-created_at')
    #todo: se raggruppare per prodotto e chi lo ha aggiunto al sito e un insieme generale, e aggiungere il permesso da assegnadolo da admin agli store manager

    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/see_all_reviews.html', context)
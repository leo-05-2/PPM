from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render, get_object_or_404, redirect
from .forms import *
from django.contrib import messages

from products.models import Product


# Create your views here.

@login_required
def write_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

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
    }
    return render(request, 'reviews/write_review.html', context)

@login_required
def delete_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    review = get_object_or_404(Review, product=product, user=request.user)

    if request.method == 'POST':
        # Check if the user is the owner of the review
        if review.user != request.user:
            messages.error(request, 'You are not authorized to delete this review.')
            return redirect('products:product_info', product_id=product.id)
        review.delete()
        messages.success(request, 'Your review has been deleted successfully.')
        return redirect('products:product_info', product_id=product.id)

    context = {
        'product': product,
        'review': review,
    }
    return render(request, 'reviews/delete_review.html', context)
@login_required
def see_reviews(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = product.reviews.all().order_by('-created_at')

    context = {
        'product': product,
        'reviews': reviews,
    }
    return render(request, 'reviews/see_reviews.html', context)

@permission_required('reviews.view_all_review', raise_exception=True)
def see_all_reviews(request):

    reviews = Review.objects.all().order_by('-created_at')
    products = Product.objects.all().order_by('-created_at')
    #todo: se raggruppare per prodotto e chi lo ha aggiunto al sito e un insieme generale

    context = {
        'reviews': reviews,
    }
    return render(request, 'reviews/see_all_reviews.html', context)
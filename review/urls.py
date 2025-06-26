
from django.urls import path
from .views import write_review, delete_review, see_all_reviews, see_reviews
app_name = 'review'

urlpatterns = [
    path('write/<int:product_id>/', write_review, name='write_review'),
    path('delete/<int:product_id>/', delete_review, name='delete_review'),
    path('see_all_reviews/', see_all_reviews, name='see_all_reviews'),
    path('see_reviews/<int:product_id>/', see_reviews, name='see_reviews'),
]



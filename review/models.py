from django.db import models


# Create your models here.

class Review(models.Model):
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(default=1)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:

        permissions = (
            ('view_all_review', 'Can view all reviews'),
        )

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name} - Rating: {self.rating}"

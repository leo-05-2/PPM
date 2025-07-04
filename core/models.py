from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from users.models import Address

# Create your models here.


CustomUser = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='core')
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='carts')



    def __str__(self):
        return f"Cart of {self.user.username}"

    def total_price(self):
        return sum(item.get_total_price() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ('cart', 'product') # Ensures a product is only once in a core

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s core"

    def get_total_price(self):
        return self.quantity * self.product.price

class DeliveryAddress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Italia')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.street}, {self.city}"



class Order(models.Model):

    STATUS_CHOICES = [
        ('pending', 'In attesa'),
        ('shipped', 'Spedito'),
        ('delivered', 'Consegnato'),
        ('cancelled', 'Annullato'),
    ]


    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders') # if an address is deleted, orders will still reference to a valid address
    delivery_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_method = models.CharField(max_length=50, default='standard')
    payment_method = models.CharField(max_length=16)



    class Meta:
        ordering = ('-created_at',)
        permissions = [
            ("view_all_orders", "Può vedere tutti gli ordini"),
        ]

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2) # Price at the time of order
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order {self.order.id}"

    def get_cost(self):
        return self.price * self.quantity


from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
from users.models import Address

# Create your models here.


CustomUser = get_user_model()

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='cart')
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
        unique_together = ('cart', 'product') # Ensures a product is only once in a cart

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in {self.cart.user.username}'s cart"

    def get_total_price(self):
        return self.quantity * self.product.price

class DeliveryAddress(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='Italia')
    created_at = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(max_length=50, default="Indirizzo principale")

    def __str__(self):
        return f"{self.street}, {self.city}, {self.province}"



class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    address = models.ForeignKey(DeliveryAddress, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders') # if an address is deleted, orders will still reference to a valid address
    delivery_date = models.DateField()
    delivered = models.BooleanField(default=False)
    shipped = models.BooleanField(default=False)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_method = models.CharField(max_length=50, default='standard')


    class Meta:
        ordering = ('-created_at',)

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


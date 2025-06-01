from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
    delivery_address = models.ForeignKey(
        'AddressList',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='delivery_addresses'
    )

    def __str__(self):
        return self.username

class AddressList(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100, blank=True, null=True)  # Optional field

    def __str__(self):
        return f"{self.address}, {self.city}, {self.country or 'N/A'}"
    class Meta:
        verbose_name_plural = "Address Lists"
        unique_together = ('user', 'address')
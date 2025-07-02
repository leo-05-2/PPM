from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import RegexValidator

# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field must be set')
        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)

class CustomUser(AbstractUser):
   phone_number = models.CharField(max_length=15, blank=True, null=True, validators=[
            RegexValidator(
                regex=r'^\+\d{2,3}\d{10}$',
                message="Il numero di telefono deve essere nel formato +CCXXXXXXXXXX o +CCCXXXXXXXXXX (prefisso di 2 o 3 cifre seguito da 10 cifre)."
            )
        ])

   favorite_list = models.ManyToManyField('products.Product', blank=True, related_name='favorited_by')
   objects = CustomUserManager()

   def __str__(self):
       return self.username

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100, blank=False, null=False)
    postal_code = models.CharField(max_length=20, blank=False, null=False)
    nickname = models.CharField(max_length=50, default="Indirizzo principale")
    country = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.street}, {self.city}, {self.postal_code}, {self.country}, {self.nickname}"

    class Meta:
        verbose_name_plural = "Address Lists"
class PaymentMethod(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='payment_methods')
    card_number = models.CharField(
        max_length=16,
        validators=[
            RegexValidator(regex=r'^\d{16}$', message="Il numero della carta deve essere di 16 cifre numeriche.")]
    )
    card_expiry = models.CharField(
        max_length=5,
        validators=[
            RegexValidator(regex=r'^\d{2}/\d{2}$', message="La data di scadenza deve essere nel formato MM/AA.")]
    )
    card_cvv = models.CharField(
        max_length=3,
        validators=[RegexValidator(regex=r'^\d{3}$', message="Il CVV deve essere di 3 cifre numeriche.")]
    )

    def __str__(self):
        return f"{self.user.username} - {self.card_number[-4:]}"  # Show last 4 digits of the card
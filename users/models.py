from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    delivery_address = models.CharField(max_length=255, blank=True, null=True)  #todo: add a list?

    def __str__(self):
        return self.user.username


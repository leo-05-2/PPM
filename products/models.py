from django.db import models

# Create your models here.


class Category(models.Model):


    name = models.CharField(max_length=200, unique=True)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

CATEGORY_CHOICES = (
        ('alimenti', 'Alimenti'),
        ('abbigliamento', 'Abbigliamento'),
        ('accessori', 'Accessori'),
        ('bevande', 'Bevande'),
    )

class Product(models.Model):
    category = models.ManyToManyField(Category)
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField()
    available = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    added_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, related_name='products_added', null=True, blank=True)
    modified_by = models.ForeignKey('users.CustomUser', on_delete=models.SET_NULL, related_name='products_modified', null=True, blank=True)


    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


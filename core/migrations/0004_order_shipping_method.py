# Generated by Django 5.2 on 2025-06-20 10:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_order_shipping_cost'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_method',
            field=models.CharField(default='standard', max_length=50),
        ),
    ]

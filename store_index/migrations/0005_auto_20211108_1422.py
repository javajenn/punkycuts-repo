# Generated by Django 3.2.8 on 2021-11-08 19:22

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store_index', '0004_auto_20211108_1416'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='BillingAddress',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='customer',
            name='BillingCity',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='customer',
            name='BillingState',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='BillingState', to='store_index.state'),
        ),
        migrations.AddField(
            model_name='customer',
            name='BillingZipCode',
            field=models.CharField(default=None, max_length=5),
        ),
        migrations.AddField(
            model_name='customer',
            name='Email',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='customer',
            name='FirstName',
            field=models.CharField(default=None, max_length=20),
        ),
        migrations.AddField(
            model_name='customer',
            name='LastName',
            field=models.CharField(default=None, max_length=20),
        ),
        migrations.AddField(
            model_name='customer',
            name='Password',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='customer',
            name='PhoneNumber',
            field=models.CharField(default=None, max_length=16, unique=True, validators=[django.core.validators.RegexValidator(regex='^\\+?1?\\d{8,15}$')]),
        ),
        migrations.AddField(
            model_name='customer',
            name='ShippingAddress',
            field=models.CharField(default=None, max_length=100),
        ),
        migrations.AddField(
            model_name='customer',
            name='ShippingCity',
            field=models.CharField(default=None, max_length=50),
        ),
        migrations.AddField(
            model_name='customer',
            name='ShippingState',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='ShippingState', to='store_index.state'),
        ),
        migrations.AddField(
            model_name='customer',
            name='ShippingZipCode',
            field=models.CharField(default=None, max_length=5),
        ),
        migrations.AddField(
            model_name='customer',
            name='Username',
            field=models.CharField(default=None, max_length=50),
        ),
    ]

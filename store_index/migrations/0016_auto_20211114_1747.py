# Generated by Django 3.2.8 on 2021-11-14 22:47

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store_index', '0015_auto_20211114_1734'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='BillingState',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='BillingState', to='store_index.state'),
        ),
        migrations.AlterField(
            model_name='customer',
            name='FirstName',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='customer',
            name='LastName',
            field=models.CharField(default='', max_length=20),
        ),
        migrations.AlterField(
            model_name='customer',
            name='ShippingState',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='ShippingState', to='store_index.state'),
        ),
    ]

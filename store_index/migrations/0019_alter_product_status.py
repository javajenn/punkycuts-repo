# Generated by Django 3.2.8 on 2021-11-15 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store_index', '0018_auto_20211115_1657'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='Status',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store_index.status'),
        ),
    ]

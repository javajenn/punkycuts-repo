# Generated by Django 3.2.8 on 2021-11-14 20:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_index', '0012_auto_20211113_2359'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customer',
            name='Email',
            field=models.CharField(blank=True, default='', max_length=50, unique=True),
        ),
    ]
# Generated by Django 3.2.8 on 2021-11-13 22:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store_index', '0007_auto_20211113_1708'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customer',
            name='Password',
        ),
        migrations.RemoveField(
            model_name='customer',
            name='Username',
        ),
    ]
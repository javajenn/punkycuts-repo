# Generated by Django 3.2.8 on 2021-11-15 21:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store_index', '0017_customer_is_email_verified'),
    ]

    operations = [
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Product_Type', models.CharField(max_length=100)),
            ],
            options={
                'verbose_name_plural': 'type',
            },
        ),
        migrations.AlterField(
            model_name='product',
            name='Status',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='store_index.status'),
        ),
        migrations.AddField(
            model_name='product',
            name='Type',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, to='store_index.type'),
        ),
    ]

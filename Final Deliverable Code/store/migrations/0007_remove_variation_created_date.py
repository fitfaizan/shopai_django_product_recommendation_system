# Generated by Django 4.2.7 on 2023-11-21 11:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_product_is_available'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='variation',
            name='created_date',
        ),
    ]

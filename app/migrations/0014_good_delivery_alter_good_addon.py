# Generated by Django 4.2 on 2023-11-22 16:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_order_food_amount_order_package_amount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='good',
            name='delivery',
            field=models.BooleanField(default=False, verbose_name='Does The Food Need Delivery Package'),
        ),
        migrations.AlterField(
            model_name='good',
            name='addon',
            field=models.BooleanField(default=False, verbose_name='Does The Food Need Other Items'),
        ),
    ]

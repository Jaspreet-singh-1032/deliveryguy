# Generated by Django 4.2 on 2023-11-19 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_remove_order_deliverypackages_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='addon',
            field=models.ManyToManyField(blank=True, to='app.addongoods'),
        ),
    ]

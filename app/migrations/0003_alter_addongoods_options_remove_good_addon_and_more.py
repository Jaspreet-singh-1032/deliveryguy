# Generated by Django 4.2 on 2023-11-18 12:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_addongoods_good_addon'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='addongoods',
            options={'verbose_name': 'AddonGoods', 'verbose_name_plural': 'Addon Foods'},
        ),
        migrations.RemoveField(
            model_name='good',
            name='addon',
        ),
        migrations.AddField(
            model_name='addongoods',
            name='food',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.good'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='orderitem',
            name='addon',
            field=models.ManyToManyField(to='app.addongoods'),
        ),
    ]
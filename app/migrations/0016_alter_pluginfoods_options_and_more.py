# Generated by Django 4.2 on 2023-11-27 06:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0015_pluginfoods_pluginorderitem_orderitem_plugin'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='pluginfoods',
            options={'verbose_name': 'Plugin Foods', 'verbose_name_plural': 'Plugin Foods'},
        ),
        migrations.AlterModelOptions(
            name='pluginorderitem',
            options={'verbose_name': 'Plugin Order', 'verbose_name_plural': 'Plugin Orders'},
        ),
        migrations.AddField(
            model_name='pluginorderitem',
            name='foods',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='app.good'),
            preserve_default=False,
        ),
    ]

# Generated by Django 2.2.12 on 2020-10-06 15:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('luckygardener', '0003_auto_20201004_2117'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contestluckygardener',
            name='image_ns',
            field=models.ImageField(blank=True, null=True, upload_to='luckygardener'),
        ),
        migrations.AlterField(
            model_name='contestluckygardener',
            name='image_ss',
            field=models.ImageField(blank=True, null=True, upload_to='luckygardener'),
        ),
    ]

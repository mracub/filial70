# Generated by Django 2.2.12 on 2020-09-22 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cost_cadastr', '0011_auto_20200921_2122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clobject',
            name='Name',
            field=models.CharField(blank=True, max_length=4096, null=True),
        ),
    ]

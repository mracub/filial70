# Generated by Django 2.2.12 on 2020-09-15 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cost_cadastr', '0008_auto_20200915_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clobject',
            name='Name',
            field=models.CharField(blank=True, max_length=1024, null=True),
        ),
    ]

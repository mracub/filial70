# Generated by Django 2.2.12 on 2020-09-12 17:42

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cost_cadastr', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clobject',
            name='clobjecttype',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClObjectType'),
        ),
    ]
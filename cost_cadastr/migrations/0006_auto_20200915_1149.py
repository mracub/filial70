# Generated by Django 2.2.12 on 2020-09-15 04:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cost_cadastr', '0005_auto_20200914_1643'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='clobject',
            name='clkeyparam',
        ),
        migrations.AddField(
            model_name='clkeyparam',
            name='clobject',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClObject'),
        ),
    ]

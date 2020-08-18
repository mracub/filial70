# Generated by Django 2.2.12 on 2020-08-04 17:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cost_cadastr', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cadastrcosts',
            name='doc_cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cost_cadastr.Docs'),
        ),
        migrations.AlterField(
            model_name='object',
            name='cost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cost_cadastr.CadastrCosts'),
        ),
        migrations.AlterField(
            model_name='object',
            name='filecost',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='cost_cadastr.FilesCost'),
        ),
    ]

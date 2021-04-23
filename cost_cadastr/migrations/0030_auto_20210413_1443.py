# Generated by Django 2.2.12 on 2021-04-13 07:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cost_cadastr', '0029_auto_20210329_1456'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClAreaCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('areaCode', models.CharField(max_length=12)),
                ('areaName', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ClLandUse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('landUseCode', models.CharField(max_length=12)),
                ('landUseName', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='ClOldNumbers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oldNumber', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='ClOldNumbersTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('oldNumberCode', models.CharField(max_length=12)),
                ('oldNumberName', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ClState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('statusCode', models.CharField(max_length=12)),
                ('statusName', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ClUnits',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unitCode', models.CharField(max_length=12)),
                ('unitName', models.CharField(max_length=64)),
            ],
        ),
        migrations.CreateModel(
            name='ClUtilizations',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utilizationByDoc', models.CharField(max_length=2048)),
            ],
        ),
        migrations.CreateModel(
            name='ClUtilizationsCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('utilizationCode', models.CharField(max_length=12)),
                ('utilizationName', models.CharField(max_length=512)),
            ],
        ),
        migrations.CreateModel(
            name='ClZuTypes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('objectTypeCode', models.CharField(max_length=12)),
                ('objectTypeName', models.CharField(max_length=64)),
            ],
        ),
        migrations.AddField(
            model_name='clobject',
            name='DateCreatedDoc',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='clobject',
            name='Inaccuracy',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True),
        ),
        migrations.AlterField(
            model_name='filedocs',
            name='filename',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='filedocs',
            name='filepath',
            field=models.CharField(blank=True, default=None, max_length=256, null=True),
        ),
        migrations.AlterField(
            model_name='filedocs',
            name='urlfile',
            field=models.URLField(blank=True, default=None, max_length=1024, null=True),
        ),
        migrations.AddIndex(
            model_name='clzutypes',
            index=models.Index(fields=['objectTypeCode'], name='cost_cadast_objectT_22d378_idx'),
        ),
        migrations.AddIndex(
            model_name='clutilizationscode',
            index=models.Index(fields=['utilizationCode'], name='cost_cadast_utiliza_1ad4d9_idx'),
        ),
        migrations.AddField(
            model_name='clutilizations',
            name='utilizationCode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClUtilizationsCode'),
        ),
        migrations.AddIndex(
            model_name='clunits',
            index=models.Index(fields=['unitCode'], name='cost_cadast_unitCod_4753ae_idx'),
        ),
        migrations.AddIndex(
            model_name='clstate',
            index=models.Index(fields=['statusCode'], name='cost_cadast_statusC_98f444_idx'),
        ),
        migrations.AddIndex(
            model_name='cloldnumberstypes',
            index=models.Index(fields=['oldNumberCode'], name='cost_cadast_oldNumb_075de2_idx'),
        ),
        migrations.AddField(
            model_name='cloldnumbers',
            name='oldNumberCode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClOldNumbersTypes'),
        ),
        migrations.AddIndex(
            model_name='cllanduse',
            index=models.Index(fields=['landUseCode'], name='cost_cadast_landUse_a3d67e_idx'),
        ),
        migrations.AddIndex(
            model_name='clareacode',
            index=models.Index(fields=['areaCode'], name='cost_cadast_areaCod_7c7fb9_idx'),
        ),
        migrations.AddField(
            model_name='clobject',
            name='clareacode',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClAreaCode'),
        ),
        migrations.AddField(
            model_name='clobject',
            name='cllanduse',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClLandUse'),
        ),
        migrations.AddField(
            model_name='clobject',
            name='cloldnumbers',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClOldNumbers'),
        ),
        migrations.AddField(
            model_name='clobject',
            name='clstate',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClState'),
        ),
        migrations.AddField(
            model_name='clobject',
            name='clunits',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClUnits'),
        ),
        migrations.AddField(
            model_name='clobject',
            name='clutilization',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClUtilizations'),
        ),
        migrations.AddField(
            model_name='clobject',
            name='clzutype',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, to='cost_cadastr.ClZuTypes'),
        ),
        migrations.AddIndex(
            model_name='clutilizations',
            index=models.Index(fields=['utilizationCode', 'utilizationByDoc'], name='cost_cadast_utiliza_8a0ea8_idx'),
        ),
        migrations.AddIndex(
            model_name='cloldnumbers',
            index=models.Index(fields=['oldNumber'], name='cost_cadast_oldNumb_cface2_idx'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-09-21 11:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0188_auto_20200922_0142'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorDisaggregationTarget',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('value', models.DecimalField(blank=True, decimal_places=2, max_digits=20, null=True, verbose_name='disaggregation target value')),
                ('dimension_value', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='indicator_disaggregation_targets', to='rsr.IndicatorDimensionValue')),
                ('indicator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='disaggregation_targets', to='rsr.Indicator', verbose_name='indicator')),
            ],
            options={
                'verbose_name': 'indicator disaggregation target',
                'verbose_name_plural': 'indicator disaggregation targets',
                'ordering': ('id',),
            },
        ),
    ]

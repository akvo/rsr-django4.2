# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-03-18 23:04
from __future__ import unicode_literals

import akvo.rsr.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0205_auto_20210407_0619'),
    ]

    operations = [
        migrations.CreateModel(
            name='IndicatorPeriodLabel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', akvo.rsr.fields.ValidXMLTextField(blank=True, verbose_name='label')),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='period_labels', to='rsr.Project', verbose_name='indicator period data')),
            ],
            options={
                'verbose_name': 'indicator period label',
                'verbose_name_plural': 'indicator period labels',
                'ordering': ('-id',),
            },
        ),
        migrations.AddField(
            model_name='indicatorperiod',
            name='label',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='periods', to='rsr.IndicatorPeriodLabel', verbose_name='label'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-15 09:07
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0208_country_level_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='partnersite',
            name='program',
            field=models.ForeignKey(blank=True, help_text='Select your program from the drop-down list.', null=True, on_delete=django.db.models.deletion.CASCADE, to='rsr.ProjectHierarchy'),
        ),
    ]

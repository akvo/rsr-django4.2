# -*- coding: utf-8 -*-
# Generated by Django 1.11.20 on 2019-05-10 12:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0148_indicatordimension_parent_dimension'),
    ]

    operations = [
        migrations.AddField(
            model_name='indicator',
            name='export_to_iati',
            field=models.BooleanField(default=True, help_text='Choose whether this indicator will be included in IATI exports. If you are not exporting to IATI, you may ignore this option.', verbose_name='Include indicator in IATI exports'),
        ),
    ]
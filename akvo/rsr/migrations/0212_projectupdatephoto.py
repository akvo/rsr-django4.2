# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-04-26 11:31
from __future__ import unicode_literals

import akvo.rsr.fields
import akvo.rsr.models.project_update
from django.db import migrations, models
import django.db.models.deletion
import sorl.thumbnail.fields


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0211_indicatorperiod_target_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProjectUpdatePhoto',
            fields=[
                ('id', models.AutoField(auto_created=True,
                 primary_key=True, serialize=False, verbose_name='ID')),
                ('photo', sorl.thumbnail.fields.ImageField(help_text='The image should have 4:3 height:width ratio for best displaying result',
                 upload_to=akvo.rsr.models.project_update.update_image_path, verbose_name='photo')),
                ('caption', akvo.rsr.fields.ValidXMLTextField(
                    blank=True, verbose_name='photo caption')),
                ('credit', akvo.rsr.fields.ValidXMLTextField(
                    blank=True, verbose_name='photo credit')),
                ('update', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                 related_name='photos', to='rsr.ProjectUpdate')),
            ],
        ),
    ]

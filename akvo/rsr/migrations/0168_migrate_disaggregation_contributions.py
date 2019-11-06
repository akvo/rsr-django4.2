# -*- coding: utf-8 -*-
# Generated by Django 1.11.23 on 2019-09-30 13:12
from __future__ import unicode_literals

from django.db import migrations
from akvo.rsr.models.result.disaggregation_contribution_handler import DisaggregationContributionHandler

def migrate_disaggregation_contributions(apps, schema_editor):
    DisaggregationContribution = apps.get_model('rsr', 'DisaggregationContribution')
    IndicatorPeriodDisaggregation = apps.get_model('rsr', 'IndicatorPeriodDisaggregation')

    handler = DisaggregationContributionHandler(
        IndicatorPeriodDisaggregation.objects,
        DisaggregationContribution.objects
    )

    for disaggregation in IndicatorPeriodDisaggregation.objects.all():
        handler.handle(disaggregation)


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0167_disaggregationcontribution'),
    ]

    operations = [
        migrations.RunPython(migrate_disaggregation_contributions),
    ]
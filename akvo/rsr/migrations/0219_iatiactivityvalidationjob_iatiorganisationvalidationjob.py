# Generated by Django 3.2.10 on 2022-07-18 12:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsr', '0218_project_thumbnail_cache'),
    ]

    operations = [
        migrations.CreateModel(
            name='IatiOrganisationValidationJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_at', models.DateTimeField(help_text='Date and time after which the job is expected to run')),
                ('started_at', models.DateTimeField(help_text='Date and time when the job is runned', null=True)),
                ('finished_at', models.DateTimeField(help_text='Date and time when the job is done', null=True)),
                ('attempts', models.IntegerField(default=0)),
                ('organisation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rsr.organisation')),
            ],
            options={
                'ordering': ('scheduled_at',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='IatiActivityValidationJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('scheduled_at', models.DateTimeField(help_text='Date and time after which the job is expected to run')),
                ('started_at', models.DateTimeField(help_text='Date and time when the job is runned', null=True)),
                ('finished_at', models.DateTimeField(help_text='Date and time when the job is done', null=True)),
                ('attempts', models.IntegerField(default=0)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rsr.project')),
            ],
            options={
                'ordering': ('scheduled_at',),
                'abstract': False,
            },
        ),
    ]
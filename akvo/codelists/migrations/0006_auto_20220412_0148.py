# Generated by Django 3.2.10 on 2022-04-12 01:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('codelists', '0005_auto_20190225_1046'),
    ]

    operations = [
        migrations.AddField(
            model_name='crschannelcode',
            name='description',
            field=models.TextField(blank=True, verbose_name='description'),
        ),
        migrations.CreateModel(
            name='UNSDGTargets',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.TextField(blank=True, verbose_name='name')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'unsdg targets',
                'verbose_name_plural': 'unsdg targets',
                'ordering': ('-version', 'code'),
            },
        ),
        migrations.CreateModel(
            name='UNSDGGoals',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='name')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'unsdg goals',
                'verbose_name_plural': 'unsdg goals',
                'ordering': ('-version', 'code'),
            },
        ),
        migrations.CreateModel(
            name='TagVocabulary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='name')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'tag vocabulary',
                'verbose_name_plural': 'tag vocabularies',
                'ordering': ('-version', 'code'),
            },
        ),
        migrations.CreateModel(
            name='ResultVocabulary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='name')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'result vocabulary',
                'verbose_name_plural': 'result vocabularies',
                'ordering': ('-version', 'code'),
            },
        ),
        migrations.CreateModel(
            name='EarmarkingCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'earmarking category',
                'verbose_name_plural': 'earmarking categories',
                'ordering': ('-version', 'code'),
            },
        ),
        migrations.CreateModel(
            name='CashandVoucherModalities',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'cashand voucher modalities',
                'verbose_name_plural': 'cashand voucher modalities',
                'ordering': ('-version', 'code'),
            },
        ),
        migrations.CreateModel(
            name='BudgetNotProvided',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='name')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'budget not provided',
                'verbose_name_plural': 'budget not provideds',
                'ordering': ('-version', 'code'),
            },
        ),
        migrations.CreateModel(
            name='AidTypeVocabulary',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(blank=True, db_index=True, max_length=100, verbose_name='code')),
                ('name', models.CharField(blank=True, max_length=300, verbose_name='name')),
                ('description', models.TextField(blank=True, verbose_name='description')),
                ('url', models.URLField(blank=True, verbose_name='url')),
                ('version', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='codelists.version', verbose_name='version')),
            ],
            options={
                'verbose_name': 'aid type vocabulary',
                'verbose_name_plural': 'aid type vocabularies',
                'ordering': ('-version', 'code'),
            },
        ),
    ]

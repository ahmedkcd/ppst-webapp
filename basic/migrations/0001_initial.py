# Generated by Django 5.1.6 on 2025-03-28 00:26

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Statistics',
            fields=[
                ('stats_id', models.AutoField(primary_key=True, serialize=False)),
                ('total_tests', models.IntegerField(default=0)),
                ('total_responses', models.IntegerField(default=0)),
                ('avg_latency', models.FloatField(blank=True, null=True)),
                ('accuracy', models.FloatField(blank=True, null=True)),
                ('last_updated', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Stimuli',
            fields=[
                ('stim_id', models.AutoField(primary_key=True, serialize=False)),
                ('stimulus', models.TextField()),
                ('correct_response', models.TextField()),
                ('span', models.IntegerField()),
                ('type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='TestSession',
            fields=[
                ('test_id', models.AutoField(primary_key=True, serialize=False)),
                ('age', models.IntegerField()),
                ('date', models.DateTimeField(null=True)),
                ('duration', models.DurationField(null=True)),
                ('avg_latency', models.FloatField(null=True)),
                ('accuracy', models.FloatField(null=True)),
                ('stimuli_order', models.TextField(null=True)),
                ('state', models.TextField(default='ready')),
                ('language', models.TextField(default='en')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Response',
            fields=[
                ('response_id', models.AutoField(primary_key=True, serialize=False)),
                ('response', models.TextField(null=True)),
                ('latencies', models.TextField(null=True)),
                ('is_correct', models.BooleanField(null=True)),
                ('stim', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='basic.stimuli')),
                ('test', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='basic.testsession')),
            ],
        ),
    ]

# Generated by Django 2.1.4 on 2018-12-28 08:37

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodmenow', '0008_auto_20181227_1516'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preference',
            name='food_genre',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, default='', max_length=256), blank=[], null=True, size=None),
        ),
        migrations.AlterField(
            model_name='preference',
            name='price_max',
            field=models.CharField(blank=True, default='', max_length=1, null=True),
        ),
        migrations.AlterField(
            model_name='preference',
            name='price_min',
            field=models.CharField(blank=True, default='', max_length=1, null=True),
        ),
    ]

# Generated by Django 2.1.4 on 2018-12-28 08:47

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('foodmenow', '0009_auto_20181228_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='preference',
            name='food_genre',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(blank=True, default=None, max_length=256), blank=[], null=True, size=None),
        ),
    ]

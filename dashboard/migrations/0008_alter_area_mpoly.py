# Generated by Django 3.2.9 on 2021-12-03 08:11

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0007_area'),
    ]

    operations = [
        migrations.AlterField(
            model_name='area',
            name='mpoly',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=3857),
        ),
    ]

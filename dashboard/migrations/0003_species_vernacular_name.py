# Generated by Django 4.0.6 on 2022-07-04 14:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0002_alter_dataimport_options_observation_references'),
    ]

    operations = [
        migrations.AddField(
            model_name='species',
            name='vernacular_name',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]

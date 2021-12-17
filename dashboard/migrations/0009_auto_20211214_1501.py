# Generated by Django 3.2.10 on 2021-12-14 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0008_alter_area_mpoly'),
    ]

    operations = [
        migrations.AddField(
            model_name='occurrence',
            name='basis_of_record',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='coordinate_uncertainty_in_meters',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='individual_count',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='locality',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='municipality',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='occurrence',
            name='recorded_by',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
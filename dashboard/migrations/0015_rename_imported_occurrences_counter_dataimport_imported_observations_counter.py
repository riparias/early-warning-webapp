# Generated by Django 3.2.10 on 2021-12-21 11:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0014_alert_email_notifications_frequency'),
    ]

    operations = [
        migrations.RenameField(
            model_name='dataimport',
            old_name='imported_occurrences_counter',
            new_name='imported_observations_counter',
        ),
    ]
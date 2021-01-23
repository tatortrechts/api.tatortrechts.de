# Generated by Django 3.1.5 on 2021-01-23 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0026_incident_orig_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='contexts',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incident',
            name='factums',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='incident',
            name='tags',
            field=models.TextField(blank=True, null=True),
        ),
    ]

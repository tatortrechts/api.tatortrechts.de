# Generated by Django 3.1.1 on 2020-09-23 12:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0021_location_search_vector'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incident',
            name='iso3166_2',
        ),
    ]

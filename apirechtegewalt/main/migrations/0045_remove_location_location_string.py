# Generated by Django 3.1.8 on 2021-05-03 20:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0044_auto_20210213_2219'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='location_string',
        ),
    ]
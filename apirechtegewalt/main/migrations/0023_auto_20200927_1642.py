# Generated by Django 3.1.1 on 2020-09-27 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_remove_incident_iso3166_2'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='subdivisions',
        ),
        migrations.AddField(
            model_name='location',
            name='city',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='country',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='county',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='district',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='house_number',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='postal_code',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='state',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='location',
            name='street',
            field=models.CharField(max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='location_string',
            field=models.TextField(unique=True),
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-23 22:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0028_incident_motives'),
    ]

    operations = [
        migrations.AlterField(
            model_name='source',
            name='url',
            field=models.CharField(blank=True, default='', max_length=255, null=True),
        ),
    ]

# Generated by Django 3.1.5 on 2021-01-23 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0027_auto_20210123_2208'),
    ]

    operations = [
        migrations.AddField(
            model_name='incident',
            name='motives',
            field=models.TextField(blank=True, null=True),
        ),
    ]

# Generated by Django 3.1 on 2020-09-01 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20200901_1331'),
    ]

    operations = [
        migrations.AlterField(
            model_name='incident',
            name='rg_id',
            field=models.CharField(max_length=255, unique=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='rg_id',
            field=models.CharField(max_length=255, unique=True),
        ),
    ]
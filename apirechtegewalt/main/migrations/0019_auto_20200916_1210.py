# Generated by Django 3.1.1 on 2020-09-16 12:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0018_auto_20200911_1435'),
    ]

    operations = [
        migrations.AddField(
            model_name='chronicle',
            name='region',
            field=models.CharField(default=None, max_length=255),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='chronicle',
            name='iso3166_1',
            field=models.CharField(blank=True, max_length=2, null=True),
        ),
    ]
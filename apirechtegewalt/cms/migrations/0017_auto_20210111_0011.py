# Generated by Django 3.1.5 on 2021-01-11 00:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0016_auto_20210111_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='article_date',
            field=models.DateField(blank=True, null=True, verbose_name='Article date (only for blog)'),
        ),
    ]

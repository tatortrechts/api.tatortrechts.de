# Generated by Django 3.1.5 on 2021-01-15 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0017_auto_20210111_0011'),
    ]

    operations = [
        migrations.AddField(
            model_name='contentpage',
            name='article_teaser',
            field=models.TextField(blank=True, null=True, verbose_name='Article teaser (only for blog)'),
        ),
    ]
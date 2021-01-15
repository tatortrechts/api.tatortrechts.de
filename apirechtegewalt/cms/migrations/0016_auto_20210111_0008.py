# Generated by Django 3.1.5 on 2021-01-11 00:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0015_auto_20210110_2318'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contentpage',
            name='date',
        ),
        migrations.AddField(
            model_name='contentpage',
            name='article_date',
            field=models.DateField(blank=True, null=True, verbose_name='Article date (only useful for '),
        ),
        migrations.AddField(
            model_name='contentpage',
            name='article_image',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to='cms.customimage'),
        ),
    ]
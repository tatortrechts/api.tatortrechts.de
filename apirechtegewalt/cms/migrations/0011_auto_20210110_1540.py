# Generated by Django 3.1.5 on 2021-01-10 15:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0010_auto_20210109_2358'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='layout',
            field=models.CharField(choices=[('FC', 'Full-width container'), ('CM', 'Centered 7/12-sized column')], default='CM', max_length=2),
        ),
    ]

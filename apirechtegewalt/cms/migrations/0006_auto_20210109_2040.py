# Generated by Django 3.1.3 on 2021-01-09 20:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0005_auto_20210109_2027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='layout',
            field=models.CharField(choices=[('FC', 'Full-width container'), ('CM', 'Centered 7-size column')], default='FC', max_length=2),
        ),
    ]

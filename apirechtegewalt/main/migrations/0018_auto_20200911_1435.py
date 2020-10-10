# Generated by Django 3.1.1 on 2020-09-11 14:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20200911_1432'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='incident',
            name='aggregator',
        ),
        migrations.AddField(
            model_name='incident',
            name='chronicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.chronicle'),
        ),
    ]
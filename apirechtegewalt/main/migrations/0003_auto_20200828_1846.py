# Generated by Django 3.1 on 2020-08-28 18:46

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20200825_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='location',
            name='rg_id',
        ),
        migrations.AddField(
            model_name='incident',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='incident',
            name='location',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.location'),
        ),
        migrations.AddField(
            model_name='incident',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='location',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='location',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='source',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='incident',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to='main.incident'),
        ),
        migrations.AddField(
            model_name='source',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='subdivisions',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]
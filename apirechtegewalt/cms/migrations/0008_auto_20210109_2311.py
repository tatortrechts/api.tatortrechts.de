# Generated by Django 3.1.3 on 2021-01-09 23:11

from django.db import migrations
import wagtail.core.blocks
import wagtail.core.fields
import wagtail.images.blocks


class Migration(migrations.Migration):

    dependencies = [
        ('cms', '0007_customimage_customrendition'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contentpage',
            name='body',
            field=wagtail.core.fields.StreamField([('heading', wagtail.core.blocks.CharBlock(form_classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('quote', wagtail.core.blocks.TextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('two_columns', wagtail.core.blocks.StructBlock([('left_column', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.core.blocks.TextBlock())], icon='arrow-right', label='Left column content')), ('right_column', wagtail.core.blocks.StreamBlock([('heading', wagtail.core.blocks.CharBlock(form_classname='full title')), ('paragraph', wagtail.core.blocks.RichTextBlock()), ('image', wagtail.images.blocks.ImageChooserBlock()), ('quote', wagtail.core.blocks.TextBlock())], icon='arrow-right', label='Right column content'))]))]),
        ),
    ]

from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock


class ColumnBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(classname="full title")
    paragraph = blocks.RichTextBlock()
    image = ImageChooserBlock()

    class Meta:
        template = "cms/column.html"


class TwoColumnBlock(blocks.StructBlock):

    left_column = ColumnBlock(icon="arrow-right", label="Left column content")
    right_column = ColumnBlock(icon="arrow-right", label="Right column content")

    class Meta:
        template = "cms/two_column_block.html"
        icon = "placeholder"
        label = "Two Columns"


class ContentPage(Page):
    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
            ("image", ImageChooserBlock()),
            ("two_columns", TwoColumnBlock()),
        ]
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
    ]

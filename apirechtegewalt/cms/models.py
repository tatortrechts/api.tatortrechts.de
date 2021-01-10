from django.db import models
from wagtail.admin.edit_handlers import FieldPanel, StreamFieldPanel
from wagtail.core import blocks
from wagtail.core.fields import StreamField
from wagtail.core.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.api import APIField

from wagtail.images.models import Image, AbstractImage, AbstractRendition


class CustomImage(AbstractImage):
    # Add any extra fields to image here

    # eg. To add a caption field:
    caption = models.TextField(blank=True, null=True)

    admin_form_fields = Image.admin_form_fields + (
        # Then add the field names here to make them appear in the form:
        "caption",
    )


class CustomRendition(AbstractRendition):
    image = models.ForeignKey(
        CustomImage, on_delete=models.CASCADE, related_name="renditions"
    )

    class Meta:
        unique_together = (("image", "filter_spec", "focal_point_key"),)


class QuoteBlock(blocks.StructBlock):
    quote = blocks.TextBlock()
    author = blocks.TextBlock(required=False)


class ColumnBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(classname="full title")
    paragraph = blocks.RichTextBlock()
    image = ImageChooserBlock()
    quote = QuoteBlock()

    class Meta:
        template = "cms/column.html"


class TwoColumnBlock(blocks.StructBlock):

    left_column = ColumnBlock(icon="arrow-right", label="Left column content")
    right_column = ColumnBlock(icon="arrow-right", label="Right column content")

    class Meta:
        template = "cms/two_column_block.html"
        icon = "placeholder"
        label = "Two Columns"


class PageLayout(models.TextChoices):
    FULL_CONTAINER = "FC", "Full-width container"
    CENTERED_MIDDLE = "CM", "Centered 7/12-sized column"


class ContentPage(Page):
    date = models.DateField("Post date", null=True, blank=True)
    layout = models.CharField(
        max_length=2,
        choices=PageLayout.choices,
        default=PageLayout.CENTERED_MIDDLE,
    )

    body = StreamField(
        [
            ("heading", blocks.CharBlock(classname="full title")),
            ("paragraph", blocks.RichTextBlock()),
            ("quote", QuoteBlock()),
            ("image", ImageChooserBlock()),
            ("two_columns", TwoColumnBlock()),
        ]
    )

    content_panels = Page.content_panels + [
        StreamFieldPanel("body"),
        FieldPanel("date"),
        FieldPanel("layout"),
    ]

    # Export fields over the API
    api_fields = [
        APIField("body"),
        APIField("date"),
        APIField("layout"),
    ]

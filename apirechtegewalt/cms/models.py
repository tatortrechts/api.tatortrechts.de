from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail import blocks
from wagtail.fields import StreamField
from wagtail.models import Page
from wagtail.images.blocks import ImageChooserBlock
from wagtail.api import APIField
from wagtail.images.api.fields import ImageRenditionField

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


# single colum can't be nested
class ColumnSingleBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(classname="full title")
    paragraph = blocks.RichTextBlock()
    image = ImageChooserBlock()
    quote = QuoteBlock()
    raw_html = blocks.RawHTMLBlock()


class CenteredColumnBlock(blocks.StructBlock):
    column = ColumnSingleBlock(icon="wagtail", label="Centered column content")
    column_size = blocks.IntegerBlock(
        min_value=1, max_value=12, default=6, label="set the size of the column (1-12)"
    )


# also make it possible to use a centered column in a double column
class ColumnBlock(blocks.StreamBlock):
    heading = blocks.CharBlock(classname="full title")
    paragraph = blocks.RichTextBlock()
    image = ImageChooserBlock()
    quote = QuoteBlock()
    raw_html = blocks.RawHTMLBlock()
    centered_column = CenteredColumnBlock()

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
    article_date = models.DateField(
        "Article date (only for blog)", null=True, blank=True
    )

    article_image = models.ForeignKey(
        "cms.CustomImage",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    article_image_caption = models.TextField(
        "Article image caption (only for blog)", null=True, blank=True
    )

    article_teaser = models.TextField(
        "Article teaser (only for blog)", null=True, blank=True
    )

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
            ("centered_column", CenteredColumnBlock()),
            ("raw_html", blocks.RawHTMLBlock()),
            ("list_child_pages", blocks.PageChooserBlock(can_choose_root=False)),
        ]
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
        FieldPanel("article_date"),
        FieldPanel("article_teaser"),
        FieldPanel("article_image_caption"),
        FieldPanel("layout"),
    ]

    promote_panels = [
        MultiFieldPanel(Page.promote_panels, "Common page configuration"),
        FieldPanel("article_image"),
    ]

    # Export fields over the API
    api_fields = [
        APIField("body"),
        APIField("article_date"),
        APIField("article_teaser"),
        APIField("article_image"),
        APIField("article_image_caption"),
        APIField("layout"),
        APIField(
            "article_image_thumbnail",
            serializer=ImageRenditionField("fill-1200x600", source="article_image"),
        ),
    ]

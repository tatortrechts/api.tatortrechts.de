from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import BaseAPIViewSet
from wagtail.api.v2.filters import ChildOfFilter, FieldsFilter, OrderingFilter
from wagtail.images.api.v2.views import ImagesAPIViewSet

from .models import ContentPage

api_router = WagtailAPIRouter("wagtailapi")


class ContentPagesAPIViewSet(BaseAPIViewSet):
    model = ContentPage

    filter_backends = [
        ChildOfFilter,
        FieldsFilter,
        OrderingFilter,
    ]

    known_query_parameters = BaseAPIViewSet.known_query_parameters.union(
        [
            "type",
            "child_of",
            "descendant_of",
            "translation_of",
            "locale",
            "live",
        ],
    )

    body_fields = BaseAPIViewSet.body_fields + [
        "title",
    ]

    meta_fields = BaseAPIViewSet.meta_fields + [
        "article_image",
        "slug",
        "show_in_menus",
        "seo_title",
        "search_description",
        "first_published_at",
        "live",
    ]

    listing_default_fields = BaseAPIViewSet.listing_default_fields + [
        "article_image",
        "article_image_thumbnail",
        "article_teaser",
        "article_date",
        "title",
        "slug",
        "first_published_at",
        "live",
    ]

    nested_default_fields = BaseAPIViewSet.nested_default_fields + [
        "title",
    ]

    # https://github.com/wagtail/wagtail/blob/971bdc0799a800a373e7326d9e564813934c09c6/wagtail/api/v2/views.py
    def get_base_queryset(self):
        queryset = ContentPage.objects.all().public().live().order_by('-article_date')
        return queryset


class CustomImagesAPIViewset(ImagesAPIViewSet):
    meta_fields = ImagesAPIViewSet.meta_fields + ["caption"]


api_router.register_endpoint("pages", ContentPagesAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewset)

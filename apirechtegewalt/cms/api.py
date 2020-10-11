from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import BaseAPIViewSet, FieldsFilter
from wagtail.images.api.v2.views import ImagesAPIViewSet

from .models import ContentPage

api_router = WagtailAPIRouter("wagtailapi")


class ContentPagesAPIViewSet(BaseAPIViewSet):
    """taken from https://github.com/wagtail/wagtail/blob/dd664218b122c5c2b09c954cbba1b1f991fa89d7/wagtail/api/v2/views.py"""

    model = ContentPage

    filter_backends = [
        FieldsFilter,
    ]

    known_query_parameters = BaseAPIViewSet.known_query_parameters.union(
        [
            "type",
            "child_of",
            "descendant_of",
        ]
    )
    body_fields = BaseAPIViewSet.body_fields + [
        "title",
    ]
    meta_fields = BaseAPIViewSet.meta_fields + [
        "slug",
        "show_in_menus",
        "seo_title",
        "search_description",
        "first_published_at",
    ]
    listing_default_fields = BaseAPIViewSet.listing_default_fields + [
        "title",
        "slug",
        "first_published_at",
    ]
    nested_default_fields = BaseAPIViewSet.nested_default_fields + [
        "title",
    ]


api_router.register_endpoint("pages", ContentPagesAPIViewSet)
api_router.register_endpoint("images", ImagesAPIViewSet)

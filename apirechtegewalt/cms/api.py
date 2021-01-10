from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import BaseAPIViewSet, FieldsFilter
from wagtail.images.api.v2.views import ImagesAPIViewSet

from .models import ContentPage

api_router = WagtailAPIRouter("wagtailapi")


class ContentPagesAPIViewSet(BaseAPIViewSet):
    model = ContentPage

    def __init__(self):
        BaseAPIViewSet.__init__(self)
        self.filter_backends += [
            FieldsFilter,
        ]
        self.body_fields += [
            "title",
        ]
        self.meta_fields += [
            "slug",
            "show_in_menus",
            "seo_title",
            "search_description",
            "first_published_at",
        ]

        self.listing_default_fields += [
            "title",
            "slug",
            "first_published_at",
        ]

        self.nested_default_fields += [
            "title",
        ]


class CustomImagesAPIViewset(ImagesAPIViewSet):
    def __init__(self):
        ImagesAPIViewSet.__init__(self)
        self.meta_fields += ["caption"]


api_router.register_endpoint("pages", ContentPagesAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewset)

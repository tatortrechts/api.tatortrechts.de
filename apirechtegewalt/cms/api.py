from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.views import BaseAPIViewSet, ChildOfFilter, FieldsFilter, OrderingFilter
from wagtail.images.api.v2.views import ImagesAPIViewSet

from .models import ContentPage

api_router = WagtailAPIRouter("wagtailapi")


# Not 100% sure why I did it like this, but I guess it was to additional fields to the meta_fields / listing_default_fields.
class ContentPagesAPIViewSet(BaseAPIViewSet):
    model = ContentPage

    def __init__(self):
        BaseAPIViewSet.__init__(self)
        self.filter_backends = [
            ChildOfFilter,
            FieldsFilter,
            OrderingFilter
        ]
        self.known_query_parameters = self.known_query_parameters.union(
            [
                "type",
                "child_of",
                "descendant_of",
                "translation_of",
                "locale",
                "live"
            ],
        )

        self.body_fields += [
            "title",
        ]
        self.meta_fields += [
            "article_image",
            "slug",
            "show_in_menus",
            "seo_title",
            "search_description",
            "first_published_at",
            "live"
        ]

        self.listing_default_fields += [
            "article_image",
            "article_image_thumbnail",
            "article_teaser",
            "article_date",
            "title",
            "slug",
            "first_published_at",
            "live"
        ]

        self.nested_default_fields += [
            "title",
        ]

    # https://github.com/wagtail/wagtail/blob/971bdc0799a800a373e7326d9e564813934c09c6/wagtail/api/v2/views.py
    def get_base_queryset(self):
        queryset = ContentPage.objects.all().public().live().order_by('-article_date')
        return queryset


class CustomImagesAPIViewset(ImagesAPIViewSet):
    def __init__(self):
        ImagesAPIViewSet.__init__(self)
        self.meta_fields += ["caption"]


api_router.register_endpoint("pages", ContentPagesAPIViewSet)
api_router.register_endpoint("images", CustomImagesAPIViewset)

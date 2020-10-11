from django.urls import include, path, re_path
from wagtail.admin import urls as wagtailadmin_urls
from wagtail.core import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

urlpatterns = [
    path("", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("pages/", include(wagtail_urls)),
]

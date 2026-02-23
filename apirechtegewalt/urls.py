"""
apirechtegewalt URL Configuration.
"""
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve

from django.conf import settings

urlpatterns = [
    path("admin/", admin.site.urls),
    path("content/", include("apirechtegewalt.cms.urls")),
    path("", include("apirechtegewalt.main.urls")),
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
]

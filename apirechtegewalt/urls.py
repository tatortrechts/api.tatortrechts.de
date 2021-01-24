"""
apirechtegewalt URL Configuration.
"""
from django.contrib import admin
from django.urls import include
from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .main.views import IncidentSubmittedCreate

urlpatterns = [
    path("neu/", IncidentSubmittedCreate.as_view()),
    path("admin/", admin.site.urls),
    path("content/", include("apirechtegewalt.cms.urls")),
    path("", include("apirechtegewalt.main.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

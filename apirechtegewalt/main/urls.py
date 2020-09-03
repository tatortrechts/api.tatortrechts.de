"""The main application's URLs."""

from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"incidents", views.IncidentViewSet)
router.register(
    r"aggincidents", views.AggregatedIncidentsViewSet, basename="aggincident"
)
router.register(
    r"autocomplete", views.AutocompleteViewSet, basename="autocomplete"
)

urlpatterns = [
    path("", include(router.urls)),
]

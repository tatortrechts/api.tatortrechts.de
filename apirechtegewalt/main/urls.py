"""The main application's URLs."""

from django.urls import include, path
from rest_framework import routers


from . import views

router = routers.DefaultRouter()
router.register(r"incidents", views.IncidentsViewSet, basename="incidents")
router.register(
    r"aggregated_incidents",
    views.AggregatedIncidentsViewSet,
    basename="aggregated_incidents",
)
router.register(r"autocomplete", views.AutocompleteViewSet, basename="autocomplete")
router.register(
    r"histogram_incidents",
    views.HistogramIncidentsViewSet,
    basename="histogram_incidents",
)
router.register(
    r"chronicles",
    views.ChroniclesViewSet,
    basename="chronicles",
)
router.register(
    r"locations",
    views.LocationViewSet,
    basename="locations",
)
router.register(r"min_max_date", views.MinMaxDateViewSet, basename="min_max_date")
router.register(
    r"chronicles_histogram",
    views.ChroniclesHistogramViewSet,
    basename="chronicles_histogram",
)

urlpatterns = [
    path("neuerfall/", views.IncidentSubmittedCreate.as_view()),
    path("fehler/", views.ErrorReportCase.as_view()),
    path("", include(router.urls)),
]

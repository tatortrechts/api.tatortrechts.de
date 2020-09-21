from django.contrib.gis.geos import Polygon
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from .models import Incident, Location, Phrase, Chronicle
from .serializers import (
    AggregatedIncidentsSerializer,
    AutocompleteSerializer,
    IncidentsSerializer,
    HistogramIncidentsSerializer,
    ChroniclesSerializer,
    LocationStringSerializer,
)


class IncidentFilter(filters.FilterSet):
    start_date = filters.DateFilter("date", "gt")
    end_date = filters.DateFilter("date", "lt")
    chronicle = filters.ModelMultipleChoiceFilter(queryset=Chronicle.objects.all())
    q = filters.CharFilter(method="search_fulltext")
    location = filters.CharFilter(field_name="location__id")

    def search_fulltext(self, queryset, field_name, value):
        return queryset.search(value, rank=False, prefix=True)

    class Meta:
        model = Incident
        fields = ["location", "start_date", "end_date"]


class AutocompleteIncidentFilter(IncidentFilter):
    def search_fulltext(self, queryset, field_name, value):
        return queryset.search(value, rank=False, prefix=True)


class CacheCountPaginator(Paginator):
    @cached_property
    def count(self):
        # only select 'id' for counting, much cheaper
        return self.object_list.values("id").count()


class SmallFastSetPagination(PageNumberPagination):
    django_paginator_class = CacheCountPaginator
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 10


class IncidentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects
    serializer_class = IncidentsSerializer
    filterset_class = IncidentFilter
    pagination_class = SmallFastSetPagination

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)

        bbox_list = self.request.GET.getlist("bbox")
        if len(bbox_list) != 0:
            bbox_geom = Polygon.from_bbox(bbox_list)

            # using geometry point to speed up computations
            queryset = queryset.select_related("location").filter(
                location__geolocation_geometry__intersects=bbox_geom
            )

        # TODO: order by rank?
        return queryset.order_by("-date")

    # cache for 10 minutes
    # @method_decorator(cache_page(60 * 10))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class HistogramIncidentsViewSet(IncidentsViewSet):
    serializer_class = HistogramIncidentsSerializer
    pagination_class = None

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return (
            queryset.annotate(month=TruncMonth("date"))
            .values("month")
            .order_by("month")
            .annotate(total=Count("month"))
        )


class AggregatedIncidentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects
    serializer_class = AggregatedIncidentsSerializer
    filterset_class = IncidentFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        # first apply django-filter
        queryset = super().filter_queryset(queryset)

        # queryset is based on Incident, but we need Location
        return Location.objects.annotate(
            total=Count("incident", filter=Q(incident__in=queryset))
        ).filter(total__gt=0)


class AutocompleteViewSet(viewsets.ReadOnlyModelViewSet):
    """Do prefix search on incidents because its about prefix. ;)
    Autocomplete should never be empty.
    """

    queryset = Incident.objects
    serializer_class = AutocompleteSerializer
    filterset_class = AutocompleteIncidentFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        # first apply django-filter
        queryset = super().filter_queryset(queryset)
        search_term = self.request.query_params.get("q")
        suggestions = (
            Phrase.objects.search(search_term).filter(incident__in=queryset).distinct()
        )
        return sorted(suggestions[:10], key=lambda x: len(x.option))


class ChroniclesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chronicle.objects.all()
    serializer_class = ChroniclesSerializer
    pagination_class = None


class LocationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects
    serializer_class = LocationStringSerializer
    filterset_class = IncidentFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        search_term = self.request.query_params.get("q_location")

        rs_qs = Location.objects
        if search_term is not None:
            rs_qs = rs_qs.search(search_term)

        # queryset is based on Incident, but we need Location
        return (
            rs_qs.filter(incident__in=queryset)
            .annotate(total=Count("id"))
            .order_by("-total")
        )[:10]

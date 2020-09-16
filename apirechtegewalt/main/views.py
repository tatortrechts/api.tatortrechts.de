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
)


class IncidentFilter(filters.FilterSet):
    start_date = filters.DateFilter("date", "gt")
    end_date = filters.DateFilter("date", "lt")
    chronicle = filters.ModelMultipleChoiceFilter(queryset=Chronicle.objects.all())

    class Meta:
        model = Incident
        fields = ["location", "start_date", "end_date"]


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

        # not using DRF search filter to have more control over the query
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            queryset = queryset.search(search_term, rank=False)

        bbox_list = self.request.GET.getlist("bbox")
        if len(bbox_list) != 0:
            bbox_geom = Polygon.from_bbox(bbox_list)

            # using geometry point to speed up computations
            queryset = queryset.select_related("location").filter(
                location__geolocation_geometry__intersects=bbox_geom
            )

        return queryset.order_by("-date")

    # cache for 10 minutes
    @method_decorator(cache_page(60 * 10))
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
    queryset = Incident.objects.all()
    serializer_class = AggregatedIncidentsSerializer
    filterset_class = IncidentFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        # first apply django-filter
        queryset = super().filter_queryset(queryset)

        # not using DRF search filter to have more control over the query
        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            queryset = queryset.search(search_term, rank=False)

        # queryset is based on Incident, but we need Location
        return Location.objects.annotate(
            total=Count("incident", filter=Q(incident__in=queryset))
        ).filter(total__gt=0)


# Todo: BBOX ETC
class AutocompleteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = AutocompleteSerializer
    filterset_class = IncidentFilter

    def filter_queryset(self, queryset):
        # first apply django-filter
        queryset = super().filter_queryset(queryset)
        search_term = self.request.query_params.get("q", "")
        suggestions = Phrase.objects.search(search_term)[:10]
        return sorted(suggestions, key=lambda x: len(x.option))


class ChroniclesViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Chronicle.objects.all()
    serializer_class = ChroniclesSerializer
    pagination_class = None


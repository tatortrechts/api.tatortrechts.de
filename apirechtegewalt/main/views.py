from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets

from .models import Incident, Location, Phrase
from .serializers import (
    AggregatedIncidentsSerializer,
    AutocompleteSerializer,
    IncidentSerializer,
)


class IncidentFilter(filters.FilterSet):
    start_date = filters.DateFilter("date", "gt")
    end_date = filters.DateFilter("date", "lt")
    aggregator = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Incident
        fields = ["aggregator", "location", "start_date", "end_date"]


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Incident.objects.all().order_by("-date")
    serializer_class = IncidentSerializer


class AggregatedIncidentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = AggregatedIncidentsSerializer
    filterset_class = IncidentFilter

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


class AutocompleteViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = AutocompleteSerializer
    filterset_class = IncidentFilter

    def filter_queryset(self, queryset):
        # first apply django-filter
        queryset = super().filter_queryset(queryset)

        search_term = self.request.query_params.get("q", "")

        suggestions = Phrase.objects.search(search_term)[:10]

        return sorted(suggestions, key=lambda x: len(x.string))

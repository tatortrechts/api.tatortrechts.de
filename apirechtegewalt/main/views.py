from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django_filters import rest_framework as filters
from rest_framework import viewsets
from watson import search as watson

from .models import Incident, Location
from .serializers import AggregatedIncidentsSerializer, IncidentSerializer


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

        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            search_results = watson.filter(Incident, search_term)
            queryset = queryset & search_results

        # queryset is based on Incident, but we need Location
        return Location.objects.annotate(
            total=Count("incident", filter=Q(incident__in=queryset))
        ).filter(total__gt=0)

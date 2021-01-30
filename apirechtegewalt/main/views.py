from django.contrib.gis.geos import Polygon
from django.core.paginator import Paginator
from django.db.models import Count, Q, Value
from django.db.models.fields import CharField
from django.db.models.functions import (
    TruncDay,
    TruncMonth,
    TruncQuarter,
    TruncWeek,
    TruncYear,
)
from django.utils.decorators import method_decorator
from django.utils.functional import cached_property
from django.views.decorators.cache import cache_page
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from .models import (
    Chronicle,
    ErrorReport,
    Incident,
    IncidentSubmitted,
    Location,
    Phrase,
)
from .serializers import (
    AggregatedIncidentsSerializer,
    AutocompleteSerializer,
    ChroniclesSerializer,
    HistogramIncidentsSerializer,
    IncidentsSerializer,
    LocationStringSerializer,
)


class IncidentFilter(filters.FilterSet):
    start_date = filters.DateFilter("date", "gt")
    end_date = filters.DateFilter("date", "lt")
    chronicle = filters.ModelMultipleChoiceFilter(queryset=Chronicle.objects.all())
    q = filters.CharFilter(method="search_fulltext")
    location = filters.CharFilter(field_name="location__id")
    rg_id = filters.CharFilter(field_name="rg_id")

    def search_fulltext(self, queryset, field_name, value):
        return queryset.search(value)

    class Meta:
        model = Incident
        fields = ["location", "start_date", "end_date", "rg_id"]


class AutocompleteIncidentFilter(IncidentFilter):
    # force prefix search
    def search_fulltext(self, queryset, field_name, value):
        return queryset.search(value)


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
    @method_decorator(cache_page(60 * 10))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class HistogramIncidentsViewSet(IncidentsViewSet):
    serializer_class = HistogramIncidentsSerializer
    pagination_class = None

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        num_results = queryset.count()

        if num_results == 0:
            return queryset

        early = queryset.earliest("date").date
        latest = queryset.latest("date").date
        time_diff = latest - early

        if num_results > 5000:
            return (
                queryset.annotate(date_histogram=TruncYear("date"))
                .values("date_histogram")
                .order_by("date_histogram")
                .annotate(
                    total=Count("date_histogram"),
                    time_interval=Value("year", CharField()),
                )
            )

        if num_results > 1000 or time_diff.days > 5 * 365:
            return (
                queryset.annotate(date_histogram=TruncQuarter("date"))
                .values("date_histogram")
                .order_by("date_histogram")
                .annotate(
                    total=Count("date_histogram"),
                    time_interval=Value("quarter", CharField()),
                )
            )

        if time_diff.days > 365:
            return (
                queryset.annotate(date_histogram=TruncMonth("date"))
                .values("date_histogram")
                .order_by("date_histogram")
                .annotate(
                    total=Count("date_histogram"),
                    time_interval=Value("month", CharField()),
                )
            )

        if time_diff.days > 90:
            return (
                queryset.annotate(date_histogram=TruncWeek("date"))
                .values("date_histogram")
                .order_by("date_histogram")
                .annotate(
                    total=Count("date_histogram"),
                    time_interval=Value("week", CharField()),
                )
            )

        return (
            queryset.annotate(date_histogram=TruncDay("date"))
            .values("date_histogram")
            .order_by("date_histogram")
            .annotate(
                total=Count("date_histogram"), time_interval=Value("day", CharField())
            )
        )


class AggregatedIncidentsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Incident.objects
    serializer_class = AggregatedIncidentsSerializer
    filterset_class = IncidentFilter
    pagination_class = None

    def filter_queryset(self, queryset):
        # first apply django-filter
        queryset_ids = super().filter_queryset(queryset).values("id")

        # queryset is based on Incident, but we need Location
        return Location.objects.annotate(
            total=Count("incident", filter=Q(incident__in=queryset_ids))
        ).filter(total__gt=0)

    # cache for 10 minutes
    @method_decorator(cache_page(60 * 10))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


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
            Phrase.objects.search(search_term)
            .filter(incident__in=queryset)
            .distinct()
            .order_by("-count")[:10]
        )
        # order the 10 best matching for lenght of sentence
        return sorted(suggestions[:10], key=lambda x: len(x.option))

    # cache for 10 minutes
    @method_decorator(cache_page(60 * 10))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


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

    # cache for 10 minutes
    @method_decorator(cache_page(60 * 10))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class MinMaxDateViewSet(viewsets.ViewSet):
    def list(self, response):
        min_date = Incident.objects.earliest("date").date
        max_date = Incident.objects.latest("date").date
        total = Incident.objects.count()
        return Response({"min_date": min_date, "max_date": max_date, "total": total})


# non-api views

from django.views.generic.edit import CreateView
from django.forms import DateInput
from django.utils.crypto import get_random_string
from django.contrib.messages.views import SuccessMessageMixin


class IncidentSubmittedCreate(SuccessMessageMixin, CreateView):
    model = IncidentSubmitted

    fields = [
        "title",
        "description",
        "date",
        "sources_input",
        "location_input",
        "contexts",
        "motives",
        "factums",
        "tags",
    ]

    success_url = "/neu/"
    success_message = "Danke für den Eintrag. Wir prüfen ihn und stellen ihn danach online. Du kannst untere weitere hinzufügen."

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["date"].widget = DateInput(
            attrs={"class": "form-control", "type": "date"}
        )
        return form

    def form_valid(self, form):
        form.instance.rg_id = "tatortrechts-" + get_random_string(length=50)
        return super().form_valid(form)


from base64 import b64decode


class ErrorReportCase(SuccessMessageMixin, CreateView):
    model = ErrorReport

    fields = [
        "description",
    ]

    success_url = "/fehler/"
    success_message = "Danke für deine Meldung. Wir werden sie zeitnah bearbeiten."

    def form_valid(self, form):
        if "rg_id" in self.request.GET:
            rg_id = self.request.GET["rg_id"]
            rg_id = b64decode(rg_id).decode("utf-8", "ignore")
        else:
            rg_id = "keine Angabe"

        form.instance.rg_id = rg_id
        return super().form_valid(form)

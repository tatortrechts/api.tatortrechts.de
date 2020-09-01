from django.db.models import Count
from django.shortcuts import get_object_or_404
from rest_framework import permissions, viewsets
from rest_framework.response import Response
from watson import search as watson

from .models import Incident, Location
from .serializers import AggregatedIncidentsSerializer, IncidentSerializer


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Incident.objects.all().order_by("-date")
    serializer_class = IncidentSerializer
    # permission_classes = [permissions.IsAuthenticated]


class AggregatedIncidentsViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = AggregatedIncidentsSerializer

    def get_queryset(self):
        qs = Location.objects

        search_term = self.request.query_params.get("q", None)
        if search_term is not None:
            search_results = watson.filter(Incident, search_term)
            qs = qs.filter(incident__in=search_results)

        return qs.annotate(total=Count("incident")).order_by("-total")


# class AggregatedIncidentsViewSet(viewsets.ViewSet):
#     """
#     A simple ViewSet for listing or retrieving users.
#     """

#     def list(self, request):
#         queryset = (
#             Incident.objects.all()
#             .values("location", "total")
#             .annotate(total=Count("location"))
#             # .order_by("total")
#         )

#         serializer = AggregatedIncidentsSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def retrieve(self, request, pk=None):
#         queryset = Incident.objects.filter(location=pk)
#         location = get_object_or_404(queryset, pk=pk)
#         serializer = IncidentSerializer(location)
#         return Response(serializer.data)

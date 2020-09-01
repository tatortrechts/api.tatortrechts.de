from .models import Incident
from .serializers import IncidentSerializer
from rest_framework import permissions, viewsets


class IncidentViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = Incident.objects.all().order_by("-date")
    serializer_class = IncidentSerializer
    # permission_classes = [permissions.IsAuthenticated]


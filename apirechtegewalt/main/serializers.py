from .models import Incident, Location, Source
from rest_framework import serializers


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = "__all__"


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class IncidentSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    sources = SourceSerializer(source="source_set", many=True, read_only=True)

    class Meta:
        model = Incident
        fields = "__all__"


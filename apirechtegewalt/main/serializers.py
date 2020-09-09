from .models import Incident, Location, Source
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "subdivisions"]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class IncidentSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    sources = SourceSerializer(source="source_set", many=True, read_only=True)

    class Meta:
        model = Incident
        exclude = ["search_vector"]


class AggregatedIncidentsSerializer(GeoFeatureModelSerializer):
    total = serializers.IntegerField()

    class Meta:
        model = Location
        fields = ["id", "geolocation", "total"]
        geo_field = "geolocation"


class AutocompleteSerializer(serializers.Serializer):
    string = serializers.CharField()

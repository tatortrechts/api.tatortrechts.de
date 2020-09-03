from .models import Incident, Location, Source
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer


class LocationSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "subdivisions", "geolocation"]
        geo_field = "geolocation"


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


class AggregatedIncidentsSerializer(GeoFeatureModelSerializer):
    total = serializers.IntegerField()

    class Meta:
        model = Location
        fields = ["id", "subdivisions", "geolocation", "total"]
        geo_field = "geolocation"


class AutocompleteSerializer(serializers.Serializer):
    string = serializers.CharField()

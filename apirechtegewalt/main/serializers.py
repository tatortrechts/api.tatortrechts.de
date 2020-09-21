from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Incident, Location, Source, Chronicle


class ChroniclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chronicle
        fields = ["id", "name", "region"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "location_string", "subdivisions"]

class LocationStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["location_string"]

class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class IncidentsSerializer(serializers.ModelSerializer):
    location = LocationSerializer(read_only=True)
    chronicle = ChroniclesSerializer(read_only=True)
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
    option = serializers.CharField()


class HistogramIncidentsSerializer(serializers.Serializer):
    month = serializers.DateField()
    total = serializers.IntegerField()


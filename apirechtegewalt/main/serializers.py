from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from .models import Chronicle, Incident, Location, Source


class ChroniclesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Chronicle
        fields = ["id", "name", "region"]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "location_string"] + [
            "house_number",
            "street",
            "postal_code",
            "district",
            "city",
            "county",
            "state",
            "country",
            "geolocation",
        ]


class LocationStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = ["id", "location_string"]


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
        exclude = ["search_vector", "phrases"]


class AggregatedIncidentsSerializer(GeoFeatureModelSerializer):
    total = serializers.IntegerField()

    class Meta:
        model = Location
        fields = [
            "id",
            "geolocation",
            "total",
            "house_number",
            "street",
            "district",
            "city",
            "county",
        ]
        geo_field = "geolocation"


class AutocompleteSerializer(serializers.Serializer):
    option = serializers.CharField()


class HistogramIncidentsSerializer(serializers.Serializer):
    date_histogram = serializers.DateField()
    time_interval = serializers.CharField()
    total = serializers.IntegerField()

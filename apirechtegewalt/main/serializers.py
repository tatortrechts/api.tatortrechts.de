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
        fields = [
            "id",
            "house_number",
            "street",
            "postal_code",
            "district",
            "city",
            "county",
            "state",
            "geolocation",
        ]


class LocationStringSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "house_number",
            "street",
            "postal_code",
            "district",
            "city",
            "county",
        ]


class SourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Source
        fields = "__all__"


class IncidentsSerializer(serializers.ModelSerializer):
    description_highlighted = serializers.CharField(allow_null=True, required=False)
    title_highlighted = serializers.CharField(allow_null=True, required=False)
    location = LocationSerializer(read_only=True)
    chronicle = ChroniclesSerializer(read_only=True)
    sources = SourceSerializer(source="source_set", many=True, read_only=True)

    class Meta:
        model = Incident
        exclude = ["search_vector", "phrases"]

    def __init__(self, *args, **kwargs):
        # when searching, only return highlighted results
        request = kwargs.get("context", {}).get("request")
        is_searching = request.GET.get("q", None) if request else None

        super(IncidentsSerializer, self).__init__(*args, **kwargs)

        if is_searching:
            self.fields.pop("description")
            self.fields.pop("title")


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

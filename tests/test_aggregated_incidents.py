import pytest
from django.urls import reverse


class TestAggregatedIncidents:
    def test_returns_200(self, api_client, all_incidents):
        response = api_client.get(reverse("aggregated_incidents-list"))
        assert response.status_code == 200

    def test_geojson_structure(self, api_client, all_incidents):
        response = api_client.get(reverse("aggregated_incidents-list"))
        data = response.json()
        assert data["type"] == "FeatureCollection"
        assert "features" in data

    def test_feature_properties(self, api_client, all_incidents):
        response = api_client.get(reverse("aggregated_incidents-list"))
        features = response.json()["features"]
        assert len(features) == 3  # Berlin, Dresden, Munich
        for feature in features:
            assert feature["type"] == "Feature"
            assert feature["geometry"]["type"] == "Point"
            assert "total" in feature["properties"]

    def test_berlin_location_has_correct_total(self, api_client, all_incidents):
        response = api_client.get(reverse("aggregated_incidents-list"))
        features = response.json()["features"]
        berlin = next(
            f for f in features if f["properties"].get("city") == "Berlin"
        )
        assert berlin["properties"]["total"] == 2

    def test_filter_by_chronicle(self, api_client, all_incidents, chronicle_sachsen):
        response = api_client.get(
            reverse("aggregated_incidents-list"), {"chronicle": chronicle_sachsen.pk}
        )
        features = response.json()["features"]
        assert len(features) == 1
        assert features[0]["properties"]["city"] == "Dresden"

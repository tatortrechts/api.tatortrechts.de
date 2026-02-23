import pytest
from django.urls import reverse


class TestLocations:
    def test_returns_200(self, api_client, all_incidents):
        response = api_client.get(reverse("locations-list"))
        assert response.status_code == 200

    def test_response_is_list(self, api_client, all_incidents):
        data = api_client.get(reverse("locations-list")).json()
        assert isinstance(data, list)

    def test_max_10_results(self, api_client, all_incidents):
        data = api_client.get(reverse("locations-list")).json()
        assert len(data) <= 10

    def test_result_has_expected_fields(self, api_client, all_incidents):
        data = api_client.get(reverse("locations-list")).json()
        assert len(data) > 0
        # LocationViewSet returns .values() dicts, not serialized models
        item = data[0]
        for field in ["city", "county", "district", "geolocation"]:
            assert field in item

    def test_search_by_q_location(self, api_client, search_synced_incidents):
        response = api_client.get(
            reverse("locations-list"), {"q_location": "Berlin"}
        )
        data = response.json()
        assert len(data) >= 1
        assert any(item["city"] == "Berlin" for item in data)

    def test_ordered_by_incident_count_desc(self, api_client, all_incidents):
        data = api_client.get(reverse("locations-list")).json()
        # Berlin has 2 incidents, should be first
        assert data[0]["city"] == "Berlin"

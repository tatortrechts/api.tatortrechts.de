import pytest
from django.urls import reverse


class TestChroniclesHistogram:
    def test_returns_200(self, api_client, all_incidents):
        response = api_client.get(reverse("chronicles_histogram-list"))
        assert response.status_code == 200

    def test_response_structure(self, api_client, all_incidents):
        data = api_client.get(reverse("chronicles_histogram-list")).json()
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_result_item_structure(self, api_client, all_incidents):
        items = api_client.get(reverse("chronicles_histogram-list")).json()["result"]
        assert len(items) > 0
        for item in items:
            assert "chronicle" in item
            assert "year" in item
            assert "total" in item

    def test_totals_sum_to_incident_count(self, api_client, all_incidents):
        items = api_client.get(reverse("chronicles_histogram-list")).json()["result"]
        total = sum(item["total"] for item in items)
        assert total == 4

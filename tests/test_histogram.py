import pytest
from django.urls import reverse


class TestHistogramIncidents:
    def test_returns_200(self, api_client, all_incidents):
        response = api_client.get(reverse("histogram_incidents-list"))
        assert response.status_code == 200

    def test_response_is_list(self, api_client, all_incidents):
        data = api_client.get(reverse("histogram_incidents-list")).json()
        assert isinstance(data, list)

    def test_result_structure(self, api_client, all_incidents):
        data = api_client.get(reverse("histogram_incidents-list")).json()
        assert len(data) > 0
        for item in data:
            assert "date_histogram" in item
            assert "time_interval" in item
            assert "total" in item

    def test_totals_sum_to_incident_count(self, api_client, all_incidents):
        data = api_client.get(reverse("histogram_incidents-list")).json()
        total = sum(item["total"] for item in data)
        assert total == 4

    def test_filter_narrows_histogram(self, api_client, all_incidents, chronicle_sachsen):
        response = api_client.get(
            reverse("histogram_incidents-list"), {"chronicle": chronicle_sachsen.pk}
        )
        total = sum(item["total"] for item in response.json())
        assert total == 1

    def test_consistent_time_interval(self, api_client, all_incidents):
        data = api_client.get(reverse("histogram_incidents-list")).json()
        intervals = {item["time_interval"] for item in data}
        assert len(intervals) == 1
        assert intervals.pop() in ("day", "week", "month", "quarter", "year")

    def test_empty_result_returns_empty_list(self, api_client, all_incidents):
        response = api_client.get(
            reverse("histogram_incidents-list"), {"start_date": "2099-01-01"}
        )
        assert response.json() == []

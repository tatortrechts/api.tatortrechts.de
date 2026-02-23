import pytest
from django.urls import reverse


class TestIncidentsList:
    def test_list_returns_200(self, api_client, all_incidents):
        response = api_client.get(reverse("incidents-list"))
        assert response.status_code == 200

    def test_list_response_structure(self, api_client, all_incidents):
        response = api_client.get(reverse("incidents-list"))
        data = response.json()
        assert "count" in data
        assert "results" in data
        assert "next" in data
        assert "previous" in data
        assert data["count"] == 4

    def test_list_result_fields(self, api_client, all_incidents, source_for_berlin):
        response = api_client.get(reverse("incidents-list"))
        item = response.json()["results"][0]
        for field in [
            "id",
            "rg_id",
            "url",
            "title",
            "description",
            "date",
            "location",
            "chronicle",
            "sources",
            "contexts",
            "factums",
            "motives",
            "tags",
        ]:
            assert field in item, f"Missing field: {field}"
        assert "city" in item["location"]
        assert "name" in item["chronicle"]

    def test_list_ordered_by_date_desc(self, api_client, all_incidents):
        response = api_client.get(reverse("incidents-list"))
        dates = [r["date"] for r in response.json()["results"]]
        assert dates == sorted(dates, reverse=True)


class TestIncidentsDetail:
    def test_detail_returns_200(self, api_client, incident_berlin):
        response = api_client.get(
            reverse("incidents-detail", args=[incident_berlin.pk])
        )
        assert response.status_code == 200

    def test_detail_returns_correct_incident(self, api_client, incident_berlin):
        response = api_client.get(
            reverse("incidents-detail", args=[incident_berlin.pk])
        )
        assert response.json()["rg_id"] == "berlin-001"

    def test_detail_404_for_nonexistent(self, api_client, db):
        response = api_client.get(reverse("incidents-detail", args=[99999]))
        assert response.status_code == 404


class TestIncidentsFilterDate:
    def test_filter_start_date(self, api_client, all_incidents):
        response = api_client.get(
            reverse("incidents-list"), {"start_date": "2023-01-01"}
        )
        # Incidents after 2023-01-01 (gt): berlin (Jun), berlin_2 (Sep), munich (Jan 5)
        assert response.json()["count"] == 3

    def test_filter_end_date(self, api_client, all_incidents):
        response = api_client.get(
            reverse("incidents-list"), {"end_date": "2023-01-01"}
        )
        # Incidents before 2023-01-01 (lt): dresden (2022-03-10)
        assert response.json()["count"] == 1

    def test_filter_date_range(self, api_client, all_incidents):
        response = api_client.get(
            reverse("incidents-list"),
            {"start_date": "2023-01-01", "end_date": "2023-07-01"},
        )
        # Between Jan 1 and Jul 1: berlin (Jun 15) and munich (Jan 5)
        assert response.json()["count"] == 2


class TestIncidentsFilterChronicle:
    def test_filter_by_single_chronicle(self, api_client, all_incidents, chronicle_sachsen):
        response = api_client.get(
            reverse("incidents-list"), {"chronicle": chronicle_sachsen.pk}
        )
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["rg_id"] == "dresden-001"

    def test_filter_by_multiple_chronicles(
        self, api_client, all_incidents, chronicle_berlin, chronicle_sachsen
    ):
        url = reverse("incidents-list")
        response = api_client.get(
            f"{url}?chronicle={chronicle_berlin.pk}&chronicle={chronicle_sachsen.pk}"
        )
        assert response.json()["count"] == 4


class TestIncidentsFilterLocation:
    def test_filter_by_location(self, api_client, all_incidents, location_berlin):
        response = api_client.get(
            reverse("incidents-list"), {"location": location_berlin.pk}
        )
        assert response.json()["count"] == 2


class TestIncidentsFilterRgId:
    def test_filter_by_rg_id(self, api_client, all_incidents):
        response = api_client.get(
            reverse("incidents-list"), {"rg_id": "berlin-001"}
        )
        data = response.json()
        assert data["count"] == 1
        assert data["results"][0]["rg_id"] == "berlin-001"


class TestIncidentsFilterBbox:
    def test_bbox_includes_berlin_and_dresden(self, api_client, all_incidents):
        url = reverse("incidents-list")
        # Berlin: 13.38, 52.52  Dresden: 13.74, 51.05  Munich: 11.58, 48.14
        response = api_client.get(f"{url}?bbox=13.0&bbox=50.5&bbox=14.0&bbox=53.0")
        assert response.json()["count"] == 3  # 2 Berlin + 1 Dresden

    def test_bbox_excludes_all(self, api_client, all_incidents):
        url = reverse("incidents-list")
        response = api_client.get(f"{url}?bbox=0.0&bbox=0.0&bbox=1.0&bbox=1.0")
        assert response.json()["count"] == 0


class TestIncidentsSearch:
    def test_search_returns_matching(self, api_client, search_synced_incidents):
        response = api_client.get(reverse("incidents-list"), {"q": "Angriff"})
        assert response.json()["count"] >= 1

    def test_search_no_results(self, api_client, search_synced_incidents):
        response = api_client.get(reverse("incidents-list"), {"q": "xyznonexistent"})
        assert response.json()["count"] == 0

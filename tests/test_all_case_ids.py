import pytest
from django.urls import reverse


class TestAllCaseIds:
    def test_returns_200(self, api_client, all_incidents):
        response = api_client.get(reverse("all_case_ids-list"))
        assert response.status_code == 200

    def test_response_structure(self, api_client, all_incidents):
        data = api_client.get(reverse("all_case_ids-list")).json()
        assert "result" in data
        assert isinstance(data["result"], list)

    def test_returns_all_ids(self, api_client, all_incidents):
        ids = api_client.get(reverse("all_case_ids-list")).json()["result"]
        assert len(ids) == 4

    def test_ids_are_integers(self, api_client, all_incidents):
        ids = api_client.get(reverse("all_case_ids-list")).json()["result"]
        assert all(isinstance(i, int) for i in ids)

    def test_empty_db_returns_empty_list(self, api_client, db):
        ids = api_client.get(reverse("all_case_ids-list")).json()["result"]
        assert ids == []

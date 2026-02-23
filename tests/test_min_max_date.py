import pytest
from django.urls import reverse


class TestMinMaxDate:
    def test_returns_200(self, api_client, all_incidents):
        response = api_client.get(reverse("min_max_date-list"))
        assert response.status_code == 200

    def test_response_structure(self, api_client, all_incidents):
        data = api_client.get(reverse("min_max_date-list")).json()
        assert "min_date" in data
        assert "max_date" in data
        assert "total" in data

    def test_correct_values(self, api_client, all_incidents):
        data = api_client.get(reverse("min_max_date-list")).json()
        assert data["min_date"] == "2022-03-10"  # dresden
        assert data["max_date"] == "2023-09-20"  # berlin_2
        assert data["total"] == 4

    def test_empty_db_raises(self, api_client, db):
        # MinMaxDateViewSet calls .earliest() without try/except
        from apirechtegewalt.main.models import Incident

        with pytest.raises(Incident.DoesNotExist):
            api_client.get(reverse("min_max_date-list"))

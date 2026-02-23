import pytest
from django.urls import reverse


class TestChronicles:
    def test_returns_200(self, api_client, chronicle_berlin):
        response = api_client.get(reverse("chronicles-list"))
        assert response.status_code == 200

    def test_response_is_list(self, api_client, chronicle_berlin, chronicle_sachsen):
        data = api_client.get(reverse("chronicles-list")).json()
        assert isinstance(data, list)
        assert len(data) == 2

    def test_chronicle_fields(self, api_client, chronicle_berlin):
        item = api_client.get(reverse("chronicles-list")).json()[0]
        for field in [
            "id", "name", "description", "url", "chronicle_source",
            "iso3166_1", "iso3166_2", "region",
        ]:
            assert field in item

    def test_detail_returns_200(self, api_client, chronicle_berlin):
        response = api_client.get(
            reverse("chronicles-detail", args=[chronicle_berlin.pk])
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Berliner Register"

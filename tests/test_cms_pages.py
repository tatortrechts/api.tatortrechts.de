import pytest


class TestCMSPages:
    def test_returns_200(self, api_client, db):
        response = api_client.get("/content/api/v2/pages/")
        assert response.status_code == 200

    def test_response_structure(self, api_client, db):
        data = api_client.get("/content/api/v2/pages/").json()
        assert "meta" in data
        assert "items" in data

    def test_empty_without_published_pages(self, api_client, db):
        data = api_client.get("/content/api/v2/pages/").json()
        assert data["items"] == []

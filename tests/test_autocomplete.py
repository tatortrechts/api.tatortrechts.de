import pytest
from django.urls import reverse


class TestAutocomplete:
    def test_returns_200(self, api_client, search_synced_incidents):
        response = api_client.get(reverse("autocomplete-list"), {"q": "Angriff"})
        assert response.status_code == 200

    def test_response_is_list(self, api_client, search_synced_incidents):
        response = api_client.get(reverse("autocomplete-list"), {"q": "Angriff"})
        data = response.json()
        assert isinstance(data, list)

    def test_result_has_option_field(self, api_client, search_synced_incidents):
        response = api_client.get(reverse("autocomplete-list"), {"q": "Angriff"})
        data = response.json()
        if len(data) > 0:
            assert "option" in data[0]

    def test_max_10_results(self, api_client, search_synced_incidents):
        response = api_client.get(reverse("autocomplete-list"), {"q": "A"})
        assert len(response.json()) <= 10

    def test_results_sorted_by_length(self, api_client, search_synced_incidents):
        response = api_client.get(reverse("autocomplete-list"), {"q": "A"})
        data = response.json()
        if len(data) > 1:
            lengths = [len(item["option"]) for item in data]
            assert lengths == sorted(lengths)

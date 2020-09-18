from django.contrib.gis.db import models
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
    TrigramSimilarity,
    SearchRank,
)
from django.db.models import F
from django.utils.text import smart_split


class SearchQuerySet(models.QuerySet):
    def search(self, search_text, rank=True, prefix=False):
        if prefix:
            # prepend wildcard to all tokens
            search_text = " & ".join([x + ":*" for x in smart_split(search_text)])
            search_query = SearchQuery(search_text, config="german", search_type="raw")
        else:
            search_query = SearchQuery(
                search_text, config="german", search_type="websearch"
            )

        qs = self.filter(search_vector=search_query)

        if rank:
            qs = qs.annotate(
                rank=SearchRank(F("search_vector"), search_query)
            ).order_by("-rank")
        return qs

    # can't use trigram because of the postgis image
    def trigram(self, search_text, threshold=0.3):
        return (
            self.annotate(similarity=TrigramSimilarity("search_vector", search_text))
            .filter(similarity__gt=threshold)
            .order_by("-similarity")
        )


class IncidentSearchQuerySet(SearchQuerySet):
    def sync(self):
        self.update(
            search_vector=SearchVector("title", weight="A", config="german")
            + SearchVector("description", weight="B", config="german")
        )


class PhrasesQuerySet(SearchQuerySet):
    def search(self, search_text):
        return super().search(search_text, rank=True, prefix=True)

    def sync(self):
        self.update(search_vector=SearchVector("option", config="german"))


class LocationSearchQuerySet(SearchQuerySet):
    def search(self, search_text):
        return super().search(search_text, rank=False, prefix=True)

    def sync(self):
        self.update(search_vector=SearchVector("location_string", config="german"))

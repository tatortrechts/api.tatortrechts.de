from django.contrib.gis.db import models
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db.models import F
from django.utils.text import smart_split


class SearchQuerySet(models.QuerySet):
    def search(self, search_text, rank=True, prefix=False, prefix_and=True):

        implicit_prefix = "*" in search_text
        # force prefix search if
        if prefix or implicit_prefix:
            conj = " & " if prefix_and else " | "

            if prefix:
                # prepend wildcard to all tokens
                search_text = conj.join(
                    [x + ":*" for x in smart_split(search_text.replace("*", ""))]
                )
            elif implicit_prefix:
                search_text = conj.join(
                    [x.replace('*', ':*') for x in smart_split(search_text)]
                )

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

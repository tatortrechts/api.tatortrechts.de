from django.contrib.gis.db import models
from django.contrib.postgres.search import (
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db.models import F
from django.utils.text import smart_split

from cleantext import clean


def split_proximity(text):
    text = text.replace("*", "").replace(":", "").replace("'", '"')
    tokens = smart_split(text)

    for t in tokens:
        t_cl = clean(t, lang="de", lower=False, no_punct=False)
        t_cl_p = clean(t, lang="de", lower=False, no_punct=True)

        if t_cl.lower() == "or":
            continue
        if " " in t or '"' in t_cl:
            yield "' " + t_cl_p.replace(" ", " <-> ") + " '"
        else:
            yield t_cl_p + ":*"


class SearchQuerySet(models.QuerySet):
    def search(
        self,
        search_text,
        rank=True,
        prefix=True,
    ):
        if prefix:
            conj = " & " if not " or " in search_text.lower() else " | "

            # prepend wildcard to all tokens
            search_text = conj.join(split_proximity(search_text))
            print(search_text)

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
    def sync(self):
        self.update(search_vector=SearchVector("option", config="german"))


class LocationSearchQuerySet(SearchQuerySet):
    def sync(self):
        self.update(search_vector=SearchVector("location_string", config="german"))

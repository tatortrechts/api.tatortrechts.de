from cleantext import clean
from django.contrib.gis.db import models
from django.contrib.postgres.search import (
    SearchHeadline,
    SearchQuery,
    SearchRank,
    SearchVector,
    TrigramSimilarity,
)
from django.db.models import F
from django.utils.text import smart_split


def split_proximity(text):
    # TODO: add not / - option
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
        self, search_text, rank=True, prefix=True, highlight=False, force_or=False
    ):
        if search_text is None:
            return self

        if prefix:
            if force_or:
                conj = " | "
            else:
                conj = " & " if not " or " in search_text.lower() else " | "
            search_text = conj.join(split_proximity(search_text))
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

        if highlight:
            qs = qs.annotate(
                description_highlighted=SearchHeadline(
                    "description", search_query, config="german", highlight_all=True
                ),
                title_highlighted=SearchHeadline(
                    "title", search_query, config="german", highlight_all=True
                ),
            )

        return qs

    # can't use trigram because of the postgis image
    def trigram(self, search_text, threshold=0.3):
        return (
            self.annotate(similarity=TrigramSimilarity("search_vector", search_text))
            .filter(similarity__gt=threshold)
            .order_by("-similarity")
        )


class IncidentSearchQuerySet(SearchQuerySet):
    def search(self, search_text):
        return super().search(search_text, highlight=True)

    def sync(self):
        self.update(
            search_vector=SearchVector("title", weight="A", config="german")
            + SearchVector("description", weight="B", config="german")
            + SearchVector("tags", weight="C", config="german")
            + SearchVector("factums", weight="C", config="german")
            + SearchVector("motives", weight="C", config="german")
            + SearchVector("contexts", weight="C", config="german")
        )


class PhrasesQuerySet(SearchQuerySet):
    def sync(self):
        self.update(search_vector=SearchVector("option", config="german"))


class LocationSearchQuerySet(SearchQuerySet):
    def search(self, search_text):
        return super().search(
            search_text,
            force_or=True,
        )

    def sync(self):
        self.update(
            search_vector=SearchVector("city", weight="A", config="german")
            + SearchVector("county", weight="B", config="german")
            + SearchVector("district", weight="B", config="german")
        )

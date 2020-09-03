from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.search import (
    SearchQuery,
    SearchVector,
    SearchVectorField,
    TrigramSimilarity,
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
                rank=SearchQuery(F("search_vector"), search_query)
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
        return super().search(search_text, rank=False, prefix=True)

    def sync(self):
        self.update(search_vector=SearchVector("string", config="german"))


# can't edit in Admin https://stackoverflow.com/a/1737078/4028896 because of
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser):
    pass


class Location(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subdivisions = models.CharField(max_length=255, db_index=True, unique=True)
    geolocation = models.PointField(geography=True, default=Point(0.0, 0.0))


class Incident(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255)
    aggregator = models.CharField(max_length=255)
    title = models.CharField(max_length=1000, blank=True, default="", null=True)
    description = models.TextField()
    date = models.DateField()
    iso3166_2 = models.CharField(max_length=5)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    search_vector = SearchVectorField(null=True)

    objects = IncidentSearchQuerySet.as_manager()


class Source(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, default="")
    date = models.DateField(blank=True, null=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, default=None)


class Phrase(models.Model):
    string = models.TextField(primary_key=True)
    count = models.IntegerField(default=0)
    search_vector = SearchVectorField(null=True)

    objects = PhrasesQuerySet.as_manager()

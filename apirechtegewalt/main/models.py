from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField

from .search import IncidentSearchQuerySet, PhrasesQuerySet

# can't edit in Admin https://stackoverflow.com/a/1737078/4028896 because of
#    created_at = models.DateTimeField(auto_now_add=True)
#    updated_at = models.DateTimeField(auto_now=True)


class User(AbstractUser):
    pass


class Chronicle(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    url = models.CharField(max_length=255)
    chronicle_source = models.CharField(max_length=255)
    iso3166_1 = models.CharField(max_length=2, blank=True, null=True)
    iso3166_2 = models.CharField(max_length=5, blank=True, null=True)
    region = models.CharField(max_length=255)


class Location(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subdivisions = ArrayField(
        ArrayField(models.CharField(max_length=255)), null=True, blank=True
    )
    location_string = models.CharField(max_length=255, db_index=True, unique=True)
    geolocation = models.PointField(geography=True, default=Point(0.0, 0.0))

    # this is not geographical but speeds up computation for e.g. bounding box check
    geolocation_geometry = models.PointField(default=Point(0.0, 0.0))


class Incident(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=1000, blank=True, default="", null=True)
    description = models.TextField()
    date = models.DateField()
    iso3166_2 = models.CharField(max_length=5)
    location = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True)
    chronicle = models.ForeignKey("Chronicle", on_delete=models.SET_NULL, null=True)
    search_vector = SearchVectorField(null=True)

    objects = IncidentSearchQuerySet.as_manager()


class Source(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, default="")
    date = models.DateField(blank=True, null=True)
    incident = models.ForeignKey("Incident", on_delete=models.CASCADE, default=None)


class Phrase(models.Model):
    option = models.TextField(primary_key=True)
    count = models.IntegerField(default=0)
    search_vector = SearchVectorField(null=True)

    objects = PhrasesQuerySet.as_manager()

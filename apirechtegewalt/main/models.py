from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point


class User(AbstractUser):
    pass


# can't edit in Admin https://stackoverflow.com/a/1737078/4028896


class Location(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    subdivisions = models.CharField(max_length=255, db_index=True, unique=True)
    geolocation = models.PointField(geography=True, default=Point(0.0, 0.0))


class Incident(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255)
    url = models.CharField(max_length=255)
    aggregator = models.CharField(max_length=255)
    title = models.CharField(max_length=1000, blank=True, default="")
    description = models.TextField()
    date = models.DateField()
    iso3166_2 = models.CharField(max_length=5)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)


class Source(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True, default="")
    date = models.DateField(blank=True, null=True)
    incident = models.ForeignKey(Incident, on_delete=models.CASCADE, default=None)

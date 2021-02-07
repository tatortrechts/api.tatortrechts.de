from django.contrib.auth.models import AbstractUser
from django.contrib.gis.db import models
from django.contrib.gis.geos import Point
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex

from .search import IncidentSearchQuerySet, LocationSearchQuerySet, PhrasesQuerySet

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

    house_number = models.CharField(max_length=255, null=True)
    street = models.CharField(max_length=255, null=True)
    postal_code = models.CharField(max_length=255, null=True)
    district = models.CharField(max_length=255, null=True)
    city = models.CharField(max_length=255, null=True)
    county = models.CharField(max_length=255, null=True)
    state = models.CharField(max_length=255, null=True)
    country = models.CharField(max_length=255, null=True)

    location_string = models.TextField(unique=True)
    geolocation = models.PointField(geography=True, default=Point(0.0, 0.0))
    # this is not geographical but speeds up computation for e.g. bounding box check
    geolocation_geometry = models.PointField(default=Point(0.0, 0.0))
    search_vector = SearchVectorField(null=True)

    objects = LocationSearchQuerySet.as_manager()

    class Meta(object):
        indexes = [GinIndex(fields=["search_vector"])]


class Incident(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255, unique=True)
    url = models.CharField(max_length=255)
    title = models.CharField(max_length=1000, blank=True, default="", null=True)
    description = models.TextField()
    date = models.DateField()
    orig_city = models.CharField(max_length=255, null=True)
    orig_county = models.CharField(max_length=255, null=True)
    orig_address = models.CharField(max_length=255, null=True)

    location = models.ForeignKey("Location", on_delete=models.SET_NULL, null=True)
    chronicle = models.ForeignKey("Chronicle", on_delete=models.SET_NULL, null=True)
    search_vector = SearchVectorField(null=True)
    phrases = models.ManyToManyField("Phrase")
    contexts = models.TextField(null=True, blank=True)
    factums = models.TextField(null=True, blank=True)
    motives = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)

    objects = IncidentSearchQuerySet.as_manager()

    class Meta(object):
        indexes = [GinIndex(fields=["search_vector"])]


class Source(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rg_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    url = models.TextField(null=True, blank=True)
    date = models.DateField(blank=True, null=True)
    incident = models.ForeignKey("Incident", on_delete=models.CASCADE, default=None)


class Phrase(models.Model):
    option = models.TextField(primary_key=True)
    count = models.IntegerField(default=0)
    search_vector = SearchVectorField(null=True)

    objects = PhrasesQuerySet.as_manager()

    class Meta(object):
        indexes = [GinIndex(fields=["search_vector"])]


# No inheritance to not fuck up the logic (filter et.c) of Incident
class IncidentSubmitted(models.Model):
    location_input = models.CharField(
        "Ort", help_text="Z. B. 'Dortmund, Dorstfeld'", max_length=1000
    )
    sources_input = models.TextField(
        "Quellen",
        help_text="Schick uns öffentliche Belege zu, für den von dir geschilderten Fall. Z. B. Links zu einem Zeitungsbericht.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    rg_id = models.CharField(max_length=255, unique=True)
    title = models.CharField(
        "Titel",
        help_text="Beschreib in ein paar Worten, was passiert ist. Z. B. 'Hakenkreuz an Schulwand gesprüht'",
        max_length=1000,
    )
    description = models.TextField(
        "Beschreibung",
        help_text="Erzähl in ein paar Sätzen, worum es geht. Z. B. 'In der XY Schule ist eine unbekannte Person dabei beobachtet worden, wie sie ....'",
    )
    date = models.DateField("Datum")
    email = models.EmailField(
        "Email",
        help_text="Lass uns optional deine E-Mail Adresse da, damit wir mit dir bei Nachfragen in Kontakt treten können.",
        null=True,
        blank=True,
    )

    contexts = models.TextField(null=True, blank=True)
    factums = models.TextField(null=True, blank=True)
    motives = models.TextField(null=True, blank=True)
    tags = models.TextField(null=True, blank=True)

    # class Meta:
    #     db_table = "incident_submitted"


class ErrorReport(models.Model):
    rg_id = models.TextField()
    description = models.TextField()

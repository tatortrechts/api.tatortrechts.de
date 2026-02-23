import datetime

import pytest
from django.contrib.gis.geos import Point
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def chronicle_berlin(db):
    from apirechtegewalt.main.models import Chronicle

    return Chronicle.objects.create(
        name="Berliner Register",
        description="Chronicle for Berlin incidents",
        url="https://example.com/berlin",
        chronicle_source="berliner-register",
        iso3166_1="DE",
        iso3166_2="DE-BE",
        region="Berlin",
    )


@pytest.fixture
def chronicle_sachsen(db):
    from apirechtegewalt.main.models import Chronicle

    return Chronicle.objects.create(
        name="RAA Sachsen",
        description="Chronicle for Saxony incidents",
        url="https://example.com/sachsen",
        chronicle_source="raa-sachsen",
        iso3166_1="DE",
        iso3166_2="DE-SN",
        region="Sachsen",
    )


@pytest.fixture
def location_berlin(db):
    from apirechtegewalt.main.models import Location

    point = Point(13.3777, 52.5163, srid=4326)
    return Location.objects.create(
        city="Berlin",
        county="Berlin",
        state="Berlin",
        country="Deutschland",
        district="Mitte",
        street="Pariser Platz",
        house_number="1",
        postal_code="10117",
        geolocation=point,
        geolocation_geometry=point,
        latitude=52.5163,
        longitude=13.3777,
    )


@pytest.fixture
def location_dresden(db):
    from apirechtegewalt.main.models import Location

    point = Point(13.7373, 51.0504, srid=4326)
    return Location.objects.create(
        city="Dresden",
        county="Dresden",
        state="Sachsen",
        country="Deutschland",
        district="Altstadt",
        street="Prager Strasse",
        house_number="10",
        postal_code="01069",
        geolocation=point,
        geolocation_geometry=point,
        latitude=51.0504,
        longitude=13.7373,
    )


@pytest.fixture
def location_munich(db):
    from apirechtegewalt.main.models import Location

    point = Point(11.5820, 48.1351, srid=4326)
    return Location.objects.create(
        city="Muenchen",
        county="Muenchen",
        state="Bayern",
        country="Deutschland",
        geolocation=point,
        geolocation_geometry=point,
        latitude=48.1351,
        longitude=11.5820,
    )


@pytest.fixture
def incident_berlin(db, chronicle_berlin, location_berlin):
    from apirechtegewalt.main.models import Incident

    return Incident.objects.create(
        rg_id="berlin-001",
        url="https://example.com/incident/1",
        title="Rassistischer Angriff in Mitte",
        description="Ein rassistisch motivierter Angriff auf dem Alexanderplatz.",
        date=datetime.date(2023, 6, 15),
        location=location_berlin,
        chronicle=chronicle_berlin,
        contexts="Alltag",
        factums="Körperverletzung",
        motives="Rassismus",
        tags="gewalt,rassismus",
    )


@pytest.fixture
def incident_berlin_2(db, chronicle_berlin, location_berlin):
    from apirechtegewalt.main.models import Incident

    return Incident.objects.create(
        rg_id="berlin-002",
        url="https://example.com/incident/2",
        title="Hakenkreuz-Schmiererei",
        description="Hakenkreuz an Schulwand gesprüht in Neukölln.",
        date=datetime.date(2023, 9, 20),
        location=location_berlin,
        chronicle=chronicle_berlin,
        contexts="Schule",
        factums="Sachbeschädigung",
        motives="Antisemitismus",
        tags="sachbeschädigung",
    )


@pytest.fixture
def incident_dresden(db, chronicle_sachsen, location_dresden):
    from apirechtegewalt.main.models import Incident

    return Incident.objects.create(
        rg_id="dresden-001",
        url="https://example.com/incident/3",
        title="Rechte Demonstration",
        description="Rechtsextreme Demonstration in der Dresdner Altstadt.",
        date=datetime.date(2022, 3, 10),
        location=location_dresden,
        chronicle=chronicle_sachsen,
        contexts="Demonstration",
        factums="Volksverhetzung",
        motives="Rechtsextremismus",
        tags="demonstration,rechtsextremismus",
    )


@pytest.fixture
def incident_munich(db, chronicle_berlin, location_munich):
    from apirechtegewalt.main.models import Incident

    return Incident.objects.create(
        rg_id="muenchen-001",
        url="https://example.com/incident/4",
        title="Vorfall in Muenchen",
        description="Beschreibung eines Vorfalls in Muenchen.",
        date=datetime.date(2023, 1, 5),
        location=location_munich,
        chronicle=chronicle_berlin,
    )


@pytest.fixture
def source_for_berlin(db, incident_berlin):
    from apirechtegewalt.main.models import Source

    return Source.objects.create(
        rg_id="src-berlin-001",
        name="Tagesspiegel",
        url="https://tagesspiegel.de/article/1",
        date=datetime.date(2023, 6, 16),
        incident=incident_berlin,
    )


@pytest.fixture
def all_incidents(incident_berlin, incident_berlin_2, incident_dresden, incident_munich):
    return [incident_berlin, incident_berlin_2, incident_dresden, incident_munich]


@pytest.fixture
def phrases_synced(db, incident_berlin, incident_berlin_2, incident_dresden):
    from apirechtegewalt.main.models import Incident, Location, Phrase

    p1 = Phrase.objects.create(option="Angriff", count=5)
    p2 = Phrase.objects.create(option="Hakenkreuz", count=3)
    p3 = Phrase.objects.create(option="Demonstration", count=2)

    incident_berlin.phrases.add(p1)
    incident_berlin_2.phrases.add(p2)
    incident_dresden.phrases.add(p3)

    Incident.objects.sync()
    Location.objects.sync()
    Phrase.objects.sync()
    return [p1, p2, p3]


@pytest.fixture
def search_synced_incidents(all_incidents, source_for_berlin, phrases_synced):
    return all_incidents

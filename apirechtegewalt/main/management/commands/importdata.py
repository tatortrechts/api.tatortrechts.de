import dataset
from apirechtegewalt.main.models import Incident, Location, Source
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm


class Command(BaseCommand):
    help = "Import data from a sqlite db."

    def add_arguments(self, parser):
        parser.add_argument("db_path", type=str)

    def handle(self, db_path, *args, **options):
        db = dataset.connect("sqlite:///" + db_path)

        for location in tqdm(db["locations"].all()):
            # can't use `update_or_create` for Geo

            sub = location["subdivisions"]
            p = Point(location["longitude"], location["latitude"])
            try:
                obj = Location.objects.get(subdivisions=sub)
                obj.geolocation = p
                # for key, value in defaults.items():
                #     setattr(obj, key, value)
                obj.save()
            except Location.DoesNotExist:
                obj = Location.objects.create(
                    subdivisions=location["subdivisions"], geolocation=p
                )

        for incident in tqdm(db["incidents"].all()):
            l = Location.objects.get(subdivisions=incident["subdivisions"])

            for x in ["id", "latitude", "longitude", "point_geom", "subdivisions"]:
                del incident[x]

            obj, created = Incident.objects.update_or_create(location=l, **incident)

        for source in tqdm(db["sources"].all()):
            try:
                incident = Incident.objects.get(rg_id=source["rg_id"])
            except Incident.DoesNotExist:
                print(f"cannot find an incident for {source}")
                continue
            del source["id"]
            obj, created = Source.objects.update_or_create(incident=incident, **source)

        Incident.objects.sync()

        self.stdout.write(self.style.SUCCESS("Successfully imported data"))

import dataset
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from ...autocomplete import generate_phrases
from ...models import Incident, Chronicle, Source, Location


class Command(BaseCommand):
    help = "Import data from a sqlite db."

    def add_arguments(self, parser):
        parser.add_argument("db_path", type=str)

    def handle(self, db_path, *args, **options):
        db = dataset.connect("sqlite:///" + db_path)

        for c in tqdm(db["chronicles"].all()):
            obj, created = Chronicle.objects.update_or_create(
                name=c["chronicler_name"],
                description=c["chronicler_description"],
                url=c["chronicler_url"],
                chronicle_source=c["chronicle_source"],
                iso3166_1=c["iso3166_1"],
                iso3166_2=c["iso3166_2"],
                region=c["region"],
            )

        for location in tqdm(db["locations"].all()):
            # can't use `update_or_create` for Geo

            location_str = location["location_string"]
            sub = eval(location["subdivisions"])
            p = Point(location["longitude"], location["latitude"])
            try:
                obj = Location.objects.get(location_string=location_str)
                obj.geolocation = p
                obj.geolocation_geometry = p
                obj.subdivisions = sub
                # for key, value in defaults.items():
                #     setattr(obj, key, value)
                obj.save()
            except Location.DoesNotExist:
                obj = Location.objects.create(
                    location_string=location["location_string"],
                    geolocation=p,
                    geolocation_geometry=p,
                    subdivisions=sub,
                )

        for incident in tqdm(db["incidents"].all()):
            l = Location.objects.get(location_string=incident["location_string"])
            chro = Chronicle.objects.get(name=incident["chronicler_name"])

            for x in [
                "id",
                "latitude",
                "longitude",
                "point_geom",
                "location_string",
                "subdivisions",
                "chronicler_name",
            ]:
                del incident[x]

            obj, created = Incident.objects.update_or_create(
                location=l, chronicle=chro, **incident
            )

        for source in tqdm(db["sources"].all()):
            try:
                incident = Incident.objects.get(rg_id=source["rg_id"])
            except Incident.DoesNotExist:
                print(f"cannot find an incident for {source}")
                continue
            del source["id"]
            obj, created = Source.objects.update_or_create(incident=incident, **source)

        self.stdout.write("syncing text vector fields...")
        Incident.objects.sync()
        Location.objects.sync()

        self.stdout.write("syncing autocomplete phrases...")
        generate_phrases()

        self.stdout.write(self.style.SUCCESS("Successfully imported data"))

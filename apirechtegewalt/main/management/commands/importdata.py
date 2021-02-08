import dataset
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from tqdm import tqdm

from ...autocomplete import generate_phrases
from ...models import Chronicle, Incident, Location, Source

location_fields = [
    "house_number",
    "street",
    "postal_code",
    "district",
    "city",
    "county",
    "state",
    "country",
    "latitude",
    "longitude",
]


class Command(BaseCommand):
    help = "Import data from a sqlite db."

    def add_arguments(self, parser):
        parser.add_argument("db_path", type=str)
        parser.add_argument(
            "--delete",
            action="store_true",
        )

    def handle(self, db_path, *args, **options):
        db = dataset.connect("sqlite:///" + db_path)

        if options["delete"]:
            self.stdout.write("Deleting old data...")

            models = [Chronicle, Location, Incident, Source]
            for m in models:
                m.objects.all().delete()

        for c in tqdm(db["chronicles"].all(), desc="updating chronicles"):
            obj, created = Chronicle.objects.update_or_create(
                name=c["chronicler_name"],
                description=c["chronicler_description"],
                url=c["chronicler_url"],
                chronicle_source=c["chronicle_source"],
                iso3166_1=c["iso3166_1"],
                iso3166_2=c["iso3166_2"],
                region=c["region"],
            )

        for location in tqdm(db["locations"].all(), desc="updating location"):
            # can't use `update_or_create` for Geo
            real_loc = {x: location[x] for x in location_fields}
            real_loc["location_string"] = ", ".join(
                [x for k, x in real_loc.items() if x is not None]
            )

            if location["longitude"] is None or location["latitude"] is None:
                continue

            p = Point(float(location["longitude"]), float(location["latitude"]))
            try:
                obj = Location.objects.get(**real_loc)
                obj.geolocation = p
                obj.geolocation_geometry = p
                # not sure about this
                obj.__dict__.update(real_loc)
                obj.save()
            except Location.DoesNotExist:
                obj = Location.objects.create(
                    geolocation=p,
                    geolocation_geometry=p,
                    **real_loc,
                )

        for incident in tqdm(db["incidents"].all(), desc="updating incidents"):
            if incident["longitude"] is None or incident["latitude"] is None:
                print("fix this incident, long+lat are broken", incident)
                continue

            try:
                l = Location.objects.get(**{x: incident[x] for x in location_fields})
            except Location.MultipleObjectsReturned:
                print({x: incident[x] for x in location_fields})
                print(
                    list(
                        Location.objects.filter(
                            **{x: incident[x] for x in location_fields}
                        )
                    )
                )
                print("error")
                raise ValueError()
            except Location.DoesNotExist:
                print("skipping over this item, could not find location ", incident)
                continue

            chro = Chronicle.objects.get(name=incident["chronicler_name"])

            for x in [
                "id",
                "point_geom",
                "chronicler_name",
                "address",
            ] + location_fields:
                del incident[x]

            obj, created = Incident.objects.update_or_create(
                location=l, chronicle=chro, **incident
            )

        for source in tqdm(db["sources"].all(), desc="updating sources"):
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

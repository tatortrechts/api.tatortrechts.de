import dataset
from django.contrib.gis.geos import Point
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
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
    help = "Import incidents from a sqlite db into Django's postgres db"

    def add_arguments(self, parser):
        parser.add_argument(
            "db_path",
            type=str,
            default="/importdata/rechtegewalt.db",
            nargs="?",
        )

        parser.add_argument(
            "--skip-chronicles",
            action="store_true",
        )

        parser.add_argument(
            "--dry-run",
            action="store_true",
        )

    def add_chronicles(self):
        """add / update all chronicles"""
        for c in tqdm(self.db["chronicles"].all(), desc="updating chronicles"):
            Chronicle.objects.update_or_create(
                name=c["chronicler_name"],
                description=c["chronicler_description"],
                url=c["chronicler_url"],
                chronicle_source=c["chronicle_source"],
                iso3166_1=c["iso3166_1"],
                iso3166_2=c["iso3166_2"],
                region=c["region"],
            )

    def one_location_exists_import(self, incident):
        """Checks wheter there is exaclty one location for a given inicent in the imported data."""
        results = list(
            self.db["locations"].find(**{x: incident[x] for x in location_fields})
        )

        if len(results) == 1:
            return True
        if len(results) > 1:
            self.stdout.write(
                self.style.NOTICE(f"too many locations for {incident.rg_id}")
            )
        else:
            self.stdout.write(self.style.NOTICE(f"no location for {incident.rg_id}"))

        return False

    def get_or_create_location(self, incident):
        """get or create a location for an incident"""
        loc_fields = {x: incident[x] for x in location_fields}
        try:
            return Location.objects.get(**loc_fields)
        except Location.DoesNotExist:
            import_location = self.db["locations"].find_one(
                **{x: incident[x] for x in location_fields}
            )

            p = Point(
                float(import_location["longitude"]), float(import_location["latitude"])
            )
            return Location.objects.create(
                **loc_fields, geolocation=p, geolocation_geometry=p
            )

    def create_sources(self, incident):
        for source in self.db["sources"].find(rg_id=incident.rg_id):
            del source["id"]
            obj, created = Source.objects.update_or_create(incident=incident, **source)

    def add_incidents_for_chronicle(self, chronicle: Chronicle):
        """add all new imported incident for given chronicle"""

        self.stdout.write(f"adding new incidents for {chronicle.name}")

        last_updated = chronicle.incident_set.latest("date")

        for incident in tqdm(
            self.db["incidents"].find(chronicler_name=chronicle.name),
            desc=f"updating incidents: {chronicle.name}",
        ):
            if "age" in incident:
                del incident["age"]

            if "official" in incident:
                del incident["official"]

            if incident["longitude"] is None or incident["latitude"] is None:
                print("fix this incident, long+lat are broken", incident)
                continue

            rg_id = incident["rg_id"]

            try:
                Incident.objects.get(rg_id=rg_id)
            except Incident.DoesNotExist:

                # check wheter there is an
                inci_date = incident["date"].date()
                if last_updated and inci_date < last_updated.date:
                    confirm_input = input(
                        f"You sure you wanna import the incident {rg_id} from {inci_date}? It's older then {last_updated.rg_id} from {last_updated.date}. If yes, enter: 'y'"
                    )
                    if confirm_input != "y":
                        print(incident)
                        raise ValueError

                if not self.one_location_exists_import(incident):
                    continue

                l = self.get_or_create_location(incident)

                for x in [
                    "rg_id",
                    "id",
                    "point_geom",
                    "chronicler_name",
                    "address",
                ] + location_fields:
                    del incident[x]

                incident_obj = Incident.objects.create(
                    rg_id=rg_id, location=l, chronicle=chronicle, **incident
                )
                print(f"new incident: {rg_id}")
                print(incident)

                self.create_sources(incident_obj)

            # if oldinc is None:
            #     obj, created = Incident.objects.update_or_create(
            #         rg_id=rg_id, location=l, chronicle=chro, **incident
            #     )
            # else:
            #     # fuck this, fix later
            #     pass
            # update
            # oldinc.update(location=l, chronicle=chro, **incident)
            # oldinc.safe()

    @transaction.atomic
    def handle(self, db_path, *args, **options):
        # make the db easily accesible to all other methods
        self.db = dataset.connect("sqlite:///" + db_path)

        if not options["skip_chronicles"]:
            self.add_chronicles()

        # choose a single chronicle or iterate over all chronicles

        all_c = Chronicle.objects.all().values_list("name", flat=True)
        input_tex = (
            "Please choose a chronicle:\n0: all\n"
            + "\n".join([f"{i+1}: {x}" for i, x in enumerate(all_c)])
            + "\n"
        )
        chosen_c_input = input(input_tex)

        if chosen_c_input == "0":
            for c in Chronicle.objects.all():
                self.add_incidents_for_chronicle(c)
        else:
            chosen_c = Chronicle.objects.get(name=all_c[int(chosen_c_input) - 1])
            self.add_incidents_for_chronicle(chosen_c)

        if options["dry_run"]:
            # Return, rolling back transaction when atomic block exits
            transaction.set_rollback(True)
            return

        self.stdout.write("syncing text vector fields...")
        Incident.objects.sync()
        Location.objects.sync()

        self.stdout.write("syncing autocomplete phrases...")
        generate_phrases()

        self.stdout.write(self.style.SUCCESS("Successfully imported data"))

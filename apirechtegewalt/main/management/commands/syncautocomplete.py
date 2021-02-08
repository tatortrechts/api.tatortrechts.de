from django.core.management.base import BaseCommand, CommandError

from ...autocomplete import generate_phrases
from ...models import Chronicle, Incident, Location, Source


class Command(BaseCommand):
    help = "Generate phrases for autocomplete"

    def handle(self, *args, **options):
        self.stdout.write("syncing text vector fields...")
        Incident.objects.sync()
        Location.objects.sync()

        self.stdout.write("syncing autocomplete phrases...")
        generate_phrases()
        self.stdout.write(self.style.SUCCESS("Success"))

from django.core.management.base import BaseCommand, CommandError

from ...autocomplete import generate_phrases


class Command(BaseCommand):
    help = "Generate phrases for autocomplete"

    def handle(self, *args, **options):
        generate_phrases()
        self.stdout.write(self.style.SUCCESS("Successfully synced autocomplete"))

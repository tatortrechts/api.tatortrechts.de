from django.core.management.base import BaseCommand, CommandError
from django.core.management.color import no_style
from django.db import connection

from ...models import Chronicle, Incident, Location, Source


class Command(BaseCommand):
    help = "reset db for the import data models"

    def handle(self, *args, **options):
        self.stdout.write("deleting objects...")

        models = [Chronicle, Location, Incident, Source]
        for m in models:
            m.objects.all().delete()

        self.stdout.write("reseting ids")
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                self.stdout.write(".")
                cursor.execute(sql)

        self.stdout.write(self.style.SUCCESS("Success"))

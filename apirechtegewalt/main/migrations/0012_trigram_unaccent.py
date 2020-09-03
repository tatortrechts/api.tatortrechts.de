from django.contrib.postgres.operations import TrigramExtension, UnaccentExtension
from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0011_phrase_search_vector"),
    ]

    operations = [
        TrigramExtension(),
        UnaccentExtension(),
    ]

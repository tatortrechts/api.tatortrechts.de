from collections import Counter
from apirechtegewalt.main.models import Incident, Phrase
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from django.utils.text import smart_split
from tqdm import tqdm
import string


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])


def find_german_nouns(tokens):
    prev_t = None
    for t in tokens:
        if prev_t is not None and t[0].isupper():
            if not prev_t[-1] in string.punctuation:
                if t[-1] in string.punctuation:
                    yield t[:-1]
                else:
                    yield t

        prev_t = t


class Command(BaseCommand):
    help = "Import data from a sqlite db."

    def handle(self, *args, **options):
        Phrase.objects.all().delete()

        c = Counter()

        for ts in tqdm(Incident.objects.all().values_list("title", "description")):
            for t in ts:
                if not t or len(t) == 0:
                    continue
                tokens = list(smart_split(t))
                tokens = list(find_german_nouns(tokens))
                if len(tokens) == 0:
                    continue
                for i in range(1, min(4, len(tokens) + 1)):
                    c.update(find_ngrams(tokens, i))

                #     ngram_text = " ".join(ngram)
                # phrase, created = Phrase.objects.get_or_create(
                #     string=ngram_text
                # )

                # phrase.count = F("count") + 1

        phrase_list = [
            Phrase(string=" ".join(x[0]), count=x[1])
            for x in c.most_common(len(c) // 2)
        ]
        Phrase.objects.bulk_create(phrase_list)

        Phrase.objects.sync()

        self.stdout.write(self.style.SUCCESS("Successfully synced autocomplete"))

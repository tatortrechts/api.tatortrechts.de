import string
from collections import Counter

from django.contrib.gis.db import models
from django.utils.text import smart_split
from tqdm import tqdm

from .models import Incident, Phrase


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


# def generate_phrases2():
#     Phrase.objects.all().delete()

#     c = Counter()

#     for ts in tqdm(Incident.objects.all().values_list("title", "description")):
#         for t in ts:
#             if not t or len(t) == 0:
#                 continue
#             tokens = list(smart_split(t))
#             tokens = list(find_german_nouns(tokens))
#             if len(tokens) == 0:
#                 continue
#             for i in range(1, min(4, len(tokens) + 1)):
#                 c.update(find_ngrams(tokens, i))

#     phrase_list = [
#         Phrase(option=" ".join(x[0]), count=x[1]) for x in c.most_common(len(c) // 2)
#     ]
#     Phrase.objects.bulk_create(phrase_list)

#     Phrase.objects.sync()




def generate_phrases():
    Phrase.objects.all().delete()

    incis = []
    res = []
    c = Counter()

    for inci in tqdm(Incident.objects.all(), desc="generating ngrams / phrases"):
        all_ngrams = []
        for t in [inci.title, inci.description]:
            if not t or len(t) == 0:
                continue
            tokens = list(smart_split(t))
            tokens = list(find_german_nouns(tokens))
            if len(tokens) == 0:
                continue
            for i in range(1, min(4, len(tokens) + 1)):
                ngrams = find_ngrams(tokens, i)
                ngrams = [" ".join(x) for x in ngrams]
                c.update(ngrams)
                all_ngrams += ngrams
        res.append(all_ngrams)
        incis.append(inci)

    real_phrases = c.most_common(len(c) // 2)
    phrase_list = [Phrase(option=x[0], count=x[1]) for x in real_phrases]
    Phrase.objects.bulk_create(phrase_list)
    phrase_dict = {x.option: x for x in phrase_list}
    phrase_set = set(x[0] for x in real_phrases)

    for i, array_ph in tqdm(
        enumerate(res), total=len(res), desc="adding phrases to incidents"
    ):
        real_ph = [phrase_dict[x] for x in array_ph if x in phrase_set]
        incis[i].phrases.add(*real_ph)

    Phrase.objects.sync()

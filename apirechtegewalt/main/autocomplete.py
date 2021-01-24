from collections import Counter

from django.utils.text import smart_split
from tqdm import tqdm

from .models import Incident, Phrase

STOP_WORDS_SPACY = """
á a ab aber ach acht achte achten achter achtes ag alle allein allem allen
aller allerdings alles allgemeinen als also am an andere anderen anderem andern
anders auch auf aus ausser außer ausserdem außerdem
bald bei beide beiden beim beispiel bekannt bereits besonders besser besten bin
bis bisher bist
da dabei dadurch dafür dagegen daher dahin dahinter damals damit danach daneben
dank dann daran darauf daraus darf darfst darin darüber darum darunter das
dasein daselbst dass daß dasselbe davon davor dazu dazwischen dein deine deinem
deiner dem dementsprechend demgegenüber demgemäss demgemäß demselben demzufolge
den denen denn denselben der deren derjenige derjenigen dermassen dermaßen
derselbe derselben des deshalb desselben dessen deswegen dich die diejenige
diejenigen dies diese dieselbe dieselben diesem diesen dieser dieses dir doch
dort drei drin dritte dritten dritter drittes du durch durchaus dürfen dürft
durfte durften
eben ebenso ehrlich eigen eigene eigenen eigener eigenes ein einander eine
einem einen einer eines einige einigen einiger einiges einmal einmaleins elf en
ende endlich entweder er erst erste ersten erster erstes es etwa etwas euch
früher fünf fünfte fünften fünfter fünftes für
gab ganz ganze ganzen ganzer ganzes gar gedurft gegen gegenüber gehabt gehen
geht gekannt gekonnt gemacht gemocht gemusst genug gerade gern gesagt geschweige
gewesen gewollt geworden gibt ging gleich gross groß grosse große grossen
großen grosser großer grosses großes gut gute guter gutes
habe haben habt hast hat hatte hätte hatten hätten heisst heißt her heute hier
hin hinter hoch
ich ihm ihn ihnen ihr ihre ihrem ihren ihrer ihres im immer in indem
infolgedessen ins irgend ist
ja jahr jahre jahren je jede jedem jeden jeder jedermann jedermanns jedoch
jemand jemandem jemanden jene jenem jenen jener jenes jetzt
kam kann kannst kaum kein keine keinem keinen keiner kleine kleinen kleiner
kleines kommen kommt können könnt konnte könnte konnten kurz
lang lange leicht leider lieber los
machen macht machte mag magst man manche manchem manchen mancher manches mehr
mein meine meinem meinen meiner meines mich mir mit mittel mochte möchte mochten
mögen möglich mögt morgen muss muß müssen musst müsst musste mussten
na nach nachdem nahm natürlich neben nein neue neuen neun neunte neunten neunter
neuntes nicht nichts nie niemand niemandem niemanden noch nun nur
ob oben oder offen oft ohne
recht rechte rechten rechter rechtes richtig rund
sagt sagte sah satt schlecht schon sechs sechste sechsten sechster sechstes
sehr sei seid seien sein seine seinem seinen seiner seines seit seitdem selbst
selbst sich sie sieben siebente siebenten siebenter siebentes siebte siebten
siebter siebtes sind so solang solche solchem solchen solcher solches soll
sollen sollte sollten sondern sonst sowie später statt
tag tage tagen tat teil tel trotzdem tun
über überhaupt übrigens uhr um und uns unser unsere unserer unter
vergangene vergangenen viel viele vielem vielen vielleicht vier vierte vierten
vierter viertes vom von vor
wahr während währenddem währenddessen wann war wäre waren wart warum was wegen
weil weit weiter weitere weiteren weiteres welche welchem welchen welcher
welches wem wen wenig wenige weniger weniges wenigstens wenn wer werde werden
werdet wessen wie wieder will willst wir wird wirklich wirst wo wohl wollen
wollt wollte wollten worden wurde würde wurden würden
zehn zehnte zehnten zehnter zehntes zeit zu zuerst zugleich zum zunächst zur
zurück zusammen zwanzig zwar zwei zweite zweiten zweiter zweites zwischen
""".split()


STOP_WORDS = (
    STOP_WORDS_SPACY
    + "Mann Täter Gruppe Polizei Personen Angreifer Unbekannte Frau Männer Männern Betroffenen Jugendliche Jugendlichen Straße Motivation".lower().split()
)

STOP_WORDS = set(STOP_WORDS)


def find_ngrams(input_list, n):
    return zip(*[input_list[i:] for i in range(n)])


def find_german_nouns(tokens):
    prev_t = None
    for t in tokens:
        if prev_t is not None and t[0].isupper():
            if not prev_t[-1] in [".", "?", ";", ","]:
                if t[-1] in [".", "?", ";", ","]:
                    # test here again for stop words because the last token may be '.' etc.
                    if t[:-1].lower() not in STOP_WORDS:
                        yield t[:-1]
                else:
                    yield t

        prev_t = t


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
            tokens = t.replace('"', "").replace("'", "")
            tokens = list(smart_split(tokens))
            tokens = [t for t in tokens if t.lower() not in STOP_WORDS]
            tokens = list(find_german_nouns(tokens))

            if len(tokens) == 0:
                continue
            for i in range(1, min(4, len(tokens) + 1)):
                ngrams = find_ngrams(tokens, i)
                ngrams = [" ".join(sorted(x)) for x in ngrams]
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

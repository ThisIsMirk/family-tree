"""
Builds a structured, connected family tree (JSON) from the hand-drawn .xls charts.
Authored from the three screenshots (Mother / All / Father sheets).

Confidence convention on each node refers to how sure we are about WHO THE
PARENT IS (the vertical connector in the chart):
  conf="ok"  -> clear in the chart
  conf="?"   -> best guess; PLEASE VERIFY
A node also carries optional spouse / note, and 'star' marks the user's direct line.
"""
import json, re

def P(name, kids=None, spouse=None, note=None, conf="ok", star=False, marriage=None, color=None, emph=False, sheet=None, side=None, twin=None, pic=None, spouse_pic=None, dob=None, occ=None, spouse_dob=None, spouse_occ=None):
    return {"name": name, "spouse": spouse, "note": note, "conf": conf, "star": star,
            "marriage": marriage, "color": color, "emph": emph, "sheet": sheet,
            "side": side, "twin": twin, "pic": pic, "spouse_pic": spouse_pic, "dob": dob, "occ": occ,
            "spouse_dob": spouse_dob, "spouse_occ": spouse_occ, "kids": kids or []}

ASK = "Please let Mirza know if you know who belongs here."
def unknown(n, extra=None):
    """n placeholder '?' children for an Excel 'N children/daughters' count."""
    note = f"{extra} — {ASK}" if extra else ASK
    return [P("?", note=note) for _ in range(n)]

# ---------------------------------------------------------------------------
# The "joined" family. Mariyomma (mother's side) married Rajab (father's side), and their
# daughter Fathima married Nangeri Aboobacker (father's side). Per the family, the descendants of
# these marriages are shown on BOTH sides: a PINK copy under the mother and a BLUE copy under
# the father. The two copies of a person share a `twin` id so the app can jump between them.
# (Built person-by-person: a person's pink copy sits under their mother, blue copy under their
# father — so e.g. Mujeeb appears under Fathima (pink) and under Nangeri Aboobacker (blue), not thrice.)
# ---------------------------------------------------------------------------
# Birth date + occupation for the living generation, from "Perooli Branch.xlsx" (uncle's sheet).
# Keyed by the person's unique `twin` id so both copies (pink/blue) get it and there's no
# risk of matching a same-named ancestor. Value = (dob, occupation); dob may be None.
BIO = {
    # Sabeetha's household
    "sabeetha": ("19 Aug 1973", "Entrepreneur"),
    "fathima_sana": ("2 Sep 1991", "Engineer, Fly Over Wonders"),
    "joaan": ("25 Oct 2017", "Student"),
    "ryaan": ("5 Sep 2022", "Student"),
    "mohammed_jathin": ("21 May 2001", "Chef"),
    "aysha_zeba": ("13 Sep 2009", "Student"),
    # Fathima & Nangeri Aboobacker's household
    "fathima": ("26 Jan 1951", "Homemaker"),
    "mujeeb": ("19 Dec 1971", "Farmer"),
    "niharika": ("17 Jun 2001", "Marketing Coordinator"),
    "norell": ("4 Dec 2008", "Student"),
    "olivia": ("4 Dec 2008", "Student"),
    "sajith": ("1 Jul 1969", "Civil Engineer"),
    "mirza": ("9 Nov 1998", "Data Engineer"),
    "rajab_jr": ("26 Feb 2001", "Operations, Malabar"),
    "aman": ("16 Aug 2009", "Student"),
    "hafis": ("1 Jan 1973", "Engineer"),
    "zayan": (None, "Student"), "zayed": (None, "Student"),
    "zarif": (None, "Student"), "zara": (None, "Student"),
    "feroz": ("26 Jan 1967", "Doctor"),
    "adam": (None, "Aditya Honda"),
    "selsha": (None, "HR Manager"),
    "hessa": (None, "Media Manager"),
    # Safiya's household
    "safiya2": ("21 Jun 1959", "Homemaker"),
    "aamir": ("15 Jun 1983", "Senior IT Engineer"),
    "alik": ("22 Jul 2014", "Student"), "avik": ("2 Feb 2016", "Student"),
    "sabir": ("15 Jun 1983", "Administration Officer"),
    "ruaa": ("24 May 2014", "Student"), "raed": ("26 Jun 2020", "Student"),
    "hiba": ("28 Jan 1992", "Marketing Executive"),
    "eira": ("18 Nov 2014", "Student"),
    # Kadheeja's household
    "salima": ("25 Apr 1975", "Homemaker"),
    "sajiya": ("2 Jun 1993", "ECE Engineer"),
    "tihami": ("30 Jan 2018", "Student"),
    "yildiz": ("13 Feb 2025", "Infant"),
    "muhammed_azeez": ("7 Nov 1996", "EEE Engineer"),
    "ayisha_aseez": ("21 Aug 2004", "Student (BDS)"),
    "ibrahim_aseez": ("21 Aug 2004", "Student (MBBS)"),
    "reshma": ("10 Sep 1977", "Finance Manager, Carewell Clinic"),
    "fathwimath": ("29 Nov 2001", "BSD Student"),
    "mosus": ("19 Aug 2004", "NIT Student, Calicut"),
    "eesa": ("29 May 2006", "MBBS Student, TVM"),
    "afsath": ("28 Feb 1971", "Tailor"),
    "sohan": ("11 Nov 1990", "Senior Software Engineer"),
    "adheena": ("10 Dec 1992", "Psychiatric Social Worker"),
    "ahammed_looth": ("26 Dec 2018", "Student"),
    "inthan": ("9 Sep 2004", "Engineering Student"),
    # Noorjahan's household
    "noorjahan": ("10 Jan 1969", "Entrepreneur"),
    "shurouk": ("24 Jul 1987", "Business"),
    "mohammed_shurouk": ("10 Nov 2018", "Student"),
    "sheikha": ("10 Aug 2023", "Toddler"),
    "diyana": ("4 Jan 1990", "Dentist"),
    "ahmed_diyana": ("22 Aug 2014", "Student"),
    "hamid": ("8 Jan 2019", "Student"),
    "houri": ("30 Apr 2025", "Toddler"),
    "suroor": ("11 Dec 1994", "Civil Engineer"),
    "faheema_mariyom": ("20 Oct 2022", "Architect"),
    # Mumtaz's household
    "mumtaz": ("8 Apr 1966", "Homemaker"),
    "fahad": ("2 Apr 1986", "Entrepreneur"),
    "elenor": ("19 Dec 2020", "Student"),
    "eva": ("15 Oct 1990", "Entrepreneur"),
    "noom": ("3 Oct 2017", "Student"),
}

# Married-in spouses (shown as a chip on their partner's node, not their own node), keyed by the
# PARTNER's twin id. Value = (spouse_dob, spouse_occ); dob may be None.
SPOUSE_BIO = {
    "sabeetha":     ("20 May 1968", "KWA Supdt (Retired)"),          # Abdul Basheer .T.K
    "fathima_sana": ("2 Aug 1990",  "Engineer"),                     # Shinu Azees
    "mujeeb":       ("24 Feb 1974", "Engineer, Malabar Group"),      # Husna Beegum .PP
    "hafis":        (None,          "Doctor"),                       # Sonia Haris
    "feroz":        (None,          "Director, Aditya Honda"),       # Praseena KK
    "safiya2":      ("7 Jan 1947",  "Senior Executive, Wataniya Telecom"),  # Abdul Khader
    "aamir":        ("10 May 1989", "IT Engineer"),                  # Shubi Amir
    "sabir":        ("2 Nov 1989",  "HR Executive"),                 # Farin Harris
    "salima":       ("10 Apr 1967", "Sr. Facilities Officer"),       # Aseez Kanhirakoottathil
    "sajiya":       ("6 Sep 1988",  "Mechanical Engineer"),          # Muhammed Wasil
    "muhammed_azeez": ("2 Oct 2000", "Chemical Engineer"),           # Laamia Thaha
    "reshma":       ("1 Apr 1968",  "Doctor"),                       # Mohammed Ashraf P.K
    "afsath":       ("2 Jun 1964",  "Retired Head Master"),          # Hamsath Palakeel
    "sohan":        ("3 Feb 1996",  "PhD Scholar"),                  # Najma .K.K
    "adheena":      ("22 May 1988", "Business"),                     # Mohammed Fasil
    "noorjahan":    ("15 Apr 1959", "Business"),                     # Abdu Rahman Thekkatt
    "shurouk":      ("23 Aug 1990", "Auditor, Projects"),            # Fathima Mehlika
    "diyana":       ("1 May 1985",  "Business"),                     # Abdullah Zuhair
    "suroor":       ("29 Oct 1999", "Psychologist"),                 # Fathima Sidra
    "mumtaz":       ("1 May 1953",  "Business"),                     # Abdurahiman Kkutty
    "fahad":        ("5 Jun 1991",  "Entrepreneur"),                 # Lubna Habeeb
    "eva":          ("11 Jan 1983", "Entrepreneur"),                 # Mohammed Shijil
    "sajith":       ("26 Jul 1969", "Homemaker"),                    # Shaniba Chemmikkat
}

def D(name, twin, side, kids=None, **kw):
    if twin in BIO:                             # auto-fill dob/occupation from the uncle's sheet
        dob, occ = BIO[twin]
        if dob: kw.setdefault("dob", dob)
        if occ: kw.setdefault("occ", occ)
    if twin in SPOUSE_BIO:                      # …and their spouse's dob/occupation
        sdob, socc = SPOUSE_BIO[twin]
        if sdob: kw.setdefault("spouse_dob", sdob)
        if socc: kw.setdefault("spouse_occ", socc)
    return P(name, kids=kids, side=side, twin=twin, **kw)

def sajith_kids(side):
    # Sajith's children. Pictures live on the canonical (Mariyomma-side) copy only.
    m = (side == "mother")
    return [
        D("Mirza", "mirza", side, pic=("pics/mirza.jpeg" if m else None)),
        D("Rajab", "rajab_jr", side, note="Named after his great-grandfather Rajab.",
          pic=("pics/rajab.jpeg" if m else None)),
        D("Aman",  "aman",  side, pic=("pics/aman.jpeg" if m else None)),
    ]

def feroz_kids(side):
    m = (side == "mother")
    return [
        D("Adam",   "adam",   side, pic=("pics/Adam.jpeg"   if m else None)),
        D("Hessa",  "hessa",  side, pic=("pics/Hessa.jpeg"  if m else None)),
        D("Selsha", "selsha", side, pic=("pics/Selsha.jpeg" if m else None)),
    ]

def mujeeb_kids(side):
    m=(side=="mother")
    return [
        D("Niharika", "niharika", side, pic=("pics/niharika.jpeg" if m else None)),
        D("Norell",   "norell",   side, pic=("pics/norell.jpeg" if m else None)),
        D("Olivia",   "olivia",   side, pic=("pics/olivia.jpeg" if m else None)),
    ]

def hafis_kids(side):
    m = (side == "mother")
    return [
        D("Zayan", "zayan", side, pic=("pics/Zayan.png" if m else None)),
        D("Zarif", "zarif", side, pic=("pics/Zarif.png" if m else None)),
        D("Zara",  "zara",  side, pic=("pics/Zara.png"  if m else None)),
        D("Zayed", "zayed", side, pic=("pics/Zayed.png" if m else None)),
    ]

def fathima_kids(side):
    return [
        D("Feroz",  "feroz",  side, spouse="Praseena", spouse_pic="pics/Praseena.jpeg", kids=feroz_kids(side)),
        D("Sajith", "sajith", side, star=True, pic=("pics/sajith.jpeg" if side=="mother" else None),
          spouse="Shaniba", spouse_pic="pics/shaniba.jpeg", kids=sajith_kids(side)),
        D("Mujeeb", "mujeeb", side, note="Listed as the original file's author",
          pic=("pics/mujeeb.jpeg" if side=="mother" else None),
          spouse="Husna", spouse_pic="pics/husna.jpeg", kids=mujeeb_kids(side)),
        D("Hafis",  "hafis",  side, pic=("pics/Hafis.png" if side=="mother" else None),
          spouse="Sonia", spouse_pic="pics/Soniaaunty.png", kids=hafis_kids(side)),
    ]

def fathima_sana_kids(side):
    m = (side == "mother")
    return [
        D("Joaan", "joaan", side, pic=("pics/Joaan.jpeg" if m else None)),
        D("Ryaan", "ryaan", side, pic=("pics/Ryaan.jpeg" if m else None)),
    ]

def sabeetha_kids(side):
    m = (side == "mother")
    return [
        D("Fathima Sana", "fathima_sana", side, pic=("pics/sana.jpeg" if m else None),
          spouse="Shinu", spouse_pic="pics/Shinu.jpeg", kids=fathima_sana_kids(side)),
        D("Mohammed Jathin", "mohammed_jathin", side, pic=("pics/mohammed.jpeg" if m else None)),
        D("Aysha Zeba",      "aysha_zeba",      side, pic=("pics/Aysha.jpeg"    if m else None)),
    ]

def shurouk_kids(side):
    m=(side=="mother")
    return [D("Mohammad Abdul Rahiman","mohammed_shurouk",side, pic=("pics/mohammed_shurouk.jpeg" if m else None)),
            D("Sheikha Fathima","sheikha",side, pic=("pics/sheikha.jpeg" if m else None))]

def diyana_kids(side):
    m=(side=="mother")
    return [D("Ahmed","ahmed_diyana",side, pic=("pics/ahmed_diyana.jpeg" if m else None)),
            D("Hamid","hamid",side, pic=("pics/hamid.jpeg" if m else None)),
            D("Houri","houri",side, pic=("pics/houri.jpeg" if m else None))]

def noorjahan_kids(side):
    m=(side=="mother")
    return [
        D("Shurouk","shurouk",side, pic=("pics/shurouk.jpeg" if m else None),
          spouse="Mehlika", spouse_pic="pics/mehlika.jpeg", kids=shurouk_kids(side)),
        D("Diyana","diyana",side, pic=("pics/diyana.jpeg" if m else None),
          spouse="Abdullah", kids=diyana_kids(side)),
        D("Suroor","suroor",side, pic=("pics/suroor.jpeg" if m else None),
          spouse="Fathima Sidra", spouse_pic="pics/fathima_sidra.jpeg"),
        D("Faheema Mariyom","faheema_mariyom",side, pic=("pics/mariyom.jpeg" if m else None)),
    ]

def aamir_kids(side):
    m=(side=="mother")
    return [D("Alik","alik",side,pic=("pics/alik.jpg" if m else None)),
            D("Avik","avik",side,pic=("pics/avik.jpg" if m else None))]

def sabir_kids(side):
    m=(side=="mother")
    return [D("Ruaa","ruaa",side,pic=("pics/ruaa.jpg" if m else None)),
            D("Raed","raed",side,pic=("pics/raed.jpeg" if m else None))]

def hiba_kids(side):
    m=(side=="mother")
    return [D("Eira","eira",side,pic=("pics/eira.jpg" if m else None))]

def safiya_kids(side):
    m=(side=="mother")
    return [
        D("Aamir","aamir",side,pic=("pics/aamir.jpg" if m else None),
          spouse="Shubi", spouse_pic="pics/shubi.jpg", kids=aamir_kids(side)),
        D("Sabir","sabir",side,pic=("pics/sabir.jpg" if m else None),
          spouse="Farin", spouse_pic="pics/farin.jpeg", kids=sabir_kids(side)),
        D("Hiba","hiba",side,pic=("pics/hiba.jpg" if m else None), kids=hiba_kids(side)),
    ]

def reshma_kids(side):
    m=(side=="mother")
    return [D("Fathwimath","fathwimath",side),   # no photo yet
            D("Mosus","mosus",side, pic=("pics/mosus.jpeg" if m else None)),
            D("Eesa","eesa",side, pic=("pics/eesa.jpeg" if m else None))]

def adheena_kids(side):
    m=(side=="mother")
    return [D("Ahammed Looth","ahammed_looth",side, pic=("pics/ahammed_looth.jpeg" if m else None))]

def afsath_kids(side):
    m=(side=="mother")
    return [
        D("Sohan",   "sohan",   side, pic=("pics/sohan.jpeg" if m else None),
          spouse="Najma", spouse_pic="pics/najma.jpeg"),
        D("Adheena", "adheena", side, pic=("pics/adheena.jpeg" if m else None),
          spouse="Mohammed Fasil", spouse_pic="pics/mohammed_fasil.jpeg", kids=adheena_kids(side)),
        D("Inthan",  "inthan",  side, pic=("pics/inthan.jpeg" if m else None)),
    ]

def mumtaz_kids(side):
    m=(side=="mother")
    return [
        D("Fahad","fahad",side, pic=("pics/fahad.jpeg" if m else None),
          spouse="Lubna Habeeb", spouse_pic="pics/lubna.jpeg",
          kids=[D("Elenor Ocean Fahad","elenor",side, pic=("pics/elenor.jpeg" if m else None))]),
        D("Eva","eva",side, pic=("pics/eva.jpeg" if m else None),
          spouse="Mohammed Shijil", spouse_pic="pics/shijil.jpeg",
          kids=[D("Noom Miraya Shijil","noom",side, pic=("pics/noom.jpeg" if m else None))]),
    ]

def sajiya_kids(side):
    m=(side=="mother")
    return [D("Tihami Wasil","tihami",side, pic=("pics/tihami.jpeg" if m else None)),
            D("Yildiz Feray","yildiz",side, pic=("pics/yildiz.jpeg" if m else None))]

def salima_kids(side):
    m=(side=="mother")
    return [
        D("Sajiya Aseez",   "sajiya",         side, pic=("pics/sajiya.jpeg" if m else None),
          spouse="Muhammed Wasil", kids=sajiya_kids(side)),
        D("Muhammed Azeez", "muhammed_azeez", side, pic=("pics/muhammed_azeez.jpeg" if m else None),
          spouse="Laamia Thaha", spouse_pic="pics/laamia_thaha.jpeg"),
        D("Ayisha Aseez",   "ayisha_aseez",   side, pic=("pics/ayisha_aseez.jpeg" if m else None)),
        D("Ibrahim Aseez",  "ibrahim_aseez",  side, pic=("pics/ibrahim_aseez.jpeg" if m else None)),
    ]

def khadeeja_kids(side):
    return [
        D("Afsath", "afsath", side, pic=("pics/afsath.jpeg" if side=="mother" else None),
          spouse="Hamsath", spouse_pic="pics/hamsath_palakeel.jpeg", kids=afsath_kids(side)),
        D("Salima", "salima", side, pic=("pics/salima.jpeg" if side=="mother" else None),
          spouse="Aseez Kanhirakoottathil", spouse_pic="pics/aseez_kanhirakoottathil.jpeg", kids=salima_kids(side)),
        D("Reshma", "reshma", side, pic=("pics/reshma.jpeg" if side=="mother" else None),
          spouse="Mohammed Ashraf", spouse_pic="pics/reshma_husband.jpeg", kids=reshma_kids(side)),
        D("Reedha", "reedha", side),
    ]

def joined_children(side):
    """Mariyomma & Rajab's 7 children (+ descendants), tagged for `side`. Fathima carries her
       children on BOTH the mother (Mariyomma) and father (Rajab) sides — and they also appear a
       third time under their own father Nangeri Aboobacker — so each of those 4 shows up 3×."""
    fathima = D("Fathima", "fathima", side, star=True, spouse="Nangeri Aboobacker",
                marriage=("fathima+nabacker" if side == "mother" else None),
                note=("Mummy ❤️" if side == "mother" else None),
                kids=fathima_kids(side))
    return [
        fathima,
        D("Khadeeja",   "khadeeja",  side, kids=khadeeja_kids(side)),
        D("K.Abdullah", "kabdullah", side, kids=[D("Anna","anna",side), D("Ishan","ishan",side)]),
        D("Safiya",     "safiya2",   side, pic=("pics/safiya.jpg" if side=="mother" else None),
          spouse="Abdul Khader", spouse_pic="pics/abdul_khader.jpg", kids=safiya_kids(side)),
        D("Mumtaz",     "mumtaz",    side, pic=("pics/mumtaz.jpeg" if side=="mother" else None),
          spouse="Abdurahiman Kkutty", spouse_pic="pics/abdurahiman.jpeg", kids=mumtaz_kids(side)),
        D("Noorjahan",  "noorjahan", side, pic=("pics/noorjahan.jpeg" if side=="mother" else None),
          spouse="Abdu Rahman", spouse_pic="pics/abdu_rahman.jpeg", kids=noorjahan_kids(side)),
        D("Sabeetha",   "sabeetha",  side, pic=("pics/sabeetha.jpeg" if side=="mother" else None),
          spouse="Basheer", spouse_pic="pics/basheer.jpeg", kids=sabeetha_kids(side)),
    ]

# ---------------------------------------------------------------------------
# MOTHER / ALL sheet  (root: Nelliadi Beeran Musaliar)
# ---------------------------------------------------------------------------
mother = P("Nelliadi Beeran Musaliar", [
    P("Valiya Chekkan"),   # placeholder — replaced below with the merged Father family (he IS "Valiya Chekkan & Thithi")
    P("Cheriya Chekkan", [
        P("Mahmoud"),
        P("Kunhamina"),
        P("Ayshomma"),
        P("Assya", note="No Issues"),
        P("Zainaba", kids=[P("Azees"), P("Mahmoud")]),
    ]),
    P("Thykkandi Mariyomma", [
        # 6 children of Thykkandi Mariyomma (confirmed)
        P("Aamina"),
        P("Aysha", star=True, kids=[
            P("Kunupath", note="Kadiri Kandi", kids=[
                # G_h: attachment to Kunupath is a guess
                P("Kunhabdullah", note="Kayirikandi", conf="?", kids=[
                    P("Nissar"), P("Laila"), P("Iqbal"), P("Navas"), P("Anwer")]),
                P("Kunhalima", conf="?", kids=[P("Vettippandi"), P("A.Rahman")]),
                P("Assya", conf="?", kids=[
                    P("Sharaf"), P("Kassim"), P("Hanifa"), P("Safiya"), P("Bushra")]),
                P("Mahmoud", conf="?"),
                P("Assu", conf="?"),
            ]),
            P("Khadija", note="Kundantavida", star=True, kids=[
                P("Mariyomma", star=True, spouse="Rajab", marriage="rajab+mariyomma", color="#e25c9c", emph=True,
                  note="m. Rajab — their children appear on both sides (pink here; blue under Rajab).",
                  kids=joined_children("mother")),       # PINK side: full family under Mariyomma
                P("Assu", emph=True, color="#e25c9c", kids=[P("Asif"), P("Haris"), P("Reshmi"), P("Taslima")]),
            ]),
            P("Moidu", note="Singapore"),
            P("Mammed", note="Singapore"),
        ]),
        P("Pathumma"),
        P("Kader", kids=[
            P("Kolari Mahmoud"),
            P("Ibrahim"),
            P("Assya- Thayyulathil",
              kids=[P("Ruqia"), P("Jameela"), P("Azees"), P("Sideque")]),
            P("Kunhaissa", kids=[
                P("Mammed Musaliar", kids=[
                    P("Azeez Musaliar", kids=[P("Mahmoud Chokli"), P("Shukkoor")]),
                    P("Kalanthu Musaliar"),
                    P("Ibrahim Kutty", kids=[P("Aysha"), P("Kulsu Teacher"), P("Faizal")]),
                    P("A.Rahman"),
                    P("Assyomma", spouse="Farhat"),
                    P("Ayshu"),
                ]),
                P("Abdu Musaliar", kids=[
                    P("Kalanthukka"), P("Koyilari Elomma"), P("Moidu"), P("Kunhaissa")]),
                P("A.Rahman Musaliar", kids=[
                    P("P.V. Mohammed"), P("Ibrahim Kutty"), P("Majeed"),
                    P("Kunhaissa-Mubarak"), P("Assya"), P("Ayshu"), P("Fathima")]),
                P("Moideen Haji", kids=[
                    P("Delux Mammu"), P("Kunhabdullah"), P("A.Rahman"), P("Aysha"), P("Zainaba")]),
                P("Ibrahim Musaliar", kids=[
                    P("Aboobacker"), P("Mammed Musaliar"),
                    P("Abdul Kader", kids=[P("Aamir"), P("Saabir"), P("Malu")]),
                    P("Abdu Rahman"),
                    P("Abdullah Kutty"), P("Kunhi Moideen"), P("Zainaba"), P("Safiya")]),
                P("Kunhi Bava", note="No Issues"),
                P("Kader Musaliar", kids=[
                    P("A.Rahman"),
                    P("Mammed Musaliar"),
                    P("Azeezkka ST", kids=[P("Thanzi"), P("Thenvi"), P("Thefsi"), P("Thedvi")]),
                    P("Aysha")]),
                # Kunhi Matha, Beevi, Assya are also the main Kunhaissa's children (10 in all)
                P("Kunhi Matha", kids=[
                    P("Kalanthu Musaliar", kids=[P("Mubarak Ahmed"), P("Mubarak Abd")])]),
                P("Beevi", kids=[
                    P("Kunhamina", kids=[P("Mammed"), P("Ubaidkka"), P("Azees")])]),
                P("Assya", kids=[
                    P("Farhat Moideen Haji",
                      note="Also appears in the Father sheet under Mohd Musaliar's line",
                      kids=[
                        P("Ahmed"), P("Safiya"), P("Salam"),
                        P("Soora", kids=[P("Basi"), P("Junaid"), P("Sister")]),
                        P("Aysha"), P("Gafoor"),
                        P("Zubaida", kids=unknown(3)),
                        P("Rahim Madathil", kids=[P("Hina")]),
                      ])]),
            ]),
        ]),
        P("Abdu", note="No Issues"),
        P("Thavodi Beeran", note="No Issues"),
    ]),
    P("Kunhaissa P.P"),
])

# ---------------------------------------------------------------------------
# FATHER sheet — now KNOWN to be the SAME man as Nelliadi's son "Valiya Chekkan"
# (he married Thithi). So this whole family hangs under Nelliadi via Valiya Chekkan,
# making Nelliadi Beeran Musaliar the single common ancestor of both sides.
# ---------------------------------------------------------------------------
valiya_chekkan = P("Valiya Chekkan", spouse="Thithi", sheet="Father",
    note="'Porathut House'.",
    kids=[
    P("Mariyam", kids=[
        P("Pathumma", star=True, kids=[
            P("Sulekha", kids=[P("Bavakka"), P("Ahmed"), P("Pokku")]),
            P("Rajab", star=True, spouse="Mariyomma", marriage="rajab+mariyomma", color="#3f74cf",
              note="m. Mariyomma — their children appear here (blue) and on the mother's side (pink under Mariyomma).",
              kids=joined_children("father")),          # BLUE side: full family under Rajab
            P("Sehad", kids=[P("Soora", kids=[P("Sulfat")])]),
            P("Mariyam", kids=[P("Hamza"), P("Mustafa"), P("A.Backer")]),
            P("Kader Haji", kids=[
                P("Peeshani"), P("Hamza"), P("Zubair"), P("Khaled"), P("Razak"),
                P("Mammed"), P("Beevi"), P("(etc.)")]),
            P("Aamina", kids=[P("Mammed"), P("Basheer"), P("Aseez"), P("Ramla"), P("Fathima")]),
        ]),
        P("Ummatha", kids=[P("Kunhi Moideen", note="Nalan Kutti")]),
        P("Khadija", kids=[P("Aysha"), P("Mohamed"), P("Abdullah")]),
        P("Abdu", kids=[
            P("Kunhammed", note="Super Med"), P("Pathumma"), P("Mariyomma")]),
        P("Ibrahim", note="No Issues"),
        P("Assainar", note="No Issues"),
        P("Moideen", note="'Great Batchelor' — No Issues"),
        P("Assya", note="No Issues"),
    ]),
    P("Assya", kids=[
        P("Pathuuma", kids=[
            P("Thayyulyil Moideen"), P("Vengadikal Abdullah"), P("Vengadikal Mammed")]),
        P("Sooppy", kids=[P("Abdullah"), P("Nissar"), P("Moideen"), P("Assya")]),
        P("Ayshoma", kids=[
            P("Kunhamina", kids=[
                P("A.Rahman", kids=[P("Noushad"), P("Shamshad")]),
                P("A.Kader", kids=[P("Saleena"), P("Nachi")]),
                P("Khaled", kids=[P("Mohamed")]),
                P("Nafisa", kids=[P("Unais"), P("Sehadi")]),
                P("Fathima", kids=[P("Asif"), P("Haris"), P("Reshmi"), P("Tasli")]),
                P("Kulsu", kids=[P("Thanzi"), P("Tajiba"), P("Anas")]),
                P("Jameela", kids=[P("Hijas")]),
            ]),
            P("Nafisa", kids=[P("Advocate Najeeb")]),
            P("Fathima", kids=[P("Aysha"), P("Kulsu Teacher"), P("Faizal"), P("Zayar")]),
        ]),
        P("Khadisha", note="Nangeri Aboobacker's mother", kids=[
            P("Nangeri Aboobacker", spouse="Fathima", marriage="fathima+nabacker", color="#7eb3e8",
              dob="28 Mar 1942", occ="Retired ACP, Kerala Police",
              note="Daddy ❤️ — m. Fathima. Their children appear here (Nangeri Aboobacker's side, light blue) and on the mother's side (pink under Fathima).",
              kids=fathima_kids("backer")),             # N.A. BACKER's side: Feroz/Sajith/Mujeeb/Hafis under their father
        ]),
        P("C.K.Abdullah", note="Singapore", kids=unknown(7)),
    ]),
    P("Ummatha", kids=[
        P("Pathu", kids=[
            P("Kunhaissa", kids=[
                P("P.M.Khaled"), P("Kunhabdulla"), P("Pathumma"),
                P("Abbas"), P("Safiya"), P("Sura")]),
            P("Kunhami", kids=[
                P("Driver K.Ahmed"), P("Mahmoud-Baker"), P("Hamza"),
                P("Karim"), *unknown(3, "Daughter")]),
            P("Nabisa", kids=unknown(2)),
            P("Assainar", note="S'pore", kids=[
                P("Hairu"), P("Sura"), P("Jameela"), P("Rashid")]),
            P("K.Abdulla", kids=unknown(10)),
        ]),
        P("Kunhamina", kids=[
            P("Pathumma"),
            P("Nabissa", spouse="Razak"),
            P("Assya", spouse="Aseez"),
            P("Sabiya", spouse="Gafoor"),
            P("Basheer"),
        ]),
        P("Basheer", kids=[
            P("Maimun"),
            P("Pathuma", kids=[P("Roslan", note="Malaysia")]),
            P("Ibrahim")]),
        P("Pockerkka", kids=[P("Hamza"), P("Rukya"), P("Soora"), *unknown(10, "Malaysia")]),
        P("Moolur Moidu", kids=[
            P("Mulur Abdullah"), P("Kalathil Pathumma"), P("Khadija")]),
    ]),
    P("Salma", kids=[P("Mammed", note="Malaysia")]),
    P("Beeran Musaliar", kids=[
        P("Kunhi Modideen", kids=[
            P("Ismail Meladi", conf="?"), P("Kunhammed", conf="?"),
            *unknown(3, "Daughter")])]),
    P("Mohd Musaliar", kids=[
        P("Farhat Moideen Haji",
          note="Also appears in the Mother sheet (under Kunhaissa's line)",
          kids=[
            P("Mammed"),
            P("Safiya", kids=unknown(3, "Kattadi")),
            P("Salam", conf="?"), P("Aysha", conf="?"), P("Gafoor", conf="?"),
            P("Rahim", conf="?", kids=[P("Hina")]),
            P("Zubaida", conf="?"),
            P("Soora", conf="?", kids=[P("Basi"), P("Junaid")]),
          ])]),
    P("Hassan", note="children Kunhi Moideen & Thadiyan Mammed may belong here OR be gen-1 siblings",
      conf="?", kids=[
        P("Kunhi Moideen", conf="?", kids=[P("Siddique"), P("Hairu"), P("Kulsu")]),
        P("Thadiyan Mammed", conf="?", kids=[P("Yasser Arafat"), *unknown(3, "Daughter")]),
    ]),
])

# ---------------------------------------------------------------------------
# Flatten to a person list with ids + parentId, and emit JSON + outline
# ---------------------------------------------------------------------------
def slug(s, i):
    base = re.sub(r'[^a-z0-9]+', '_', s.lower()).strip('_')
    return f"p_{base}_{i}"

persons = []
counter = [0]
def walk(node, parent_id, sheet, depth, lines):
    sheet = node.get("sheet") or sheet      # a node can switch the sheet/provenance for its whole subtree
    counter[0] += 1
    pid = slug(node["name"], counter[0])
    persons.append({
        "id": pid, "name": node["name"], "parentId": parent_id, "sheet": sheet,
        "spouse": node["spouse"], "notes": node["note"], "confidence": node["conf"],
        "directLine": node["star"], "side": node.get("side"), "twin": node.get("twin"),
        "dob": node.get("dob"), "occupation": node.get("occ"),
        "spouseDob": node.get("spouse_dob"), "spouseOccupation": node.get("spouse_occ"),
    })
    marks = ""
    if node["star"]:        marks += " ★"           # direct line
    extra = []
    if node["spouse"]:
        sp = f"m. {node['spouse']}"
        sd = [x for x in (node.get('spouse_dob') and f"b. {node['spouse_dob']}", node.get('spouse_occ')) if x]
        if sd: sp += f" [{', '.join(sd)}]"
        extra.append(sp)
    if node.get("dob"):  extra.append(f"b. {node['dob']}")
    if node.get("occ"):  extra.append(node["occ"])
    if node["note"]:   extra.append(node["note"])
    suffix = f"  ({'; '.join(extra)})" if extra else ""
    lines.append("  " * depth + f"- {node['name']}{suffix}{marks}")
    for k in node["kids"]:
        walk(k, pid, sheet, depth + 1, lines)

# Merge: the Father family is the descent of Nelliadi's son Valiya Chekkan (m. Thithi).
mother["kids"][0] = valiya_chekkan
lines = []
walk(mother, None, "Mother/All", 0, lines)

data = {
    "meta": {
        "source": "family_tree.xls (hand-drawn chart, 2005)",
        "note": "Best-effort reconstruction. Nodes flagged confidence='?' need verification. "
                "Both sheets descend from one ancestor, Nelliadi Beeran Musaliar: the Father line's "
                "'Valiya Chekkan & Thithi' is Nelliadi's son Valiya Chekkan (m. Thithi).",
        "legend": {"directLine": "user's ancestry (Nelliadi Beeran Musaliar -> ... -> Sajith -> you)",
                   "confidence": "'ok' = clear in chart; '?' = parent link is a guess"},
    },
    "crossLinks": [
        {"marriage": ["Mariyomma (Mother)", "Rajab (Father)"], "children": "the 7 siblings incl. Fathima"},
        {"marriage": ["Fathima (Mother)", "Nangeri Aboobacker (Father)"],
         "children": ["Feroz", "Sajith", "Mujeeb", "Hafis"]},
        {"samePerson": ["Farhat Moideen Haji (Mother)", "Farhat Moideen Haji (Father)"], "note": "unverified"},
    ],
    "persons": persons,
}
with open("family_tree.json", "w") as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)

outline = ("PEROOLI FAMILY — NELLIADI BEERAN MUSALIAR (common ancestor)\n" + "="*60 + "\n" +
           "\n".join(lines) + "\n")
with open("family_tree_outline.txt", "w") as fh:
    fh.write(outline)

# ---- also emit nested data for the webapp (d3.hierarchy format) ----
import os
def to_d3(node, sheet):
    sheet = node.get("sheet") or sheet
    attrs = {"sheet": sheet}
    if node["spouse"]: attrs["spouse"] = node["spouse"]
    if node["note"]:   attrs["note"]   = node["note"]
    if node.get("marriage"): attrs["marriage"] = node["marriage"]
    if node.get("color"):    attrs["color"]    = node["color"]
    if node.get("emph"):     attrs["emph"]     = True
    if node.get("side"):     attrs["side"]     = node["side"]   # "mother" (pink) / "father" (blue)
    if node.get("twin"):     attrs["twin"]     = node["twin"]   # links a person's pink & blue copies
    if node.get("pic"):      attrs["pic"]      = node["pic"]    # circular photo (path under webapp/)
    if node.get("spouse_pic"): attrs["spousePic"] = node["spouse_pic"]   # married-in spouse's photo
    if node.get("dob"):      attrs["dob"]      = node["dob"]    # birth date, shown under the name
    if node.get("occ"):      attrs["occ"]      = node["occ"]    # occupation, small line in the card
    if node.get("spouse_dob"): attrs["spouseDob"] = node["spouse_dob"]   # spouse's birth date
    if node.get("spouse_occ"): attrs["spouseOcc"] = node["spouse_occ"]   # spouse's occupation
    d = {"name": node["name"], "attrs": attrs}
    kids = [to_d3(k, sheet) for k in node["kids"]]
    if kids: d["children"] = kids
    return d

# Single tree: Nelliadi Beeran Musaliar is the root / common ancestor of both sides.
webapp_root = to_d3(mother, "Mother/All")
webapp_root["attrs"]["root"] = True
os.makedirs("webapp", exist_ok=True)
# A content version stamped into the data file. The webapp appends it (?v=…) to image URLs so
# photos re-download only when the data OR the photo set (names/sizes) changes — otherwise cached.
import hashlib
payload = json.dumps(webapp_root, ensure_ascii=False)
_h = hashlib.md5(payload.encode("utf-8"))
_picdir = "webapp/pics"
if os.path.isdir(_picdir):
    for _fn in sorted(os.listdir(_picdir)):
        _h.update(_fn.encode("utf-8"))
        _h.update(str(os.path.getsize(os.path.join(_picdir, _fn))).encode("utf-8"))
family_ver = _h.hexdigest()[:10]
with open("webapp/tree-data.js", "w") as fh:
    fh.write('window.FAMILY_VER = "%s";\n' % family_ver)
    fh.write("window.FAMILY_DATA = " + payload + ";\n")

n_uncertain = sum(1 for p in persons if p["confidence"] == "?")
print(f"Total people: {len(persons)}")
print(f"Flagged for verification (uncertain parent): {n_uncertain}")
print()
print(outline)

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

def P(name, kids=None, spouse=None, note=None, conf="ok", star=False, marriage=None, color=None, emph=False):
    return {"name": name, "spouse": spouse, "note": note, "conf": conf, "star": star,
            "marriage": marriage, "color": color, "emph": emph, "kids": kids or []}

ASK = "Please let Mirza know if you know who belongs here."
def unknown(n, extra=None):
    """n placeholder '?' children for an Excel 'N children/daughters' count."""
    note = f"{extra} — {ASK}" if extra else ASK
    return [P("?", note=note) for _ in range(n)]

# ---------------------------------------------------------------------------
# MOTHER / ALL sheet  (root: Nelliadi Beeran Musaliar)
# ---------------------------------------------------------------------------
mother = P("Nelliadi Beeran Musaliar", [
    P("Valiya Chekkan"),   # NOTE: a different person from the Father sheet's "Valiya Chekkan & Thithi"
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
                  note="m. Rajab (Father sheet). Their children are the start of this family.",
                  kids=[
                    P("Fathima", star=True, spouse="N.A. Backer", marriage="fathima+nabacker", note="Mummy ❤️", kids=[
                        P("Feroz"),
                        P("Sajith", star=True),
                        P("Mujeeb", note="Listed as the original file's author"),
                        P("Hafis")]),
                    P("Khadija", kids=[P("Hafsa"), P("Salima"), P("Reshma"), P("Reetha")]),
                    P("K.Abdullah", kids=[P("Anna"), P("Ishan")]),
                    P("Safiya", kids=[P("Aamir"), P("Sabir"), P("Hiba")]),
                    P("Mumtaz", kids=[P("Fahad"), P("Eva")]),
                    P("Noorjahan", kids=[P("Shurook"), P("Diyana"), P("Suroor"), P("Mariyam")]),
                    P("Sabitha", kids=[P("Sana"), P("Muhammed"), P("Ayesha")]),
                  ]),
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
# FATHER sheet  (root: Valiya Chekkan & Thithi — a DIFFERENT Valiya Chekkan, NOT Nelliadi's son)
# ---------------------------------------------------------------------------
father = P("Valiya Chekkan & Thithi",
    note="'Porathut House' — a separate founding family, joined to the other side only by marriage.",
    kids=[
    P("Mariyam", kids=[
        P("Pathumma", star=True, kids=[
            P("Sulekha", kids=[P("Bavakka"), P("Ahmed"), P("Pokku")]),
            P("Rajab", star=True, spouse="Mariyomma", marriage="rajab+mariyomma", color="#3f74cf",
              note="m. Mariyomma (Mother sheet). Their children are detailed under Mariyomma — "
                   "tap the couple icon to jump there."),
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
        P("Khadisha", note="N.A. Backer's mother", kids=[
            P("N.A. Backer", spouse="Fathima", marriage="fathima+nabacker", color="#7eb3e8",
              note="Daddy ❤️ — m. Fathima (Mother sheet). Their children are shown under Fathima — "
                   "tap the couple icon to jump there."),
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
    counter[0] += 1
    pid = slug(node["name"], counter[0])
    persons.append({
        "id": pid, "name": node["name"], "parentId": parent_id, "sheet": sheet,
        "spouse": node["spouse"], "notes": node["note"], "confidence": node["conf"],
        "directLine": node["star"],
    })
    marks = ""
    if node["star"]:        marks += " ★"           # direct line
    extra = []
    if node["spouse"]: extra.append(f"m. {node['spouse']}")
    if node["note"]:   extra.append(node["note"])
    suffix = f"  ({'; '.join(extra)})" if extra else ""
    lines.append("  " * depth + f"- {node['name']}{suffix}{marks}")
    for k in node["kids"]:
        walk(k, pid, sheet, depth + 1, lines)

m_lines, f_lines = [], []
walk(mother, None, "Mother/All", 0, m_lines)
walk(father, None, "Father", 0, f_lines)

data = {
    "meta": {
        "source": "family_tree.xls (hand-drawn chart, 2005)",
        "note": "Best-effort reconstruction. Nodes flagged confidence='?' need verification. "
                "The two sheets are separate families joined only by marriage (Mariyomma x Rajab; Fathima x N.A. Backer).",
        "legend": {"directLine": "user's ancestry (Nelliadi Beeran Musaliar -> ... -> Sajith -> you)",
                   "confidence": "'ok' = clear in chart; '?' = parent link is a guess"},
    },
    "crossLinks": [
        {"marriage": ["Mariyomma (Mother)", "Rajab (Father)"], "children": "the 7 siblings incl. Fathima"},
        {"marriage": ["Fathima (Mother)", "N.A. Backer (Father)"],
         "children": ["Feroz", "Sajith", "Mujeeb", "Hafis"]},
        {"samePerson": ["Farhat Moideen Haji (Mother)", "Farhat Moideen Haji (Father)"], "note": "unverified"},
    ],
    "persons": persons,
}
with open("family_tree.json", "w") as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)

outline = ("MOTHER / ALL SHEET\n" + "="*60 + "\n" + "\n".join(m_lines) +
           "\n\n\nFATHER SHEET\n" + "="*60 + "\n" + "\n".join(f_lines) + "\n")
with open("family_tree_outline.txt", "w") as fh:
    fh.write(outline)

# ---- also emit nested data for the webapp (d3.hierarchy format) ----
import os
def to_d3(node, sheet):
    attrs = {"sheet": sheet}
    if node["spouse"]: attrs["spouse"] = node["spouse"]
    if node["note"]:   attrs["note"]   = node["note"]
    if node.get("marriage"): attrs["marriage"] = node["marriage"]
    if node.get("color"):    attrs["color"]    = node["color"]
    if node.get("emph"):     attrs["emph"]     = True
    d = {"name": node["name"], "attrs": attrs}
    kids = [to_d3(k, sheet) for k in node["kids"]]
    if kids: d["children"] = kids
    return d

webapp_root = {"name": "Perooli Family", "attrs": {"root": True}, "children": [
    to_d3(mother, "Mother/All"), to_d3(father, "Father")]}
os.makedirs("webapp", exist_ok=True)
with open("webapp/tree-data.js", "w") as fh:
    fh.write("window.FAMILY_DATA = " + json.dumps(webapp_root, ensure_ascii=False) + ";\n")

n_uncertain = sum(1 for p in persons if p["confidence"] == "?")
print(f"Total people: {len(persons)}  (Mother≈{len(m_lines)}, Father≈{len(f_lines)})")
print(f"Flagged for verification (uncertain parent): {n_uncertain}")
print()
print(outline)

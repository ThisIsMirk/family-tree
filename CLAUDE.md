# Perooli Family Tree — project context

An interactive web app of the **Perooli family** tree, digitized from a hand-drawn 2005 Excel
(`family_tree.xls`, 3 sheets: `Mother tree`, `All`, `Father`). The user (Mirza, mirza.abubacker@…)
is iteratively **verifying the tree branch-by-branch against the Excel** and giving corrections.

## How it works — THE BUILD PIPELINE (read first)
- **`build_tree.py` is the single source of truth.** It defines the whole tree as nested `P(...)`
  calls, then writes three outputs:
  - `family_tree.json` — flat person records (reference)
  - `family_tree_outline.txt` — indented human-readable outline (great for verifying)
  - `webapp/tree-data.js` — the nested data the web app loads
- **After editing the tree, run `python3 build_tree.py` to regenerate all three.**
  **NEVER hand-edit `tree-data.js`, `family_tree.json`, or the outline** — they're generated.
- The app is `webapp/index.html` (one self-contained D3 page; loads `tree-data.js` + D3 from CDN).

### `P()` node fields (in build_tree.py)
`P(name, kids=[...], spouse=, note=, star=, marriage=, color=, emph=)`
- `note` — shown only in the tap-to-open **detail card**, not inline. Preserve Excel metadata here
  (nicknames like `"Nalan Kutti"`, places like `"Singapore"`/`"Kattadi"`).
- `star=True` — on a person in the user's direct line (no longer drawn specially; legacy).
- `marriage="id"` — both spouses of a couple share an id → renders a ❤️ link + lets you
  tap to jump to the spouse elsewhere in the tree. (`partnerOf`/`navigate` in the app.)
- `color="#hex"` — colours that person's **lineage path** up to the root Nelliadi (pink Mariyomma & Assu,
  blue Rajab, light-blue Nangeri Aboobacker). All these paths now converge at Nelliadi.
- `emph=True` — bold/darken that person's **entire descent** (currently Mariyomma & Assu = the `blood` set,
  which is also what the ⌕ button / default view frames).
- `sheet="Mother/All"|"Father"` — overrides the source-sheet tag for that node **and its whole subtree**
  (used to keep the Father family tagged "Father" now that it lives inside Nelliadi's tree).
- `unknown(n, extra=None)` — helper returning `n` "?" placeholder children for an Excel "N children"
  count; each gets the note `"<extra> — Please let Mirza know if you know who belongs here."`
  Splice with `*unknown(7)` inside a kids list, or `kids=unknown(7)`.

## Key family facts (so corrections make sense)
- **ONE bloodline. The common ancestor of both sheets is `Nelliadi Beeran Musaliar`** (the tree root).
  ⚠️ UPDATED 2026: the Father sheet's `Valiya Chekkan & Thithi` **IS** Nelliadi's son **Valiya Chekkan**
  (m. **Thithi**) — the same man. So the whole Father family hangs under Nelliadi via Valiya Chekkan.
  (An earlier session had them as separate people; the user confirmed they are the same.)
- The "Mother/All" vs "Father" split is now just **source-document provenance** (the `sheet` attr), not
  two families. The two sheets still connect via marriages **Mariyomma × Rajab** and **Fathima × Nangeri Aboobacker** —
  now marriages between relatives who both descend from Nelliadi.
- User's line: Nelliadi → Thykkandi Mariyomma → Aysha → Khadija(Kundantavida) → **Mariyomma** (m. Rajab)
  → **Fathima** (m. **Nangeri Aboobacker**) → **Sajith** → the user. **Mujeeb** (the Excel's author) is the user's uncle.
- The grandparents **Fathima & Nangeri Aboobacker ARE blood-related** — both descend from Valiya Chekkan
  (Nelliadi's son) via siblings **Mariyam** and **Assya**.
- Tree is ~355 people and growing as dropped Excel data is recovered.

## Web app features
- Always **fully expanded** — branch collapsing was **removed** (elderly users hid family by accident).
  Tapping a **dot OR a name** both just open the detail card. No show/hide-children button.
- **Default view = the living family** (Mariyomma + all her descendants & Assu, i.e. the `blood` set),
  on both phone and desktop (`showFamily()` at boot).
- **Detail card**: spouse chip, lineage path, notes, source sheet. Selecting a person lights their
  **golden lineage** — it animates/draws outward from them, glowing+pulsing up to Nelliadi, calmer/thinner
  down through descendants; gold overrides the pink/blue/blood colours.
- Lineage colours: pink → Mariyomma & Assu, blue → Rajab, light-blue → Nangeri Aboobacker (all converge at Nelliadi).
- **Generation columns**: faint vertical dividers between depths + "Gen N" labels pinned at the top
  (Nelliadi = Gen 1). Labels auto-hide when zoomed out.
- **"?" branches** = unknown children from Excel counts; tapping shows "Please let Mirza know…".
- Search box with a live **suggestions dropdown** (each shows "Child of <parent(s)>").
- Bottom-right buttons: **desktop** = **＋ / − / ⌕**; **mobile** = **⤢ / ⌕**. ⌕ = zoom to the family,
  ⤢ = whole tree, ＋/− = zoom in/out. Camera moves **glide**.

## How the user works with you (norms)
- They give corrections like "X is the child of Y, has N kids …"; you edit `build_tree.py`, rebuild,
  and **verify with the outline** (and screenshots) before reporting.
- **Move data, don't duplicate it** when reparenting (they care about this a lot).
- **Preserve Excel metadata** (brackets/nicknames/places/counts) — don't drop notes.
- **Commit only when the user says so. Push only when explicitly told** — they've been keeping work
  **local** (currently several commits ahead of origin, not pushed). Default to NOT pushing.
- To preview without pushing: `cd webapp && python3 -m http.server 8765`, open http://localhost:8765/
  on this Mac. (The user's phone can't reach the LAN server because of a VPN.)
- Headless screenshots: Chrome at `--window-size=500,900` (it lays out ≥~500px wide and clips
  narrower shots, which can make bottom-right buttons look missing — they're fine).

## Git / deploy
- Repo **ThisIsMirk/family-tree** (gh CLI authed as ThisIsMirk), **public**, on GitHub Pages:
  **https://thisismirk.github.io/family-tree/** (root `index.html` redirects to `webapp/`).
- Pushing to `main` auto-redeploys Pages in ~1 min.
- End of last session: everything committed **and pushed**; working tree clean; live site current.
  Always run `git status` / `git log` to confirm the present state, and **push only when the user asks**.

## Open items
- More Excel data may still be missing (user is recovering it branch by branch).
- The living/current generation (the user, cousins) is not in the tree yet.
- Optional later: GEDCOM export from `family_tree.json`.

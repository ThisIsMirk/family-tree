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
- `marriage="id"` — both spouses of a cross-sheet couple share an id → renders a 💑 link + lets you
  tap to jump to the spouse on the other sheet. (`partnerOf`/`navigate` in the app.)
- `color="#hex"` — colours that person's **lineage path** from the founder (pink Mariyomma, blue Rajab).
- `emph=True` — bold/darken that person's **entire descent** (currently Mariyomma & Assu).
- `unknown(n, extra=None)` — helper returning `n` "?" placeholder children for an Excel "N children"
  count; each gets the note `"<extra> — Please let Mirza know if you know who belongs here."`
  Splice with `*unknown(7)` inside a kids list, or `kids=unknown(7)`.

## Key family facts (so corrections make sense)
- **TWO separate founding families, joined ONLY by marriage** (NOT one bloodline):
  `Nelliadi Beeran Musaliar` (Mother/All sheets) and `Valiya Chekkan & Thithi` (Father sheet).
  ⚠️ The "Valiya Chekkan" who is Nelliadi's son is a **different person** from "Valiya Chekkan & Thithi".
- The two sheets connect via two marriages: **Mariyomma × Rajab** and **Fathima × N.A. Backer**.
- User's line: … → Khadija(Kundantavida) → **Mariyomma** (m. Rajab) → **Fathima** (m. **N.A. Backer**)
  → **Sajith** → the user. **Mujeeb** (the Excel's author) is the user's uncle.
- The grandparents **Fathima & N.A. Backer ARE blood-related** (~2nd cousins once removed) — both
  descend from `Valiya Chekkan & Thithi` (via siblings **Mariyam** and **Assya**).
- Tree is ~355 people and growing as dropped Excel data is recovered.

## Web app features
- Loads **fully expanded**, opening anchored on the founder (Nelliadi). Tap a **dot** to collapse/expand;
  tap a **name** to open the detail card (spouse chip, lineage, notes, sheet).
- Pink lineage → Mariyomma, blue → Rajab; their descent drawn darker/bolder.
- **"?" branches** = unknown children from Excel counts; tapping shows "Please let Mirza know…".
- Search box; big Mother/Father vertical gap (`sideOf` separation).
- **Two buttons** bottom-right: **⤢** = see the whole tree, **⌂** = back to the opening view.

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
- As of this handoff: latest commit `4f5a9dd`, **4 local commits ahead of origin (un-pushed)**, plus
  **uncommitted working changes** (removed the "needs-verifying" flags from the UI; reduced the
  bottom-right controls to the two buttons above). Run `git status` / `git log` to confirm current state.

## Open items
- More Excel data may still be missing (user is recovering it branch by branch).
- The living/current generation (the user, cousins) is not in the tree yet.
- Optional later: GEDCOM export from `family_tree.json`.

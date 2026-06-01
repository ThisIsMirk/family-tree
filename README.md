# Family Tree

A digitized, interactive version of a hand-drawn family tree (originally an Excel chart from 2005,
rooted at **Nelliadi Beeran Musaliar**).

## What's here

| Path | Description |
|------|-------------|
| `family_tree.xls` | The original hand-drawn chart (3 sheets: Mother / All / Father). |
| `family_register.csv` / `.xlsx` | Every name extracted into a clean, structured table. |
| `family_tree.json` | The full connected tree as structured data (287 people, with parent links, spouses, notes, and confidence flags). |
| `family_tree_outline.txt` | A human-readable, indented version of the tree for review. |
| `build_tree.py` | Authoring script. Edit the tree here, then re-run to regenerate the JSON, outline, and webapp data. |
| `webapp/` | A mobile-first interactive viewer (see below). |
| `source_images/` | Upscaled crops of the original chart, used to reconstruct the relationships. |

## Viewing the tree

The webapp is a single static page (uses [D3](https://d3js.org/) from a CDN). To run it:

```bash
cd webapp
python3 -m http.server 8765
# then open http://localhost:8765/
```

**Features:** pinch/scroll to zoom, drag to pan, tap a dot to expand/collapse, tap a name for details,
search any name, and a **★ My Line** button that frames the highlighted direct lineage.

- **Gold** = the direct ancestral line.
- **Orange dashed** = a parent link that is a best-guess and still needs verifying (61 of these).

## Regenerating the data

After editing the tree in `build_tree.py`:

```bash
python3 build_tree.py
```

This rewrites `family_tree.json`, `family_tree_outline.txt`, and `webapp/tree-data.js`.

## Status

First-pass reconstruction. The sibling groups and their children are solid; the 61 links flagged
`"confidence": "?"` (orange-dashed in the app) are best guesses for *which parent a group hangs from*
and should be confirmed by family members. The living/current generation is not yet included.

# Asset restore - how any task (scheduled or manual) gets music, backgrounds, cutouts in a fresh workspace
All big files live in GitHub release assets of Rodantmat/Alphadog-Styles (use `gh api`, auth already set). Catalogs are in the repo. Run these FIRST in a fresh workspace; then build.
| Asset | Count | Catalog (in repo) | Restore |
|---|---|---|---|
| Music clips (45 s, 128 kbps, Mixkit free license) | 1,017 tracks (+67 unused-theme) with bpm / energy / theme | docs/music_catalog.json | `python3 scripts/video/pick_music.py restore` (-> out/musiclib/clips/mxNNN.mp3) ; pick with `pick_music.py pick STYLE` ; commit with `commit` |
| Background photos (real, CC0) | 6,026 (3,988 HDRI views, 2,038 textures) | docs/bgcat/catalog_*.json (copy to out/bgcat/) | for s in 0..7: download zips + catalog from release `bgphotos_s$s`, unzip into out/bg (see scripts/bgfetch.py / bg-fetch.yml) ; pick with scripts/video/bgmatch.py (kinds person, closeup, flat, folded, scenery) |
| Printify transparent cutouts | 95 PNG (7 products) | docs/printify_cameras.json, docs/cutout_blocklist.json | release `mocktrans` -> out/trans ; refresh with workflow mocktrans / docs/PRINTIFY_TRANSPARENT.md |
| Merch library (5,159 trimmed items) | 5,159 | docs/merch_lib_catalog.json | D: drive merch_library or release merch-cutouts-v1 -> out/merch_lib |
| People backgrounds (legacy procedural) | 300 | docs/backgrounds_people_catalog.json | superseded by real photos; `python3 social/people_bg/bg_people.py out/bg_people` |
Rebuild music library (new tracks): workflows music-crawl then music-build (8 shards), then merge catalogs into docs/music_catalog.json.
Rules before using any asset: docs/RULES_LEDGER.md, docs/VIDEO_MODELS.md; always `python3 scripts/video/variation.py check ENTRY.json` before building/scheduling a Post A.

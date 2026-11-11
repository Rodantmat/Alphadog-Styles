# Post A video models - same concept, everything inside changes (owner 2026-11-10, permanent)
Machine-readable: docs/video_models.json. Enforcement: `python3 scripts/video/variation.py brief DATE | check ENTRY.json | commit ENTRY.json`. A video is NOT built or scheduled until `check` prints OK.

## The models (7 reel models + 2 laugh models; rotate, never the same model twice in a row, least-recently-used first)
| Model | Fixed (the concept) | Always changes |
|---|---|---|
| laugh4 (Mon) | 4 dogs, snap-to-laugh, crowd laugh, layout | NEW joke every time (never repeated), background (structurally different), music, laugh track, merch mix |
| laugh2 (Thu) | 2 dogs (chihuahua + yorkie), snap-to-laugh | NEW joke, background, music, laugh track, merch mix |
| d1 snack gag | the gag format | breed, merch, bg, music, gag |
| d2 shades vs ours | real dog in shades vs our design | breed, merch, bg, music |
| d3 scenery tees | merch ON REAL SCENERY (landscape / city / skyline / nature / sunset / night photos; never flat or procedural) | breed, merch, scenery photo, music |
| d4 line-art hoodies | line by line drawing | breed, merch, bg, music |
| d5 breed compilation | fast funny breed cuts | breeds, merch, bg, music, captions |
| d6 neon sign | neon sign look | ONE breed per week (no breed again until all breeds have had a week), different merchandise type, different colour, different neon colour, music |
| d7 which one is yours / which back | interactive pick | breeds, merch, views, bg, music |

## What `variation.py check` enforces
- not the same model as the previous video; Mon = laugh4, Thu = laugh2 only
- primary breed not used in the last 4 videos; neon: exactly one breed, never repeated until all breeds used, neon colour required
- merch: no two items sharing product + colour family inside one video; >= 3 different views (back print / big face / small emblem / full dog) when 4+ items; no repeat of product / colour / design vs the previous video
- backgrounds: never reused within 60 days, no duplicates inside a video; d3 must use real scenery (pg_* photo, kind "scenery" in bgmatch)
- music never reused (also pick_music.py: style themes, bpm, never same theme as neighbour); joke never reused; laugh track never reused

## Where each ingredient comes from (see docs/ASSET_RESTORE.md for restore commands)
- music: docs/music_catalog.json + release assets musiclib_s* (pick via scripts/video/pick_music.py)
- backgrounds: docs/bgcat/catalog_*.json + release assets bgphotos_s0..s7; `scripts/video/bgmatch.py` (kinds person / closeup / flat / folded / scenery)
- cutouts: release mocktrans (Printify transparent PNGs), merch library on D: drive / merch-cutouts release
- jokes: never repeat; keep docs/jokes_used.json via the registry (field joke)

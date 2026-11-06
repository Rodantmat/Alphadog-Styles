# Post A weekly rotation + variation rules (owner rules, 2026-11-06)
Post A = morning reel (9am PT weekdays / 10am weekends), ONE day at a time.
Weekly 7-day window: day 4 = MONDAY = 4-dog "dogs laugh" video (social/laugh/build.py + jNN json). day 7 = THURSDAY = 2-dog laugh video (social/laugh/build2.py: chihuahua + yorkie, out/footage3). Other days rotate the existing video models (social/videos d1..d7 styles).
Old d1 (boston-snack-gag) and d6 (neon-sign) moved to the end of the line (first reuse Fri Nov 13 / Mon-after, as new variations).
## Every re-creation MUST change
merchandise, merch colour, merch design, background, music. Funny videos: same dogs, same snap-to-laugh effect + crowd laugh, NEW dog-related joke each week, new background + music. Breed joke -> that breed's merch; otherwise assorted merch (kinds, colours, front/back, full dog/head). Finale = 4 corners + middle, hold ~2 s, never covering text.
Backgrounds (texture + colour) and music may repeat only after 2 months. Never the same video style back-to-back (rotate). Log every video in docs/style_registry.json (date, type, background, music, merch, joke) BEFORE scheduling and check it.
## Assets
Trimmed merch library: out/merch_lib/<cat>/<breed>/<code>.webp (RGBA, black-bg tested; code = design digit + colour). Builder scripts/video/merch_lib.py. Released as GitHub release asset merch-cutouts-v1 when complete.
Laugh template config examples: social/laugh/j01_labrador.json, j02_pupperoni.json (bg via "seed" + "pal"{c1,c2,ink}).

## Merch placement rule (owner, 2026-11-06)
Every finale mixes placement/views: back print (library file <code>_back.webp = big full-dog back), big face on the front (designs 2 and 5), small chest emblem (designs 1,3,4), plus different product types, colours and designs. Backgrounds must be structurally different (social/laugh/bgs.py: sunburst, checker, dots, stripes, chevron, stars, hexes; paws only for laugh01), never just a recolour. Laugh track also changes (out/sfx: 424 used by 01, 422 by 02; others 423, 460, 512, 516).
Layout: joke fixed on top the whole time, dog tiles centred below with wiggle space, answer under them, merch big (finale 4 corners + middle, ~2 s hold).

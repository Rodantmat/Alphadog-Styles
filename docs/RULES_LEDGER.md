# AlphaDog Styles - owner rules ledger (tally)
Every rule the owner has stated, with WHERE it is enforced in code and its status. Read before any build; update the moment a new rule or correction arrives.
Status: ENFORCED = code blocks a violation; CHECKED = verified by a script after the fact; MANUAL = only a written rule (must become code); OPEN = known violation being fixed.
Last audit: 2026-11-10.

## Product / print
| ID | Rule (owner) | Where enforced | Status |
|---|---|---|---|
| P1 | Brand logo only on the INSIDE neck label, with the brand name, never printed on the outside (docs/03) | scripts/printify_labelfix.py + workflow printify-labelfix (removes outer logo, fixes neck); printify_extras.LABEL must never use back/hat positions | FIXED Nov 10: removed outside logo from 198 polos + 9 cap test products (scan certified 0 remaining); printify_extras no longer adds it. Re-run printify-labelscan after any product build |
| P2 | Label ink in tone with the garment: black ink on light garments, white ink on dark; never trespasses the fabric | printify_labelfix.py (neck ink must equal the artwork ink) | FIXED Nov 10: 17 old v1 labels moved to v3; all live necks are v3 logo+name, tone matches art |
| P3 | Light garments black-ink art, dark garments white-ink art; white lines not too thin | art analyzer (docs/05) | CHECKED |
| P4 | Use only approved art (BLACK_CARDS_v2) | manual | MANUAL |
| P5 | Printify may hold old unapproved dark versions - never use | manual | MANUAL |
| P6 | A listing/mockup must never show a product that is wrong (missing design, outside logo, cut art) | printify_audit.py + labelscan; cutout_blocklist for videos | CHECKED: labelscan certifies placement; run after every product build |

## Video / post
| ID | Rule | Where enforced | Status |
|---|---|---|---|
| V1 | Never same colour / merch type / design back-to-back | postc2_build.order() cost | ENFORCED (verify per build) |
| V2 | Every shot must show the dog design clearly; no cut-off, no tag-only | docs/cutout_blocklist.json via postc_build.pool() | ENFORCED (75 cutouts reviewed by eye) |
| V3 | One image per frame, never split/stacked; 40% people (4 different); fades; never repeat person/merch/design/breed | postc2_build | ENFORCED |
| V4 | Text never over merch; hook top, CTA bottom | postc2_build add_text positions | CHECKED by frame review |
| V5 | 8-10 s long, phone-safe 1080x1920 | postc2_build (10.0 s) | ENFORCED |
| V6 | Never repeat music (log) / backgrounds within 60 days | pick_music.py commit, bgmatch used log | ENFORCED if commit step runs |
| V7 | Transitions: slow, each clip once, no return | postc2_build (fixed Nov 10) | ENFORCED |
| V8 | Backgrounds real, textured, premium, matched to garment | bgmatch + 6,026 library | ENFORCED |
| V9 | Absolute ban on look-alikes between reels | postc2_build.py: env C2_EXCL=<reel ids> (no camera, person, background or breed shared with those reels), distinct breed/colour/person inside a reel; cutout library = release `trans2` (docs/trans2_plan.json, restore: unzip into out/) | ENFORCED for Post B C2 (Nov 10); Post A still via variation.py |
| V10 | Post A morning, Post B ~8 pm PT; 2 posts/app/day; verify every post actually posted | scheduled tasks + checker | CHECKED |

| V11 | Post A: same concept, everything inside different (breed, merch, placement, style, bg, music); neon = 1 breed/week; scenery = real photos; jokes never repeat | scripts/video/variation.py + docs/video_models.json | ENFORCED (needs scheduled-task prompts to call it) |
| V12 | Extensive music library, never repeat, retrievable by any task | docs/music_catalog.json (1,017) + pick_music.py restore + docs/ASSET_RESTORE.md | ENFORCED |

## Process (how I work)
- Before delivering any video: contact-sheet EVERY shot at <=0.2 s spacing, confirm design visible on each garment, confirm no look-alike. (Learned Nov 10: certified without looking for the neck-logo defect.)
- A defect found anywhere = fix the cause in the source (live product, pipeline, rule), not just hide the item.
- Every owner correction is added to this ledger the same day.

- 2026-11-11 run note: Post A bg must differ from same-day Post B bgs (register A bg in docs/bg_used.json BEFORE building B); variation.py commit must run BEFORE pick_music.py commit (check flags music already used). Engine needs pip: cairosvg pymatting librosa + stub rembg + /home/claude/passive-income/brand/alphadog_logo.png (copy of refs/alphadog_logo.png).

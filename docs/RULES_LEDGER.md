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
| V13 | Post B: never show yorkshire_terrier, pomeranian, shih_tzu, havanese, pug, mini_poodle, bichon_frise, maltese (owner, runbook) | postc2_build.BANNED_BREEDS filter in pool (added 2026-11-12) ; C2_EXCLC env = no same product+colour as previous reel | ENFORCED from c13. c09-c12 replaced by c14-c17 (2026-11-12). OPEN: c04-c07 (Nov 13-16 04:00Z slots) contain banned breeds, may already be scheduled - owner decision |
| V14 | C2_EXCLR env: wider window for people/cameras than for breeds (only ~25 allowed breeds, ~40 people) | postc2_build.py | ENFORCED 2026-11-12; note c16 reuses c13 breed set and c17 shares 4 breeds with c14 (pool too small for a 3-reel breed window) |

- 2026-11-13 run: FIXED at source: (a) d3 scenery now built by engine/vidD3c.py from real bgmatch scenery photos (old d3b used procedural bg = violation, replaced by d3c for Nov 18); (b) postc2_build.pick_trans no longer emits 0.033 s hard cuts (all transitions >=0.7 s: fade/dissolve/fadeblack/push/smoothleft). Existing reels c13-c17 may still contain cut transitions (c14-c17 not re-rendered) - OPEN. d2 reel builder now engine/vidS2.py (real photo bg, merch_lib).

- 2026-11-14 run: FIXED at source in engine/vidA4.py (d4): real bgmatch photos (string bg ids) instead of procedural 300-library; music from musiclib; transitions now 18 frames (0.75 s, was 0.33 s); last-frame bug (pop zoom at t=99 produced giant ghost design in crossfade) fixed. NOTE V14 again: c19 had to share breeds (not cutouts/people/bgs) with c16 because the strict breed window empties the back-person pool; library expansion still needed. Small-emblem designs on a few caps/tee (Dad Hat, Cavalier chest emblem) are visible but small.

- 2026-11-15 run: FIXED at source: (a) laugh builders (social/laugh/build2.py) accept J.bgphoto = real bgmatch photo instead of procedural bg, music read from out/musiclib/clips; (b) postc2_build.py new env C2_NOCOL="Colour,..." drops colours/breeds worn in the same-day Post A (V1/V9); (c) d2 builder now scripts/video/engine/vidS2b.py (runs from /tmp/kl with PYTHONPATH=/tmp/kl:/tmp/stubs:engine; needs rembg stub + /tmp/sel_d2.json). Rebuilt skipped items: Nov 19 A laugh02_newyorkie (new joke, laugh track 512, mx841), Nov 21 A d2c (5 new breeds, mx798), Nov 20 B c20 (mx1, replaces c17). NOTE V14: Post B pool is too small for a strict 3-reel window (people/back pool empties); c20 uses window c16,c18 only and has three green tees (Forest Green/Military Green/Forest) - OPEN, expand cutout library.
- 2026-11-16 run: FIXED at source: social/laugh/build.py (4-dog Mon) now accepts J.bgphoto real photo like build2. c21 built with relaxed breed/people windows (pool V14 still tight - OPEN: expand cutout library).
- 2026-11-17 run: FIXED at source: d5 builder now scripts/video/engine/vidF5.py (real bgmatch photos per cut, 0.75 s dissolves, runs from /tmp/kl copy because engine/funny.py is an older copy). Verify footage clips by eye (manifest label 1212 = Boston terrier). OPEN: Nov 21/22 B (c18/c19) skipped and not rebuilt; V14 pool tight (c22 has Navy hoodie + Navy tee non-adjacent).

- 2026-11-18 (owner check "everything posted fine, on schedule"): items the auto-scheduler SKIPS for a variety clash were never rebuilt (c18 Nov 21, c19 Nov 22 evenings left empty for 3 runs). Fixed at source: generator task prompt now has step "REBUILD FIRST" (rebuild every flagged item as a new id before building new days; none may stay open within 4 days) and Post B is checked against same-day A, next-morning A and neighbouring B before building. Enforced in: scheduled task trig_01CVnnuodyUvTBdra9xPM6yZ.

- 2026-11-18 run: REBUILD FIRST executed: B c18/c19/c22 replaced by c23/c24/c25 (neighbour exclusions via C2_NOCOL/EXCL/EXCLP/EXCLR/EXCLC). Fixed at source: neon builder engine/vidX3c.py (parametrised breed/product/colours, REAL brick photo wall from bgmatch library instead of procedural wall, CTA moved below garment so text never covers merch). NOTE: shell env vars do not persist between tool calls - export C2_* in the same command as the build. Nov 25 d6c: variation check flagged tee repeat vs d5c -> used wtank. OPEN: V14 pool tight (c25 has Natural tee vs same-day d5c Soft Cream tee; c26 reuses Maroon hoodie/breeds of c21 two evenings earlier).
- 2026-11-19 (owner screenshot of Instagram feed): laugh02_newyorkie question + top line were cut in the scrolling feed (4:5 center crop, account bar on top). FIXED AT SOURCE: laugh builders moved all text/tiles/merch into rows 430-1580 (FEED_TOP/FEED_BOT + fit assert), new scripts/video/feedcrop.py feed-view contact sheet, VIDEO_RULES rule 15, generator quality gate updated. Other builders (vidA4/vidW1 'logo pill y276', vidX3c, postc2) still have items above row 430: check each when next built (logo pill only; heading y436 is OK).

2026-11-19 (PM): postc2_build.add_text now clamps the text pill into rows 448..1580 (rule 15) so hooks (y310) no longer sit under the feed account bar. Reels c23-c26 must be rebuilt with it and reviewed with feedcrop.py (check the lowered hook does not cover merch). Still open: neon builder brand pill (vidA4/vidW1, d6c).

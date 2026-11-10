# PRINTIFY TRANSPARENT CUT-OUTS - the ONLY approved way to trim Printify pictures (owner Rodo, 2026-11-09, permanent)
Why: every AI/matting trim we tried (rembg, isnet, pymatting, flat-bg analytic) left white hair fringes, white in arm gaps/armpits, cut-off people, ruined white caps. The owner rejected all of it.
Researched fix: Printify's Mockup Library has a "Download > Transparent" option. It is served by Printify's image server as a real RGBA PNG - exact hair, see-through cap mesh, true brim edges. It needs no login.

## The call
https://images.printify.com/mockup/{pid}/{variantId}/{cameraId}/x.png?camera_label=front&t={epoch_ms}&s=2048&transparent_background=true&use_cache=false
- pid = Printify product id (out/mockidx/catalog.tsv.gz col 0), variantId = colour/size variant in the catalog URL, cameraId = which picture (docs/printify_cameras.json).
- Camera ids work for EVERY colour/variant of the product (colour = variantId). Size does not matter for the picture; pick a variant of the colour wanted.
- Result 2048x2048 RGBA. Tight-crop to the alpha bbox (alpha>6). transparent fraction < 0.08 = the picture is a SCENE (plant, couch, chair, flat-lay): Printify does not cut those.
- Helper: scripts/video/ptrans.py (fetch/url/usable). Workflow printify-trans.yml pulls a whole product set. images.printify.com is reachable ONLY from GitHub Actions runners, not from the Claude sandbox; GitHub artifacts cannot be downloaded in the sandbox but release assets can (gh api .../releases/assets/ID with Accept: application/octet-stream).

## Rules
1. All posts, Post A merch, Post B, laugh videos, store/marketplace composites: trimmed pictures come from ptrans, never from AI background removal.
2. Never use size charts (camera kind chart) or blank hats (kind blank). Women's Polo has only illustrations: never use.
3. Scenes (kind scene) are posted AS-IS: full-bleed cover crop to 1080x1920, subject kept inside the phone-safe area, no cut-out, no overlay on the garment.
4. People pictures (kind person) are cut off at the waist/thigh by Printify: anchor them to the BOTTOM edge of the frame (bleed off), centred or per-layout, on people-friendly backgrounds (docs/backgrounds_people_catalog.json).
5. After any pull, build a black-background contact sheet and look at it; also run scripts/video/ptrans_qa.py (alpha sanity: transparent fraction, no border-touching opaque rim, bbox ratio).
6. Camera map is the source of truth for what each picture is (flat_front/back, folded, hanging, closeup, person front/back/side, scene). New products: run printify-trans on one variant, view the sheet, add the map entry.

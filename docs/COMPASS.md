# COMPASS - AlphaDog Styles: read this first when anything is unclear
Owner: Rodo (San Diego, ALL times Pacific). Wife Jessi reviews designs. Repo: github.com/Rodantmat/Alphadog-Styles (public; keep public to avoid Actions charges). Budget: Cloudflare $5/mo + GitHub $4/mo plans, no extra costs.
Owner style: wants instructions followed exactly, everything automated, Claude runs workflows itself (never asks him), final results not logic, no questions for things Claude can find. A video/asset he has seen and not asked to change = approved.

## 1. Business and stores
- Brand AlphaDog Styles: dog-breed apparel (33 breeds x themes continuous-line/geometric/silhouette; Classic/Cool/Heart; light garments black ink, dark garments white ink; custom dog design for $19.99). Made to order via Printify (Bella+Canvas 3001 tees, Gildan 18500 hoodies, tanks, polos, caps; brand label inside neck/hat). US-only shipping for now; free shipping built into prices; approved per-channel price table must not be changed ad hoc.
- Own store alphadogstyles.com (Cloudflare domain, store/ in repo: Cloudflare worker + DigitalOcean Postgres, Stripe (sandbox first; live account under Flipping Magic LLC), Resend email, Google login + email registration (no Apple/Facebook), custom design flow #/custom, full variant flow). Deploy: workflow store-deploy.yml; fulfil: store-fulfill.yml sends paid orders to Printify (orders@alphadogstyles.com bridge).
- Marketplaces (never cancel orders, no real test orders, protect seller standing): Etsy AlphaDogStyles (61 consolidated listings), eBay user alphadogstyles (~100 listings, API keys in secrets), TikTok Shop Alphadogstyles (~80 of 100 slots; edit, never delete). Sale notifications go to flippingmagic.sales@gmail.com; marketplace orders bridged to Printify like the own store.
- Support: customers write support@ / customization@alphadogstyles.com (inbox in store DB). Scheduled task "AlphaDog support assistant" (trig_013oh4T32RB5BZzhTxiMYK2r, hourly :21) answers via workflow store-support.yml (actions list/orders/custom/reply/done); money/orders decisions are escalated to the owner by email "[Support needs you]". Policies: no returns for change of mind; damaged/misprint within 30 days = free reprint/refund; production 2-5 days, shipping 3-7.
- Other owner assets: Flipping Magic LLC (Amazon seller, separate and must never be put at risk). Mail infra: mail/ (own mail server scripts). Printify, eBay, Etsy tokens are GitHub secrets (never printed).

## 2. Social structure (brand handle alphadogstyles)
- TikTok, Instagram, Facebook Page, Pinterest ("AlphaDog Styles" board serviceId 1133710974888199746). Instagram<->Page link blocked by Meta (given up). Everything posts through Buffer: account 1 (secret BUFFER_API_KEY) = Instagram + TikTok, account 2 (BUFFER_API_KEY_2) = Facebook + Pinterest. Buffer limit: 10 scheduled posts per channel. Helper social/buffer.py, workflow buffer-run.yml (inputs account=1|2, args = posts | plan FILE | delete IDS).
- 2 posts per app per day: Post A (creative video, 9:00 PT weekdays / 10:00 PT weekends), Post B (Printify mockup reel, 20:00 PT). Videos ~8-10 s, phone-safe areas, logo top-right, "AlphaDog Styles" bottom, brand link/CTA never over merch, textured bright backgrounds.
- A separate project (AlphaDog Studio / Yellowstone YouTube etc.) lives in repo Rodantmat/Alphadog-Social with its own tasks - not part of this brand.

## 3. Video system (read docs/VIDEO_RULES.md, docs/video_rotation.md, docs/PRODUCTION_RUNBOOK.md)
- Weekly: Mon = 4-dog laugh (social/laugh/build.py), Thu = 2-dog laugh (build2.py), each week NEW joke, background, music, laugh track, mixed merch; other days rotate models d1-d7 with new bg/music/merch; never same style/colour/product/design back-to-back. The owner adds a new Post A model now and then; add it to docs/music_style_map.json and docs/style_registry.json and use it as new base content.
- Post B: full-screen Printify mockups (social/postb/build2.py, PLAN env), popular breeds, varied dark shades, people views, banned breeds (yorkshire_terrier, pomeranian, shih_tzu, havanese, pug, mini_poodle, bichon_frise, maltese).
- Libraries: merch cutouts (5,159) and 300 backgrounds (never reuse a background within 2 months), 300 themed songs out/music2 matched to video style (docs/music_style_map.json, enforced by scripts/video/pick_music.py; never reuse a track). QA: scripts/video/qa2.py, defringe.py, repair_lost.py.
- Registries: docs/style_registry.json, docs/music_log.md + music_used.json, docs/schedule.json (internal schedule to ~day 16/17), social/POSTLOG.md, social/GENLOG.md.

## 4. Storage and access
- Code/catalogs: repo main. Heavy libraries (merch_lib, backgrounds, kl engine, footage/media): repo branch prod-assets as split zips (restore steps in docs/PRODUCTION_RUNBOOK.md); owner's copy on D:\Rodo\Projects\AlphaDog Styles\merch_library (+ Videos folder for finals). Repo must be cloned at EXACTLY /home/claude/alphadog-styles (scripts hardcode it).
- Access from cloud sessions: add_repo (push) tool, gh REST only (GraphQL, releases and the secrets listing are blocked by the proxy). Run workflows with gh api -X POST .../actions/workflows/FILE/dispatches -f ref=main -f inputs[x]=y; read logs with gh api repos/.../actions/jobs/ID/logs. Alphadog_Bridge MCP offers GitHub/db helpers. Secrets live in GitHub Actions (never print). Device bridge to the owner's PC only when linked.
- Claude workspace is ephemeral; anything needed later must be in git (or D: via bridge).

## 5. Scheduled tasks (Claude scheduled tasks; owner asked for these)
- Auto-scheduler trig_01LcKHogXtrybwxQ7U2eBU5P daily 12:12 PT: verify sent, repost misses, fill Buffer from docs/schedule.json in date order.
- Content generator trig_01CVnnuodyUvTBdra9xPM6yZ daily 14:47 PT: keep 7-day lead of built A+B, quality gate, music via pick_music.py, cleanup.
- Post checker trig_016ysqez1G5AocRMNmP2aEsz daily 9:34/10:34/20:34 PT: 30 min after each slot, forces any missing post in (delete stuck, re-plan now+5 min).
- One-shot trig_01FCu7RYnTjj88zxjSDmxmD3 (Nov 7 9:10 PM PT) tops up Post B b08/b09. Support assistant (hourly). Other tasks in the account belong to the Studio/NBA projects.
- All write progress to social/GENLOG.md / POSTLOG.md; check them first when something is off. A run that ends in minutes without output is a failure.

## 6. Rules recap (details in repo docs; owner statements are binding)
No repeat of music/background within 2 months (music never); never same colour/product/design back-to-back; no text over merch; cutouts must pass qa2 (no white edges/cut-off); dark garments use varied dark shades; missed posts must be reposted at once; never touch posted items; keep things simple and clean; save libraries on D: or GitHub, do not send them in chat; no real orders; do not harm marketplace standings.

## 7. Next big project: Colombia and Brazil (to study, then automate fully)
- Brazil: owner's mother is seller of record; Paolla Oliveira (cousin) may promote; Brazilian POD + Mercado Livre + own store, all via API. Colombia same idea. Workflows printify-brazil.yml and printful-brazil.yml already exist (earlier probes).
- Plan: study local print-on-demand with API (Brazil: e.g. Printi, Camiseteria/Dreamy, Printify/Printful shipping to Brazil; Colombia: local POD options), marketplaces (Mercado Livre BR/CO, Shopee, Amazon BR), payment (Pix, Mercado Pago, Wompi/PayU), tax/legal, shipping/customs, language (pt-BR/es-CO) for designs, posts and support; decide per country using numbers (cost, delivery time, fees, margin); keep it fully automated like the US arm. Present all options with numbers before deciding (owner decides).

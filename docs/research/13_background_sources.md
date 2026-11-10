# 13 - Background sources for 300+ "elite" 9:16 reel backgrounds (AlphaDog Styles)

Research date: 2026-11-10. Method: WebSearch (standard) to discover URLs (the WebFetch allowlist only accepts URLs surfaced by search), then WebFetch to read. Reddit not used.
**Pages fetched: 51** (pages that returned usable content). A further 18 fetch attempts failed (not on allowlist, redirect, or server error) and are listed after the table; they are NOT counted. Several pages returned only partial information; that is noted in "key takeaway".
Repo note (names only, repo not accessible): `Rodantmat/Alphadog-Styles` is said to contain `scripts/video/pexels.py`, `unsplash.py`, `picsum.py`. Not verified. Important: picsum.py (Lorem Picsum) is a placeholder service whose photos are Unsplash-sourced; it is not a licence-clean production source (see risks).

## (a) Log of fetched pages

Reliability: H = official/primary doc, M = reputable secondary or partial page, L = blog/aggregator/AI-summarised or thin.

| # | URL | What | Key takeaway | Rel. |
|---|---|---|---|---|
| 1 | https://www.pexels.com/api/documentation/?language=javascript | Pexels API docs | Key in `Authorization` header. 200 req/h, 20,000/mo default. `/v1/search` params: query, orientation (portrait), size (large 24MP/medium 12MP/small 4MP), color, per_page<=80. `src.original`, `src.portrait` (800x1200 crop). Must show prominent Pexels link/credit. | H |
| 2 | https://help.pexels.com/hc/en-us/articles/900005852323 | Pexels API terms | Allowed: build on app with value beyond API. Not allowed: wallpaper apps, copying core functionality, selling unaltered copies. Must credit Pexels and send proof of attribution to api@pexels.com. | H |
| 3 | https://python-pexels.readthedocs.io/en/latest/guidelines.html | Pexels guidelines mirror | Same: link to Pexels per request, no identifiable people in bad light, no implying endorsement, no unaltered resale. | M |
| 4 | https://pexels.com/terms-of-service | Pexels ToS s.5 | Commercial OK, no attribution needed for content, BUT: standalone resale banned; recognizable people "likely require consent"; trademarks/logos cannot be used commercially in relation to goods/services (incl. merch); **scraping, bulk, large-scale or systematic copying strictly prohibited without permission**; no "compile/replicate a competing service". | H |
| 5 | https://www.pexels.com/api/?locale=en-US | Pexels API landing | **"New API key issuance is currently paused and cannot be requested."** (Nov 2026). Only pre-existing keys work. | H |
| 6 | https://unsplash.com/documentation | Unsplash API docs | Demo 50 req/h, production 1,000/h (only api.unsplash.com JSON counts; images.unsplash.com does not). Must hotlink API `urls`, keep `ixid`, and call `/photos/:id/download` on every download. | H |
| 7 | https://unsplash.com/license | Unsplash licence | Commercial OK, no attribution required, irrevocable; may not "compile photos to replicate a similar or competing service". | H |
| 8 | https://help.unsplash.com/en/articles/2612331-why-can-t-i-compile-photos-from-unsplash-to-replicate-a-similar-or-competing-service | Unsplash compile rule | Restriction exists to stop mass copying/rehosting; a private compiled library is grey area. | H |
| 9 | https://pixabay.com/api/docs/ | Pixabay API docs | `key` required; 100 req/60 s per key; **responses must be cached 24 h; no automated bulk querying or systematic mass downloads**; `largeImageURL` max 1280 px; `fullHDURL`/`imageURL` (1920/original) only for approved accounts. Params: image_type, orientation=vertical, min_width/min_height, colors, editors_choice, safesearch, per_page<=200. | H |
| 10 | https://pixabay.com/en/service/license/ | Pixabay licence | Free, no attribution. Prohibited: standalone sale; recognisable trademarks/logos on goods/services; recognisable people in immoral/illegal ways; misleading use. User responsible for model/property releases. | H |
| 11 | https://pixabay.com/cs/service/faq/ | Pixabay FAQ | AI content allowed on site; merch needs significant alteration; recognisable person -> ask for model release. Page does not address bulk download. | M |
| 12 | https://polyhaven.com/our-api | Poly Haven API terms | Free for personal/academic/commercial. No key. **Unique User-Agent header required.** Attribution ("Powered by Poly Haven") only if the live API is exposed in a product; assets themselves CC0. No rate limits documented. | H |
| 13 | https://github.com/Poly-Haven/Public-API | Poly Haven repo | Base `https://api.polyhaven.com`; swagger at `/api-docs/swagger.json`; endpoints for assets, categories, per-asset info. Detail pages not in the fetched text. | M |
| 14 | https://www.polyhaven.com/license | Poly Haven licence | Assets CC0 (commercial, no credit). Website renders/logos/user avatars/example renders NOT CC0. **Web scraping needs permission - use the API, not the site.** | H |
| 15 | https://docs.polyhaven.com/en/faq | Poly Haven FAQ | Returned metadata only - nothing learned. | L |
| 16 | https://github.com/agmmnn/polydown | Poly Haven downloader | Confirms sizes 1k/2k/4k/8k; HDRI hdr/exr; **tonemapped 8K JPG for HDRIs**; texture maps jpg/png/exr. URL pattern not shown. | M |
| 17 | https://docs.ambientcg.com/api/v2/full_json | ambientCG API v2 | `https://ambientCG.com/api/v2/full_json?type=Material&sort=Popular&limit=250&offset=0&include=downloadData,imageData,tagData`; `q`, `type` (Material, PlainTexture, HDRI, Atlas...), `method` (PBRPhotogrammetry, PlainPhoto, HDRIStitched...). limit<=250. No key. | H |
| 18 | https://docs.ambientcg.com/license | ambientCG licence | CC0 1.0 for files and previews; credit optional. | H |
| 19 | https://metmuseum.github.io | Met Open Access API | No key; 80 req/s. `/public/collection/v1/search?hasImages=true&isPublicDomain=true&q=...` (old `/search` retires 2026-10-01; use `/v1.1/search`, limit<=500, offset+limit<=10,000). `primaryImage` = full JPEG, `isPublicDomain` boolean. Dataset CC0. | H |
| 20 | https://api.artic.edu/docs | Art Institute of Chicago API | `https://www.artic.edu/iiif/2/{image_id}/full/843,/0/default.jpg`; filter `query[term][is_public_domain]=true`; 60 req/min/IP, advise 1 req/s; limit<=100. Artwork data CC0, descriptions CC-BY. Use only PD-tagged images. | H |
| 21 | https://openaccess-api.clevelandart.org | Cleveland Museum API | `https://openaccess-api.clevelandart.org/api/artworks/?cc0=1&has_image=1&q=...`; `images.web/print/full` (full = TIFF). CC0 images only when `share_license_status`=CC0. No key stated. | H |
| 22 | https://www.si.edu/openaccess/devtools | Smithsonian dev tools | Key via api.data.gov; PD objects include image URL; copyrighted objects return metadata only. GitHub JSON dump refreshed weekly. | M |
| 23 | https://www.navigating.art/articles-from-navigatingart/open-access-2026 | Museum open-access practice 2026 | Met: no auth. AIC: IIIF needs a Referer header or 403, and `image_id` must be requested via `fields`. Cleveland: licence field returns "CC0" (docs say "Open Access"). Rijksmuseum: no key, Linked Open Data + IIIF, two-step. Getty: SPARQL, no key. | M |
| 24 | https://data.labs.loc.gov/free-to-use/README.html | LoC Free-to-Use dataset | 2,610 items, curated PD/no-known-copyright/cleared sets; bulk package with `manifest.txt`. Mostly historical prints/photos - low fit for "elite" modern backgrounds. | H |
| 25 | https://libraryofcongress.github.io/data-exploration/loc.gov%20JSON%20API/Accessing%20images%20for%20analysis.html | loc.gov JSON API | `?fo=json&c=100`; `image_url` array (last = largest); many images only ~150 px; check `rights` fields; sleep 3 s between pages. | M |
| 26 | https://www.nasa.gov/nasa-brand-center/images-and-media | NASA media usage | Generally not copyrighted, credit NASA; no implied endorsement; no logos (meatball/worm) or identifiable astronauts/employees in commercial promo. | H |
| 27 | https://licenseorg.com/guide/images/rawpixel | Rawpixel licence summary | Free tier = personal use only; Business ~$18/mo for commercial. CC0 only for specific PD items. No API mentioned. Not usable for automation. | M |
| 28 | https://printful.com/blog/free-images-for-print-on-demand | POD-safe free sources | Safest = PD/CC0 (Smithsonian, Rawpixel PD, BL Flickr Commons). Unsplash/Pexels/Pixabay need meaningful alteration for merch; Burst CC0/own licence. Verify per image. | M |
| 29 | https://licenseorg.com/blog/free-stock-photos-licensing-traps | Stock licence traps | No release guarantees for people, property, trademarks; uploader risk; "Pexels: responsibility rests solely with you". | M |
| 30 | https://www.stocksnap.io/license | StockSnap CC0 | All CC0; no implied endorsement. No API; site scraping not authorised. | H |
| 31 | https://licenseorg.com/guide/images/kaboompics | Kaboompics licence | Commercial OK, no attribution; no standalone redistribution; user takes responsibility for logos/products/people. No API. | M |
| 32 | https://community.shopify.com/t/can-i-edit-and-print-burst-app-photos-on-my-t-shirts/294750 | Burst licence question | Unresolved; Burst licence page itself redirected (not read). Treat Burst as unverified. | L |
| 33 | https://huggingface.co/datasets/KoalaAI/StockImages-CC0/blob/main/README.md | HF dataset | 3,999 CC0 stock photos (~889 MB parquet), provenance only "various CC0 sources", with tags. Unknown originals -> provenance risk. | M |
| 34 | https://huggingface.co/datasets/dream-textures/textures-color-normal-1k/blob/main/README.md | HF dataset | 1,426 ambientCG textures at 512x512 only - too small; go to ambientCG directly. | M |
| 35 | https://support.google.com/culturalinstitute/partners/answer/6002688?hl=en | Google Arts & Culture FAQ | Partners keep rights; no reuse licence given to visitors. **Not a reuse source.** | H |
| 36 | https://make.wordpress.org/openverse/handbook/openverse-catalog/provider-api-wikimedia-commons/?output_format=md | Commons API usage (Openverse) | `action=query&generator=allimages&prop=imageinfo&iiprop=url|user|dimensions|extmetadata`; licence from `extmetadata.LicenseUrl`. | M |
| 37 | https://oanor.com/api/commons-api/llms.txt | Third-party Commons wrapper | Confirms: no server-side licence/size filter; filter client-side on licence; "always check per-file licence". | L |
| 38 | https://commons.wikimedia.org/wiki/Help:Searching | Commons search help | `haswbstatement`, `incategory` (case sensitive) documented; `filetype`/`deepcategory` not covered in fetched text. | M |
| 39 | https://jentic.com/apis/openverse.org/openverse.md | Openverse API spec summary | Params: q, license (cc0, by...), license_type (commercial), aspect_ratio (tall), size, category, excluded_source, mature, page_size. OAuth2 client-credentials. | M |
| 40 | https://make.wordpress.org/openverse/2022/06/17/mitigating-out-of-terms-api-usage/ | Openverse limits | Anonymous max 20 results/page (older limit 1 req/s); key needed for volume; scraping/multi-machine evasion forbidden. | M |
| 41 | https://blog.laozhang.ai/en/posts/free-image-api.md | 2026 free image API comparison | Unsplash prod cut 5,000 -> 1,000/h. **Pexels paused new keys**. Pixabay: cache 24 h, no permanent hotlink, preview URLs expire. Commons: 10/min unidentified, 200/min identified, <=3 in flight. Openverse anon 20/min, 200/day. | L (corroborated by #5, #9) |
| 42 | https://developers.cloudflare.com/workers-ai/platform/pricing/ | Workers AI pricing | 10,000 free neurons/day (reset 00:00 UTC); $0.011/1k neurons above. flux-1-schnell 4.8 neurons per 512x512 tile + 9.6 per step. | H |
| 43 | https://developers.cloudflare.com/workers-ai/models/flux-1-schnell | Workers AI FLUX.1 schnell | Input `prompt` (1-2048 chars), `steps` (max 8, default 4), `seed`; output `image` base64 JPEG. **width/height not documented** -> output size must be tested; plan to outpaint/crop to 9:16. | H |
| 44 | https://www.promptzone.com/zuzanna_choi/flux-ai-license-key-insights-2g8d.md | FLUX licence guide | schnell = Apache-2.0 (commercial OK); dev = non-commercial weights (output clause separate). | M |
| 45 | https://invideo.io/blog/open-source-image-models-licenses/ | Open image model licences | Article mostly off-target; FLUX.1 schnell noted as Apache 2.0. | L |
| 46 | https://www.fast.io/resources/stability-ai-review-2026.md | Stability AI pricing/licence | Core $0.03, SD3.5 Medium $0.035, Ultra $0.08 per image; 25 free credits; Community licence free commercial only under $1M revenue + registration + "Powered by Stability AI". | M |
| 47 | https://magichour.ai/blog/imagen-4-pricing-and-api | Imagen 4 status | **Imagen generation endpoints discontinued** (Vertex 2026-06-30; Gemini API 2026-08-17); migrate to Gemini image models. | L-M |
| 48 | https://blog.laozhang.ai/en/posts/gemini-image-api-free-tier | Gemini image API | **No free API tier for image output**; Nano Banana 2.1 ~$0.0336/1K image (~$0.0168 batch); $5 minimum prepay; all outputs SynthID-watermarked (invisible). | L-M |
| 49 | https://huggingface.co/docs/inference-providers/pricing | HF Inference Providers | Free users: no monthly credits; PRO $2/mo credits. Search snippet (unfetched) says free credits removed Oct 2026 and FLUX.1-schnell removal complaints. -> not a free route. | H |
| 50 | https://dev.to/mdenda/procedurally-generating-marble-dice-textures-with-simplex-noise-23pp | Procedural marble | Recipe: multi-octave simplex noise, domain warp (~90 px at freq 0.003), ridged transform 1-|n|, two seeds for dark veins + light highlights, thresholds ~0.86, contrast exponent. | M |
| 51 | https://iquilezles.org/articles/warp | Domain warping | f(p + fbm(p + fbm(p))) double-warp gives organic swirls; colour by q and r magnitudes. | H |

Fetch attempts that failed (not counted): pexels.com/api/documentation, pexels.com/license, polyhaven.com/license (initial), ambientcg.com/help/api, pixabay.com/service/license-summary, metmuseum.github.io (first try), api.artic.edu/docs/ (trailing slash), openaccess-api (first), api.openverse.org/v1/, mediawiki API:Search, Commons reuse page, rijksmuseum data, si.edu/openaccess, pixabay.com/service/terms (server error), shopify Burst licence (redirect x2, redirect target not on allowlist), mediawiki Wikimedia_APIs/Access_policy (not found). Rijksmuseum, Burst licence text, Kaboompics official page, StockSnap bulk terms, Poly Haven `/files` response shape, ambientCG download link shape therefore rest on secondary info or my background knowledge (marked "unverified" below).

## (b) Ranked sources, licence verdicts, recommended pipeline

### Ranked table

Rank = suitability for "automated, licence-safe, 300+ photoreal/texture backgrounds in CI".

| Rank | Source | Licence verdict | Key / limits | Portrait / resolution | "No people" filter | Fit |
|---|---|---|---|---|---|---|
| 1 | **Poly Haven HDRIs** (api.polyhaven.com) | CC0, commercial, no credit. Use API not site scraping. Unique User-Agent. | No key; no documented limit (be polite, 1-2 req/s) | Equirect to 8K tonemapped JPG; render rectilinear 9:16 views yourself (any yaw/pitch = many backgrounds per HDRI) | HDRIs have no people by design; check for logos/signage in street scenes | **Best photoreal env source**: skies, forests, studios, interiors, sunsets, city night |
| 2 | **ambientCG** (ambientcg.com/api/v2) | CC0 files and previews | No key; limit<=250/page | 2K-8K JPG tiling maps; build 1080x1920 by cropping or tiling | Materials only, no people | **Best textures**: marble, plaster, concrete, wood, leather, fabric, paper, metal |
| 3 | **Poly Haven textures/ materials** | CC0 | as #1 | up to 8K | none | Extra premium marble/wood/plaster |
| 4 | **Met Open Access** | CC0 data; use only `isPublicDomain=true` | No key; 80 req/s | primaryImage often 3000+ px | Filter by classification: paintings (landscape), textiles, "Ornament". Portraits excluded by search terms/vision filter | Painterly landscapes, fabrics, marble reliefs; good "luxury" feel |
| 5 | **Art Institute of Chicago** | PD-tagged only | no key; 60/min/IP; need Referer header | IIIF arbitrary size, e.g. `/full/1080,/0/default.jpg` or `full/!1080,1920/` | same | Impressionist landscapes, textiles |
| 6 | **Cleveland Museum** | CC0 only when `share_license_status`=CC0 | no key stated | `images.print` ~ 3500 px JPEG | same | paintings, textiles, Japanese prints |
| 7 | **Smithsonian Open Access** | CC0 when media present | free api.data.gov key | varies; large | same | NASA/NMNH/Cooper Hewitt patterns |
| 8 | **Wikimedia Commons** | Per-file: accept only CC0 / PD (PD-self, PD-old with known author >=70 yr, PD-USGov). Reject CC BY/SA for zero-attribution goal. | no key; descriptive UA required; 10/min unidentified, 200/min identified | Huge originals via `iiurlwidth`; landscape orientation mainly (crop to 9:16) | Use `incategory:` and vision filter; images may include people/buildings -> check | Landscapes, skies, ocean, mountains. High variance in quality |
| 9 | **Openverse** | Discovery layer only. Request `license=cc0,pdm`; open each result's source and re-verify (aggregated metadata can be wrong). | anon 20 results/page; OAuth key for more | aggregated | `category=photograph`, post-filter | Backfill only |
| 10 | **Cloudflare Workers AI FLUX.1 schnell** | Apache-2.0 model; generated outputs usable commercially per BFL; US law: AI outputs may lack copyright (cannot be "owned", but also no third-party rights). Not photographs. | Your existing account; 10k free neurons/day, ~57 neurons per 1024x1024 4-step image (derived, ~170 images/day free); then $0.011/1k | output size undocumented - test; likely 1024x1024-ish -> upscale/outpaint | No people unless prompted; negative prompt not supported by schnell, so avoid people words | Good for "luxury backdrop" bokeh/studio looks |
| 11 | **Procedural (numpy/OpenCV/skimage)** | Own work: no licence risk | CPU only in Actions | Any size, native 1080x1920 | none | Marble, plaster, linen, light leaks, grain overlays |
| 12 | Pixabay API | Free, no credit, but: cache 24 h, no mass downloads, trademark/people limits; API keys may be gated (unconfirmed) | 100/min; `largeImageURL` 1280 px (too small for 1080x1920 without upscale) | portrait via `orientation=vertical` | `safesearch`, plus vision filter | Use sparingly, not primary |
| 13 | Pexels API | ToS forbids bulk/systematic copying; **new keys paused**; API terms need attribution and approval | 200/h | `src.original`, `portrait` 800x1200 crop (too small) | vision filter | **Do not use for bulk 300**. If an existing key works, cap at a few dozen, credit Pexels |
| 14 | Unsplash API | Licence OK but API demands hotlinking + download tracking + no "compiling"; demo 50/h | 50/h demo | `urls.raw` + `&w=1080&h=1920&fit=crop` (must keep ixid) | vision filter | Not suitable for stored library; fine as live hotlink only (not our case) |
| 15 | Library of Congress FTU | PD/cleared | no key | mostly low-res historic | n/a | Skip (poor fit) |
| 16 | StockSnap / Burst / Kaboompics | CC0 / own licences, no APIs; scraping is not permitted | n/a | good photos | manual | Manual hand-picked, only if owner downloads by hand; Kaboompics bars t-shirt standalone, Burst terms unverified |
| 17 | Rawpixel | Free tier personal-use only | none | n/a | n/a | **Exclude** (unless CC0-tagged individual items) |
| 18 | Google Arts & Culture | no reuse licence | n/a | n/a | n/a | **Exclude** |
| 19 | HF/Kaggle "CC0" datasets | Provenance unknown (e.g. StockImages-CC0 = "various CC0 sources") | download via `huggingface_hub` | small/varied | check | Exclude for production; ok for style reference |
| 20 | Gemini image API / Stability / HF inference | Gemini: no free image tier, SynthID, ~$0.034/img; Imagen endpoints retired. Stability: community licence only <$1M revenue with registration + credit line. HF: no free credits. | paid | 9:16 supported on Gemini (`imageConfig.aspectRatio`) | n/a | Optional paid fallback: ~$5 buys ~148 Gemini images |

### Recommended pipeline (target ~350 backgrounds, all CC0/PD/own work)

| Category (reel look) | Source | Count | Search terms / selectors |
|---|---|---|---|
| Skies, sunset, golden hour, dusk, overcast | Poly Haven HDRI (categories: skies, outdoor) | 45 | api `assets?t=hdris&c=skies` / `outdoor`; render 9:16 views at pitch 5-25 deg |
| Forests, misty woods, meadows, desert dunes, mountains, beach/ocean, snow, autumn | Poly Haven HDRI nature + Commons CC0/PD | 45 + 25 | HDRI tags: forest, field, beach, sand, snow; Commons `incategory:` Featured/Quality + CC0 filter |
| Studio backdrops, softbox, interior wall with window light, sunlit shadows | Poly Haven HDRI (studio/indoor) | 30 | categories studio, indoor; tags window, sun |
| City bokeh at night, rooftop skyline | Poly Haven HDRI urban/night (blur 4-10 px to guarantee anonymity) | 20 | categories urban, night |
| Marble, plaster, concrete | ambientCG + Poly Haven | 45 | `q=Marble`, `Plaster`, `Concrete`, `Travertine`, `Terrazzo` |
| Dark wood, leather, velvet/fabric, linen, paper | ambientCG | 45 | `q=Wood`, `Leather`, `Fabric`, `Paper`, `Cardboard`; fabrics are the "velvet/linen" substitute |
| Watercolour / painterly landscapes, marble sculpture detail, textile patterns | Met + AIC + Cleveland (PD) | 45 | Met `q=landscape&departmentId=11` (European Paintings), `q=textile`; AIC `is_public_domain` + `classification_title=painting` |
| Procedural marble, plaster, linen weave, light leaks, film grain, gradients | Own code | 40 | see below |
| AI "luxury product backdrop" extras (blurred boutique, silk, bokeh) | Workers AI FLUX.1 schnell | 30 | see prompts |
| Optional existing-key photos (Pexels/Pixabay), each with credit | existing scripts | <=20 | skip unless wanted |

Total CC0/PD/own: ~350. Keep 20% surplus to absorb QC rejections (expect 10-25% rejected).

### Exact request patterns

Poly Haven (always send a descriptive UA, e.g. `AlphaDogStyles-bg-builder/1.0`):
```
GET https://api.polyhaven.com/assets?t=hdris            # dict {id: {name,categories,tags,...}}
GET https://api.polyhaven.com/assets?t=hdris&c=skies    # category filter (c=outdoor, studio, urban, nature...)
GET https://api.polyhaven.com/files/{id}                # JSON tree of file URLs
# then pick files JSON: ["tonemapped"]["url"] (8K JPG) or ["hdri"]["4k"]["hdr"]["url"]; URL host is dl.polyhaven.org (shape unverified)
```
Render a 9:16 rectilinear view from the equirect JPG: numpy/py360convert, FOV h ~ 55-70 deg, 1080x1920, vary yaw 0..330 by 60 deg to obtain several backgrounds per HDRI; sharpen no more than needed.

ambientCG:
```
GET https://ambientCG.com/api/v2/full_json?type=Material&q=marble&sort=Popular&limit=50&include=downloadData,imageData,tagData
# each asset -> downloadFolders.default.downloadFiletypeCategories.zip.downloads[].fullDownloadPath (unverified field names)
# download pattern seen in the wild: https://ambientcg.com/get?file=Marble006_4K-JPG.zip -> use *_Color.jpg
```
Material colour maps are tileable squares; for 1080x1920 use 4K-8K crop, add vignette and gradient, or lay 2x1 tile with seam blending.

Met:
```
GET https://collectionapi.metmuseum.org/public/collection/v1/search?hasImages=true&isPublicDomain=true&q=landscape
GET https://collectionapi.metmuseum.org/public/collection/v1/objects/{id}   # check isPublicDomain==true and primaryImage
```
AIC:
```
GET https://api.artic.edu/api/v1/artworks/search?query[bool][must][0][term][is_public_domain]=true&q=landscape&fields=id,title,image_id,is_public_domain&limit=100
GET https://www.artic.edu/iiif/2/{image_id}/full/1686,/0/default.jpg   # send Referer: https://www.artic.edu/ ; <=1 req/s
```
Cleveland:
```
GET https://openaccess-api.clevelandart.org/api/artworks/?cc0=1&has_image=1&q=landscape&type=Painting&limit=100
# use images.print.url; verify share_license_status == "CC0"
```
Commons (UA with contact required):
```
GET https://commons.wikimedia.org/w/api.php?action=query&format=json&generator=search&gsrnamespace=6&gsrsearch=filetype:bitmap incategory:"Featured pictures of landscapes" haswbstatement:P6216=Q6938433 &gsrlimit=50&prop=imageinfo&iiprop=url|size|mime|extmetadata&iiurlwidth=2400
# P6216=Q6938433 is "copyright status: public domain"(CC0 is P275 license); verify in extmetadata
```
Gate on `extmetadata.LicenseShortName.value` in {"CC0", "Public domain", "PD-..."}, `extmetadata.Restrictions` empty or not containing trademark/personality, `NonFree` absent, `Artist`/`Credit` stored. Keep <=3 concurrent requests, ~1/s.

Openverse (discovery only):
```
GET https://api.openverse.org/v1/images/?q=misty+forest&license=cc0,pdm&category=photograph&aspect_ratio=tall&size=large&page_size=20
```

Workers AI (account already paid; use REST from Actions with API token):
```
POST https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/ai/run/@cf/black-forest-labs/flux-1-schnell
Authorization: Bearer {TOKEN}
{"prompt":"...", "steps":6, "seed": N}     # response: {"result":{"image":"<base64 jpeg>"}}
```
Cost estimate: ~57 neurons per 1024^2 at 4 steps; ~10k free/day gives ~170 images; paid overage ~$0.0006/image. Size control undocumented: test passing width/height; if ignored, generate square and outpaint/blur-extend to 9:16 or use as a bokeh layer (soft backgrounds hide the upscale).

Prompt patterns (9:16 "luxury product backdrop", no people, no text):
- "empty luxury boutique interior, softly blurred, warm golden window light, creamy bokeh, shallow depth of field, photographic, no people, no text, no logos"
- "polished white Carrara marble surface with subtle grey veining, soft studio lighting, product photography backdrop, vertical composition, negative space at center"
- "dark walnut wood grain, moody low key lighting, subtle vignette, macro photograph, empty"
- "crumpled champagne silk fabric background, soft folds, studio softbox light, empty frame"
- "misty pine forest at dawn, volumetric light rays, muted colors, empty trail, vertical landscape photo"
- "city skyline at blue hour from rooftop, heavy bokeh lights, no readable signs"
Add composition words: "negative space in the lower-middle for product placement". schnell ignores negative prompts, so keep unwanted things (people, text, brands) out of the positive prompt and QC after.

Procedural recipes (numpy + OpenCV, all in 1080x1920, deterministic by seed):
- Marble: fBM (6 octaves) -> domain warp (q then r, IQ style) -> ridged `1-|n|` -> power 2-4 -> colormap white/grey/gold; second seed for fine veins; slight gaussian blur; add film grain sigma 0.01-0.02.
- Plaster / limewash: low-frequency fBM + mottling + fine noise, 2-3 tone colour ramp, subtle directional light gradient.
- Linen/fabric: sinusoidal warp/weft threads with noise jitter on thread width, slub noise, multiply tone ramp.
- Light leaks: sum of large soft gaussians in amber/magenta with additive screen blend at 15-35%, optional diagonal streak.
- Film grain & halation: gaussian noise (sigma 0.015) luminance-weighted, plus 2-pass blurred highlight bloom.
- Gradient studio: radial gradient + noise dither (prevents banding in H.264).
Libraries: `opensimplex` or `noise` (PyPI), `numpy`, `scipy.ndimage`, `opencv-python-headless`.

### Licence checks to automate (in CI before a file is accepted)
1. Write one `meta.json` per image: source, id, source URL, licence string, licence URL, retrieved_at, sha256, width/height, author. Reject if any field missing.
2. Allowlist licences: `CC0-1.0`, `PDM-1.0`/Public domain, `own-work` (procedural), `ai-generated(flux-1-schnell, Apache-2.0)`. Everything else rejected, including CC BY / BY-SA (want zero attribution).
3. Per source gates: Met `isPublicDomain==true`; AIC `is_public_domain==true`; Cleveland `share_license_status=="CC0"`; Commons `LicenseShortName` in CC0/PD and no Restrictions/NonFree; Openverse `license in (cc0,pdm)` then re-verify at source; Poly Haven / ambientCG implicitly CC0.
4. Visual gates (vision model in the Actions job, e.g. Gemini Flash vision or open-source detectors): reject if face/person detected (OpenCV DNN / YOLO person class), if OCR (tesseract) finds more than ~3 characters, if logo/brand/storefront detected, if recognisable landmarks/buildings with famous trademarks, NASA/other insignia, or watermark. For painting sources reject portraits and religious/sensitive subjects, nudity.
5. Technical gates: min short side >=1080 after crop (>=1500 source preferred), no upscaled blur (Laplacian variance threshold), no heavy JPEG artifacts, perceptual-hash dedupe (imagehash pHash distance <6) across the library and against past reels.
6. Store a `LICENSES.md`/CSV in the repo listing every background and its licence (audit trail), plus "Powered by Poly Haven"-style credit lines in README (not required for CC0 but harmless).
7. Re-check at publish time that a file's `meta.json` has `approved: true` from the QC job.

## (c) Risks

1. **Bulk-download traps.** Pexels ToS prohibits "bulk, large-scale or systematic copying" and ML scraping; Pixabay API forbids systematic mass downloads and requires 24 h caching; Unsplash API requires hotlinking and prohibits compiling a library; Poly Haven site scraping needs permission (API is fine). Building a 300-image stored library from Pexels/Pixabay/Unsplash is the single biggest compliance risk, so they are demoted to optional.
2. **Key availability.** Pexels is not issuing new keys (Nov 2026). Pixabay key status unconfirmed. Unsplash demo = 50 req/h. Plan must not depend on them.
3. **Trademarks and logos.** Pexels/Pixabay licences explicitly bar commercial use of images with recognisable trademarks/brands in relation to goods or services (reels promoting merch count). Street HDRIs, cityscapes, storefronts, cars, phones and signage can carry logos. OCR + logo detection gate and blur city bokeh.
4. **Identifiable people.** Release is never guaranteed by stock sites. HDRIs and textures have none; museum PD paintings may show real historical people (low risk, but exclude portraits for brand safety); Commons landscape photos can contain people or private property. Run person detection on everything.
5. **Per-image licence drift.** Commons files can be re-licensed/deleted; Openverse metadata aggregated from third parties can be wrong; HF "CC0" datasets have unknown provenance; AIC images are served through a hotlink-friendly but removable IIIF and some images are not PD; Smithsonian copyrighted objects have metadata-only CC0; Cleveland CC0 images only for CC0-status works. Always verify at source and keep a snapshot.
6. **AI-generated backgrounds.** FLUX.1 schnell is Apache-2.0 (commercial OK), but outputs may not be copyrightable (low practical risk for backdrops) and could resemble real brands/places; Gemini outputs carry SynthID; Stability community licence needs registration + credit and is revenue-capped; avoid FLUX.1 dev (non-commercial weights). Prompts must exclude people, text, brands.
7. **Non-CC0 parts of CC0 sites.** Poly Haven website renders, logos and avatars are not CC0; ambientCG previews are CC0; Rawpixel free tier is personal-use only; NASA logos/astronauts restricted; Kaboompics forbids standalone t-shirt use.
8. **Platform-side compliance.** Reels are on Instagram/TikTok/YouTube: AI-labelling rules may require marking AI-generated backgrounds; keep generated images <=10-15% of the library to keep a "real photograph" identity.
9. **Quality risk.** Museum paintings and Commons images are landscape-oriented, so 9:16 crops may lose resolution; HDRI-derived rectilinear views are the cleanest way to get true 9:16. ambientCG tiles may show repetition at 2K - use 4K+.
10. **Unverified items** (not confirmed on a fetched page): Poly Haven `/files` JSON shape and `dl.polyhaven.org` host, ambientCG `downloadData` field names and `/get?file=` pattern, Commons `P6216` search syntax, Rijksmuseum API specifics, Burst licence text, Pixabay API key issuance state, Workers AI width/height support. Test each once in CI before building on it.

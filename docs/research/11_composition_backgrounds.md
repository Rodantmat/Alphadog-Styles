# 11 - Elite backgrounds and composition for 9:16 merch reels

Research date: 2026-11-10. Pages fetched: 61 (successfully read; 66 fetch attempts, 4 failed, 1 redirect not followed; a duplicate re-fetch of the Hopper Reels page is not counted).
Honesty note: web sources are mostly generic photography/design blogs and give few numbers. Where a number is not in a source it is marked **[eng]** (my engineering judgement, tested only visually on a synthetic cutout) and must be tuned by eye on real Printify cutouts. Sourced numbers are marked **[src #]** (# = row in the log). Reddit and some brand sites could not be fetched; brand staging (Gymshark, Aritzia, Carhartt, Patagonia) is NOT directly evidenced by fetched pages - see section A.3 for what is actually supported.

---------------------------------------------------------------------
## (a) Fetch log

| # | URL | Type | Key takeaway | Reliability |
|---|-----|------|--------------|-------------|
| 1 | stock.adobe.com/learn/product-photography-backgrounds-guide | vendor guide | Types: white/neutral, textured (wood=artisan, marble=luxury, concrete=modern/urban), lifestyle, colour/gradient. Subtle textures, scale texture to product, keep 5-10 go-to textures for brand consistency; complementary pops, analogous = sophisticated; dark bg = drama but needs contrast | medium |
| 2 | eggradients.com/blog/image-cutouts | blog | Cutouts look pasted from: colour-temp mismatch (5500K subject on 3000K bg), old-bg halos, grey/black shadows (should be tinted by scene), conflicting gradient direction. Fix: sample shadow colour from bg dark areas; match in CIELAB (L first); blur/invert/desaturate/thumbnail checks | medium-high (practical, no numbers) |
| 3 | dreamina.capcut.com/.../product-scene-scale-contact-shadows | vendor blog | No universal radius/opacity; contact shadow tucked under base, Multiply, scale both axes together, check camera height/perspective vs scene | medium |
| 4 | fstoppers.com/composite/...blend-your-subject-background | tutorial | Match exposure, gradient map to tie colour, blur only part of subject edges, add contrast + vignette, take a 10-15 min break; light direction must agree | medium |
| 5 | hopperhq.com/blog/instagram-reel-size | guide | Reels safe zone: top 14% (~270px), bottom 35% (~670px; right ~770px), sides 6% (~65px) -> ~950x980 centred; grid thumb 3:4 (1080x1440) crops ~240px top/bottom | medium |
| 6 | argil.ai/blog/instagram-reel-size-e350f | guide | Safe zone 1080x1420 (top 250, bottom 250, left >=100px); profile grid shows centre 1080x1080 | medium (conflicts with #5 on bottom) |
| 7 | shotkit.com/flat-lay-clothing-photography | pro-photo guide | Hardwood warm/rustic, marble for tan/white outfits, neutral rug softens vivid outfit; soft window light, light at ~45 deg to reduce shadow; one accent prop; fold neatly | medium-high |
| 8 | shopify.com/blog/clothing-photography | commerce guide | White/light grey standard; for light garments use slightly off-white/grey; lifestyle: setting itself is the bg (woods for earth tones); 3-point light (key, fill, back) | medium |
| 9 | expertphotography.com/clothing-photography | photo blog | Seamless paper, plain wall; keep bg colour from overpowering; large window + 45 deg angle; matches sources 7-8 | medium |
| 10 | skillshare.com/blog/the-6-steps-to-flat-lay-photography | blog | Wood, wrinkled sheets as neutral bg; dark bg + light objects = monochrome look; centred/thirds/leading lines; leave negative space for text | medium |
| 11 | petapixel.com/2024/01/03/v-flat-world...shadow-boards | trade news | Window-shadow gobo boards (hard light + board) light only bg or bg+subject; real product tool = window-shadow look is an accepted pro device | high (fact), n/a numbers |
| 12 | planetphotoshop.com/using-photoshop-to-create-digital-gobos | tutorial | Digital gobo = white pane grid, Overlay, perspective warp, Gaussian blur, optional clipped copy on subject at low opacity | medium-high |
| 13 | photofocus.com/.../what-is-a-gobo | photo blog | Gobo nearer subject = sharper shadow, farther = softer (shadow blur must scale with "distance") | high |
| 14 | morphic.com/resources/how-to/create-a-streetwear-brand-photo | AI-vendor guide | Streetwear settings: street, rooftop, underpass, graffiti wall (day), wet city street (night); name time of day + light; vary crop/location, check at square + vertical | low-medium |
| 15 | retouchinglabs.com/clothing-brand-photoshoot-ideas | blog | Studio neutral / urban / nature (golden hour) / social-seasonal / conceptual colour-block backgrounds | low-medium |
| 16 | phlearn.com/tutorial/intro-to-studio-compositing | course page | Hard part = matching studio light to bg; without shadow subject floats; copy bg shadows; remove halos; match skin/colour to environment | high (Phlearn is a pro source) |
| 17 | phlearn.com/tutorial/30-days-photoshop-match-light-color | tutorial | 8-step method: anchor transform at bottom, clip adjustments, B&W check for brightness, Levels, saturation-mode solid to expose casts, Color Balance toward bg hues, KEEP original contact shadow patch | high |
| 18 | fixanyphoto.com/guide/flat-lay-apparel-photography | guide | Flat-lay: 90 deg overhead, 50mm, level camera; 2 lights ~45 deg, 5000-5600K, CRI>=90; lights at surface height (raised light = top brighter); diffuse; no mixing light | medium |
| 19 | blog.wearview.co/flat-lay-clothing-photography | blog | Neutral almost always better; light wood vinyl, linen, sealed concrete for lifestyle brands; light 45 deg, white reflector fill | medium |
| 20 | pixelcut.ai/learn/clothing-flat-lay-photography-ideas-2023 | blog | Wood, marble tabletop, wrinkled bed cover; opposite-hue bg makes outfit pop; never white bg for white outfit; ~90 deg | medium-low |
| 21 | soona.co/blog/clothing-product-photography | studio blog | Plain bg default; black clothing with white/bright accessories; window side light, early morning/late afternoon; props sparingly | medium |
| 22 | soona.co/blog/add-color | blog index | Page returned only a blog index - no usable content | n/a (logged for honesty) |
| 23 | squareshot.com/post/lifestyle-shot-vs-white-background... | agency blog | White bg for marketplaces; lifestyle for social/ads; keep angle/light/bg tone consistent; busy lifestyle can distract; no hard numbers | low-medium |
| 24 | squareshot.com/post/apparel-photography-lighting | agency blog | Front / directional / back light roles; dark garments need shaped light not more exposure; white garments need bg contrast control | medium |
| 25 | w3.org/WAI/WCAG22/Techniques/general/G18 | standard | Relative luminance L=0.2126R+0.7152G+0.0722B (linearised sRGB); contrast=(L1+0.05)/(L2+0.05) | very high (formula); applying it to garment/bg separation is my proxy |
| 26 | joshwcomeau.com/css/designing-shadows | expert essay | One global light direction, same offset ratio for all shadows; higher elevation = bigger offset+blur+lower opacity; layer several shadows; tint shadows with bg hue instead of black | high (principles transfer to compositing) |
| 27 | dev.to/alphashark/the-anatomy-of-a-good-box-shadow... | dev blog | Close 0 1px 3px .12; mid 0 4px 12px .15; high 0 12px 40px .20; 3 layers (1/2, 4/8, 12/24px) at ~.07; tint shadows | medium (UI units, scale to 1080 px) |
| 28 | pixotter.pages.dev/blog/add-grain-to-photo | blog | Grain: LR amount 15-25 social, 20-40 editorial; PS Add Noise 3-8% subtle; Python sigma 5 subtle/25 visible/50 heavy; shadows heavier (35) than highlights (10); +30-50% for print | medium |
| 29 | stable-diffusion-art.com/add-film-grain-and-vignette-comfyui | tutorial | No numeric values (paywalled workflow); vignette feather/zoom controls only | low (no data) |
| 30 | licenseorg.com/blog/unsplash-license-attribution-required | licence explainer | Unsplash: commercial OK, no attribution; no bulk re-hosting; recognisable people/logos may need releases; API requires credit | medium-high |
| 31 | licenseorg.com/blog/free-stock-photos-licensing-traps | licence explainer | Free stock lacks model/property releases; uploader rights unverified; avoid recognisable people/trademarks in ads | medium |
| 32 | app.cinevva.com/guides/free-textures-hdris-materials | guide | Poly Haven (CC0, 850+ textures, 990+ HDRIs), ambientCG (CC0, 2000+ materials), 3DTextures.me, ShareTextures, cgbookcase CC0; FreePBR NOT commercial-free | medium-high |
| 33 | gearpatrol.com/.../ruffwear-designed-worlds-best-dog-harness | magazine | Ruffwear = outdoor-gear story; (no imagery detail) | low for style |
| 34 | retailbrew.com/.../ruffwear-pricey-new-line | trade press | Ruffwear shows wilderness settings (Isle of Skye), "explorer" archetype like Patagonia, dog as pack companion, no costume/novelty vibe | medium-high (brand positioning) |
| 35 | theimpression.com/?p=11343407 | fashion news | Fear of God Essentials campaign: neutral palette, bright open industrial-refined interior, plain lookbook portraits focusing on texture/silhouette | medium |
| 36 | nightjar.so/blog/ai-product-photography-fitness-gym-athleisure-brands | vendor blog | Athleisure staging = packshot on flat colour + contact shadow, on-model, location scenes; keep photographic style layer consistent across catalogue; does NOT name Gymshark | low-medium |
| 37 | zilliondesigns.com/blog/?p=22467 | agency blog | Fitness-brand: plain neutral bg, logo as set piece, sunset silhouettes, avoid stock | low |
| 38 | libcom.readthedocs.io/en/latest/color_transfer.html | library docs | Reinhard transfer: shift/scale fg mean+std in L*a*b* to bg; good for simple/uniform colours, not refined | high |
| 39 | pyimagesearch.com/?p=997 | tutorial | 10-step Reinhard colour transfer in Lab with mean/std (clip 0-255) | high |
| 40 | creatomate.com/blog/how-to-zoom-images-and-videos-using-ffmpeg | tutorial | zoompan z/x/y/d/s/fps; upscale (e.g. scale=8000:-1) before zoompan for smooth zoom | medium-high |
| 41 | hopperhq.com/blog/tiktok-dimensions | guide | TikTok: top ~150, bottom ~400, right ~140, left ~60 px margins | medium |
| 42 | wildandfreetools.com/blog/vertical-video-safe-zones-guide-2026 | guide | Hidden top/bottom: TikTok 220/480, Reels 220/450, Shorts 150/400; universal safe Y = 220-1440 | medium |
| 43 | phlearn.com/tutorial/depth-aware-haze-photoshop | tutorial | Haze = "one of the strongest depth cues"; far items lose contrast+saturation, take pale tint; start with haze amount only | high |
| 44 | diyphotography.net/add-depth-images-2-easy-steps | tutorial | Depth = lower bg contrast (aerial perspective) + blurry foreground elements that make sense; avoid cliche petals | medium |
| 45 | blog.evoto.ai/how-to-create-a-floor-reflection-in-photoshop | tutorial | Flip, start exactly at contact (gap = floating), lower opacity, gradient mask fade, slight blur | medium |
| 46 | pixc.com/blog/how-to-create-a-reflection-effect... | tutorial | Gradient mask on flipped copy, Gaussian blur ~5 px | medium |
| 47 | polyhaven.com/license | licence | All CC0, commercial OK, no attribution; scraping prohibited, API under separate terms | very high |
| 48 | snobbydrops.com/.../how-to-match-backdrops-to-client-wardrobe | backdrop vendor | Complementary (blue/orange), analogous (peach/blush), neutral greige/ivory/sand; matte backdrop vs silk/sequins | medium |
| 49 | slrlounge.com/how-why-to-shoot-on-colored-seamless-backgrounds... | photo blog | Light the backdrop separately; vary only bg light power to move tone (rose<->pink); keep subject-bg gap large | medium-high (its two distance rules contradict; ignore) |
| 50 | social.colostate.edu/.../vertical-video-and-using-composition-rules | university | Eye near top-third intersection; vertical suits tall subjects; centre OK for symmetry; no headroom guidance | medium |
| 51 | photographyicon.com/vertical-video-social-media | blog | Eyes near upper third line; headroom ~ forehead height; safest content = middle 70% of frame | medium |
| 52 | cursa.app/en/page/mobile-composition-framing-and-safe-zone-design | course page | Favour centre column; key objects higher than feels natural; keep right edge + bottom clear; reserve a caption shelf; test with overlay | medium |
| 53 | mko.re/blog/ken-burns-ffmpeg | blog | zoompan formulas (z='zoom+0.002', centred x/y expressions); higher fps for long pans | medium |
| 54 | adorama.com/alc/how-to-use-complementary-colors-in-photography | retailer blog | Complementary pairs, split-complementary for softer balance, accent role | medium |
| 55 | static.bhphotovideo.com/explora/node/35431 | retailer guide | Mono/analogous = calm low contrast; complementary = max contrast; value + saturation guide the eye | medium |
| 56 | github.com/agmmnn/polydown | tool repo | `pip install polydown; polydown textures -s 2k -tf png --maps Diffuse` bulk-fetches Poly Haven CC0 | medium (3rd-party tool) |
| 57 | cs.brown.edu/.../colormatch.py | course code | Reinhard in Lab via skimage rgb2lab; "right colour space matters" | medium |
| 58 | blog.evoto.ai/how-to-add-floor-reflection-to-photos | tutorial | Reflection opacity 35-55%, narrow far end, desaturate slightly, steep fade, soften contact line | medium |
| 59 | shutterevolve.com/how-to-add-atmosphere-and-depth-in-photoshop | tutorial | Blurred duplicate masked in as atmosphere, restore highlights with Levels | medium-low |
| 60 | adobe.com/learn/photoshop/web/fantasy-atmospheric-effects | vendor tutorial | Fog via Screen mode tinted with sky colour; frame composition with foreground elements in lower corners; mask fog edges | medium |
| 61 | snobbydrops.com/.../choosing-color-palettes-that-complement-your-backdrops | backdrop vendor | Navy/charcoal bg + beige/cream/pastel blue clothes; olive/clay + burnt orange/tan/ochre; blush/sage + soft; mid grey/taupe + black/white/metallic | medium |

Failed / not usable (not counted): canon.co.uk fashion-product-photography-challenges (server error), canon.co.uk colour-in-photography (server error), learnarchitecture.net cc0-textures (client error), el-tramo.be (redirect to #53, fetched there). Reddit not fetchable (as stated).

### Reading of the evidence
* Every source agrees: neutral/muted backgrounds + one consistent light direction + a tinted (not black) contact shadow is what separates "photographic" from "pasted". Textures (plaster, concrete, linen, wood, marble) are explicitly endorsed for luxury/modern/artisan moods (#1, #19, #20).
* Light-direction consistency, shadow colour and colour-temperature agreement are the three most-cited failure points (#2, #4, #16, #17, #26).
* Platform safe zones disagree (top 150-270, bottom 250-670). I use the intersection (section B.1).
* There is no fetched evidence for Gymshark/Aritzia/Carhartt/Fear of God internal staging rules. What IS supported: Fear of God Essentials = neutral palette, bright industrial-refined interior, plain texture-led portraits (#35); Ruffwear/Patagonia = wilderness/explorer settings with the dog as companion (#34); athleisure = flat-colour packshot with contact shadow, one style layer reused across the catalogue (#36).

---------------------------------------------------------------------
## (b) Elite background and composition spec

### B.1 Canvas, safe zones, thirds (1080x1920)
* Safe zone to design the HERO subject inside: **y 270..1440, x 100..940** (intersection of #5, #6, #41, #42, #52; right ~140 px keeps off TikTok/Reels buttons). Background art runs full-bleed; only subject + text obey the zone.
* Reels grid thumbnail = centre 1080x1440 (y 240..1680) [src 5] and some crops 1:1 centre 1080x1080 [src 6]: the product/dog design must also be fully legible inside y 420..1500 -> centre the hero's "logo/design area" near y ~ 760-1000.
* Brand text (if any): top pill y 290..360; CTA at y 1300..1400 (above the ~1440 line). Never over merchandise (owner rule).
* Single subject: **centred on x (540) with an optical offset of 0-6% (<=65 px) toward the side opposite the light** [eng]; use thirds vertically: the design/face/key graphic sits near the upper third line y ~ 640 (33%) [src 50, 51] [eng for the pixel].
* Headroom (people): ~ one forehead height ~ 4-6% of person height above the head [src 51 + eng]; person head top not above y 270.

### B.2 Numeric parameters per subject kind  (all [eng] unless a src is shown)
Light convention for every scene: ONE key light from upper-left (light_xy=(-1,-1)), so shadows fall right/down; mirror the whole scene for variety, never mix [src 26].

| Param | Person (full body, cutout) | Flat-lay garment (top-down) | Folded garment / stack | Cap |
|---|---|---|---|---|
| Height or width on canvas | height 1050-1250 px (55-65%); 3/4-length crop may be 1350 but hands stay y<1440 | width 760-860 px (70-80%) | width 560-680 px (52-63%) | width 420-560 px (40-52%) |
| Anchor | feet/bottom at y 1400-1440, centre x 540(+-60) | centre y 780-900 (41-47%) | base y 1080-1180, centre y ~ 930 | centre y ~ 820-900 |
| Rotation | 0 | 0 to +-4 deg (never 90 deg unless intentional) | 0 to +-3 deg | 0 to +-6 deg |
| Contact shadow (tight) | ellipse sigma 6-10 px, opacity .45-.55, offset (3,5) px, squashed to 0.15 height | sigma 3-4 px, opacity .30-.40, offset (3,5) | sigma 3-5 px, opacity .45-.55, offset (2,4) | sigma 4-6 px under brim, opacity .45, offset (3,6) |
| Ambient / cast shadow | sigma 30-45 px, opacity .22-.30, long on floor, direction away from light, length 0.25-0.4 x height for studio sweep (golden hour 0.8-1.2x) | sigma 14-22 px, opacity .14-.24, offset (8,16)-(12,26) | sigma 18-28 px, opacity .20-.28, offset (10,18) | sigma 14-20, opacity .18-.26, offset (8,16) |
| Shadow colour | bg 5th percentile colour x0.45 (tinted, not black) [src 2, 26] | same | same | same |
| Reflection (only glossy surfaces: polished concrete, black marble, gloss paper) | optional, opacity .35-.45, fade to 0 over 280-380 px, blur 2->8 px, starts exactly at contact [src 45, 58] | not on matte; on marble .15-.25, long fade | .25-.35 | .30-.40 |
| Background blur (if photo has detail) | real photo already shallow; if flat photo add Gaussian sigma 6-14 px (simulates f/2-2.8) [eng] | none on the textured surface itself (it is in focus plane) but props/edges blur sigma 10-20 | none | none |
| Subject colour fidelity | alter <=6% towards bg tint (colour-match strength alpha 0.06); NEVER re-grade garment hue (customer expectation) | same | same | same |
| Edge | erode alpha 1 px, feather Gaussian 0.8-1.2 px, remove old-bg fringe [src 2, 16] | same | same | same |
| Rim / light-wrap | 3-6 px light-wrap from blurred bg, 25-40% screen, only on side facing key; optional rim on dark garments | not needed | not needed | optional |

Global finishing [eng, anchored by #28, #4]:
* Grain: Gaussian sigma **5-7** (0-255 scale) for social, luminance only, shadow-weighted x1.0-1.6, applied to the WHOLE composite (subject included) so subject and bg share the same noise; regenerate per frame at 12-24 fps for video (static grain looks like a dirty lens).
* Vignette: corner darkening **10-16%**, power 2.4; for dark bgs 6-10%.
* Bg contrast: lower bg local contrast ~10-20% vs raw texture (aerial perspective, #44, #43) and keep the bg 0-1 stops darker/less saturated than the subject (greatest-area-of-contrast to subject).
* Foreground blur elements (leaf, rope, grass, curtain edge, out-of-focus plant): occupy 6-14% of frame at lower corners [src 60], Gaussian sigma 18-35 px, opacity 55-85%, max 1-2 per scene; must make sense in scene [src 44].
* Parallax (10 s): bg zoom 1.00->1.05, subject 1.00->1.025 (+ drift -5 px), foreground blur element 1.00->1.12; smoothstep easing; keep subject displacement <= 20 px so merch stays readable [eng].
* Haze: lift bg blacks by 4-8 and desaturate bg 6-12% on landscapes/urban photos [src 43 + eng].

### B.3 Colour theory and luminance numbers
Formula (#25): L = 0.2126 R + 0.7152 G + 0.0722 B (linear), ratio=(Lhi+.05)/(Llo+.05). Used here as a separation proxy (not an accessibility claim).
Rule set [eng, consistent with #1, #8, #20, #21, #48, #55, #61]:
* Dark garment (L<0.05): bg L 0.25-0.80 -> ratio 5-15; best 0.35-0.65 (ratio 6-11) so the dark print area doesn't clip and shadows still read. Avoid bg L<0.10 unless a rim/spot pool is added.
* Mid garment (L 0.2-0.5): go either direction: bg L<=0.06 (ratio 4-9) or L>=0.75.
* Light garment (L>0.7): bg L 0.01-0.20 (ratio 5-15) or mid 0.2-0.4 (ratio 3-4); never bg L>0.6 (ratio <1.7, white-on-white) [src 20].
* Minimum ratio garment-to-bg dominant tone: **3.0** (below 2.0 only for deliberate tonal editorial with rim light); max useful ~15 (beyond looks like a cut-out on black).
* Hue: prefer analogous/neutral first (greige, oat, bone, charcoal, navy, sage, dusty blue = "quiet luxury"), complementary only as an accent of <=15% area (e.g. terracotta behind navy) [src 1, 48, 54, 61]; avoid saturated bg (>45% HSV saturation) behind garments with colour prints.
* Skin/people: warm bg for cool skin, cool bg for warm skin [src 61]; for merch reels use neutral beige/grey/charcoal so wardrobe colour stays the hero.

Computed WCAG ratios (garment row x background column), from `python` run in this session:

| garment \ bg | warm greige plaster c9bfb1 | oat linen d8cfbf | bone paper e6e0d4 | light concrete b9b9b6 | mid concrete 8a8a88 | charcoal slate 2e3033 | deep navy 14213a | terracotta b5654a | sage plaster a7b59b | dusty blue 8fa6bd | walnut 5a3f2c | warm sand d9c7a3 | forest 24402f | blush e3c5bd | mustard c99a2e | black marble 1b1b1d | white marble e9e7e4 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| black 111111 | 10.4 | 12.2 | 14.4 | 9.6 | 5.5 | 1.4 | 1.2 | 4.4 | 8.8 | 7.5 | 2.0 | 11.4 | 1.7 | 11.7 | 7.3 | 1.1 | 15.3 |
| charcoal 36393d | 6.4 | 7.5 | 8.8 | 5.9 | 3.4 | 1.1 | 1.4 | 2.7 | 5.4 | 4.6 | 1.2 | 7.0 | 1.0 | 7.2 | 4.5 | 1.5 | 9.4 |
| navy 1b2a41 | 8.0 | 9.4 | 11.0 | 7.3 | 4.2 | 1.1 | 1.1 | 3.4 | 6.7 | 5.8 | 1.5 | 8.7 | 1.3 | 8.9 | 5.6 | 1.2 | 11.7 |
| forest 1f3d2b | 6.6 | 7.7 | 9.1 | 6.1 | 3.5 | 1.1 | 1.4 | 2.8 | 5.5 | 4.8 | 1.2 | 7.2 | 1.1 | 7.4 | 4.6 | 1.4 | 9.7 |
| burgundy 5a1f2b | 7.0 | 8.2 | 9.6 | 6.4 | 3.7 | 1.1 | 1.3 | 3.0 | 5.8 | 5.0 | 1.3 | 7.6 | 1.1 | 7.8 | 4.9 | 1.4 | 10.2 |
| heather grey 9a9ca0 | 1.5 | 1.8 | 2.1 | 1.4 | 1.3 | 4.8 | 5.8 | 1.6 | 1.3 | 1.1 | 3.5 | 1.7 | 4.1 | 1.7 | 1.1 | 6.3 | 2.2 |
| sand/tan c8b79a | 1.1 | 1.3 | 1.5 | 1.0 | 1.8 | 6.7 | 8.2 | 2.2 | 1.1 | 1.3 | 4.9 | 1.2 | 5.8 | 1.2 | 1.3 | 8.8 | 1.6 |
| cream efe8d8 | 1.5 | 1.3 | 1.1 | 1.6 | 2.8 | 10.8 | 13.2 | 3.5 | 1.8 | 2.1 | 7.9 | 1.4 | 9.3 | 1.3 | 2.1 | 14.1 | 1.0 |
| white f4f4f2 | 1.7 | 1.4 | 1.2 | 1.8 | 3.1 | 12.0 | 14.6 | 3.9 | 2.0 | 2.3 | 8.7 | 1.5 | 10.3 | 1.5 | 2.3 | 15.6 | 1.1 |
| sage 9caf88 | 1.3 | 1.5 | 1.8 | 1.2 | 1.5 | 5.6 | 6.8 | 1.8 | 1.1 | 1.1 | 4.1 | 1.4 | 4.8 | 1.5 | 1.1 | 7.3 | 1.9 |
| dusty blue 7f9ab5 | 1.6 | 1.9 | 2.2 | 1.5 | 1.2 | 4.5 | 5.5 | 1.5 | 1.4 | 1.2 | 3.3 | 1.8 | 3.9 | 1.8 | 1.1 | 5.9 | 2.4 |
| red b3262e | 3.6 | 4.2 | 4.9 | 3.3 | 1.9 | 2.0 | 2.5 | 1.5 | 3.0 | 2.6 | 1.5 | 3.9 | 1.8 | 4.0 | 2.5 | 2.7 | 5.3 |

Bg relative luminances: greige .53, oat .63, bone .75, light concrete .48, mid concrete .25, charcoal .03, navy .015, terracotta .20, sage .44, dusty blue .37, walnut .06, sand .58, forest .04, blush .60, mustard .36, black marble .01, white marble .80.

Colour pairing table (recommended / acceptable / avoid):

| Garment | Best backgrounds (ratio>=5) | Acceptable (3-5) | Avoid (<2.5) |
|---|---|---|---|
| Black | bone paper, oat linen, greige plaster, light concrete, white/Carrara marble, warm sand, blush | mid concrete, sage, terracotta | charcoal, navy, walnut, forest, black marble |
| Charcoal / forest / burgundy | bone, oat, greige, light concrete, warm sand, blush, white marble, sage | mid concrete, mustard | charcoal, navy, black marble, walnut |
| Navy | bone, oat, greige, sand, blush, light concrete, white marble, sage | mid concrete, terracotta (complement, accent only) | charcoal, navy, forest, black marble |
| Heather grey / dusty blue | charcoal slate, deep navy, black marble, forest, walnut(3.3-3.5) | dark walnut | greige, concrete, bone, sage |
| Sand / tan / sage | charcoal, navy, black marble, walnut, forest | - | greige, oat, sand, mustard |
| Cream / white | charcoal, navy, forest, walnut, black marble, terracotta (3.5-3.9) | mid concrete (2.8-3.1), mustard | bone, oat, warm sand, blush, white marble, light concrete |
| Red | bone, oat, white marble, blush, sand | greige, light concrete, sage | terracotta, walnut, forest, mid concrete |

Rule of the three colours per frame: bg dominant (60%), garment (30%), accent (10% = dog-breed print colour or a prop).

### B.4 Concept library (52 named backgrounds)
Kind key: P = person/model cutout, F = flat-lay garment, Fo = folded garment/stack, C = cap. Source key (how to produce, section C): PROC = procedural numpy/PIL (bgkit.py), TEX = CC0 texture (Poly Haven/ambientCG) + grading, PHOTO = real photograph (own shoot or Unsplash/Pexels/Pixabay, licence caveat #30/#31), COMP = composite of several.
Garments: D = dark (black/charcoal/navy/forest/burgundy), L = light (cream/white/sand/sage/heather/dusty blue), M = mid/colour.

**Studio sweeps / seamless colour-matched**
1. **Greige Studio Sweep** - warm greige wall-to-floor curve, soft upper-left light pool; D, M; P,F,Fo,C; PROC (`sweep`).
2. **Bone Paper Sweep** - nearly white warm paper, long soft shadow; D, red; P,F,Fo,C; PROC/TEX.
3. **Charcoal Cyclorama** - charcoal sweep with back rim-light halo; L garments; P,Fo,C; PROC.
4. **Deep Navy Tonal Sweep** - dark navy with spot pool; L garments (cream/white/sand); P,F,Fo,C; PROC.
5. **Dusty Blue Seamless** - mid dusty-blue paper; D, cream; P,Fo,C; PROC.
6. **Terracotta Seamless + Sun Slash** - terracotta paper with one hard diagonal sunbeam; navy, black, cream; P,Fo,C; PROC+gobo.
7. **Sage Seamless** - pale sage paper; black/navy/cream; P,F,Fo,C; PROC.
8. **Blush Seamless** - blush pink paper; black, navy, forest; P,F,Fo,C; PROC.
9. **Mustard Arch Shadow** - ochre wall with soft arch shadow; black/navy/white; P,Fo,C; PROC+gobo.
10. **Olive Clay Seamless** - olive/clay earth paper; tan/cream/orange prints; P,Fo; PROC.

**Textured walls, surfaces, stones**
11. **Venetian Plaster Greige** - soft cloudy trowel marks; D; P,F,Fo,C; PROC `plaster`.
12. **Limewash Sand Wall** - warm sand limewash with brush drift; D, navy; P,Fo,C; PROC/TEX.
13. **Light Raw Concrete** - pale concrete with pores; D, M; P,F,Fo,C; PROC `concrete` / TEX.
14. **Board-Formed Dark Concrete** - charcoal concrete with plank lines; L; P,Fo,C; TEX.
15. **Polished Concrete Floor (reflective)** - satin concrete with subtle reflection; D/L; P,Fo,C; TEX + reflection.
16. **Natural Linen Weave** - oat linen close-up weave; D; F,Fo,C; PROC `linen`.
17. **Handmade Deckle Paper** - bone cotton paper with fibres; D; F,Fo,C; PROC `paper`.
18. **Walnut Table Top** - dark walnut grain, top-down; L garments; F,Fo,C; PROC `wood`/TEX.
19. **Light Oak Planks** - pale oak boards, top-down; D, navy; F,Fo,C; TEX.
20. **Birch Plywood** - pale plywood, visible veneers; D; F,Fo,C; TEX.
21. **Carrara White Marble** - white marble soft grey veins; D (esp. black); F,Fo,C; PROC `marble`/TEX.
22. **Nero Marquina Black Marble** - black marble white veins (restrained); L garments; F,Fo,C; PROC `marble` inverted/TEX.
23. **Cream Terrazzo** - cream with muted chips; D, navy, forest; F,Fo,C; PROC `terrazzo`.
24. **Travertine Slab** - warm travertine with pits; D, navy; F,Fo,C; TEX.
25. **Slate Stone Slab** - dark slate, matt; L garments; F,Fo,C; TEX.
26. **Charcoal Wool Felt** - dark felt with fibres; L garments; F,Fo,C; PROC (noise + blur) / TEX.
27. **Artist Canvas Drop Cloth** - raw canvas weave, slight wrinkle; D; F,Fo,C; TEX.
28. **Cognac Leather Desk** - tan leather grain; navy/black/cream; F,Fo,C; TEX.

**Light and shadow (gobo / window light)**
29. **Window Pane Light on Plaster** - 4-6 pane light patches, perspective-skewed, blur 20-30 px; D,M; P,F,Fo,C; PROC `gobo('window')` (tested).
30. **Venetian Blind Stripes** - diagonal warm stripes across wall+floor; D; P,Fo,C; PROC `gobo('blinds')`.
31. **Monstera/Palm Leaf Shadow on Wall** - soft leaf shadows, blur 18-30 px; D, cream; P,F,Fo,C; PROC `gobo('leaves')` or photographed shadow.
32. **Dappled Tree Light on Linen** - dapple speckles at 6-12% coverage; D; F,Fo,C; PROC.
33. **Arched Doorway Sun on Sand Wall** - one arch-shaped hard light; navy/black; P,Fo; PROC+polygon gobo.
34. **Spot Pool on Dark Wall** - elliptical hard spotlight, falloff to near black; L garments; P,Fo,C; PROC radial gradient + grain.
35. **Hardwood Floor with Window Stripes** - oak floor, top-down, window light stripes; D; F,Fo; TEX + gobo.

**Lifestyle photographs (real photography, shallow DOF; owner's "real photography" ask)**
36. **Alley Brick Wall, Golden Hour** - real warm brick wall defocused (not procedural bricks); D/L; P; PHOTO.
37. **Concrete Steps / Skate Plaza** - grey steps, soft light; D/M; P; PHOTO.
38. **City Street Night Bokeh** - warm/cool bokeh, wet street; L garments; P; PHOTO.
39. **Park Lawn Backlit Golden Hour** - green lawn, backlit trees, bokeh; D/M; P; PHOTO.
40. **Beach Dunes Soft Sand** - pale sand, haze, sea blur; D/navy; P,Fo,C (on sand texture); PHOTO.
41. **Forest Trail (Ruffwear mood)** - dirt trail, trees blurred; D/M; P; PHOTO.
42. **Autumn Leaves Path** - warm leaf carpet; navy/cream/D; P,F; PHOTO.
43. **Snowy Morning Trail** - cool, low-saturation; D/red/forest; P; PHOTO.
44. **Meadow Dog Park** - wildflower meadow bokeh; D/M; P; PHOTO.
45. **Cosy Sofa + Window Light Interior** - blurred living room, warm light; D/M; P; PHOTO.
46. **Cafe Window Table** - blurred cafe, wood table; D/M; P,F,Fo,C (table plane); PHOTO.
47. **Modern Minimal Room with Plant** - light plaster wall, plant, daylight (Essentials-style #35); D; P; PHOTO.
48. **Porch / Wooden Deck at Sunset** - warm deck boards, bokeh; D/M; P,F,Fo,C; PHOTO.
49. **Gallery Wall with Picture-Rail Shadow Lines** - white wall, thin shadow lines; D; P,F; COMP/PROC.
50. **Boutique Clothing Rail Interior** - blurred rail and shelves; D/M; P,Fo; PHOTO.
51. **Rooftop Skyline at Dusk** - blue-hour haze skyline; L garments; P; PHOTO.
52. **Tonal Color-Block Duo** - two-tone wall/floor split (e.g., sage wall + oat floor) with soft shadow; D, cream; P,F,Fo,C; PROC.

Matching rule by subject kind (summary):
* People (P): sweeps (1-10), plaster/limewash/concrete walls (11-14), gobo walls (29-34), all lifestyle photos (36-52, which must carry a visible ground plane; stand the person on the ground region y>=62% of the photo, camera height ~ chest level) and gallery/boutique.
* Flat-lay (F): top-down surfaces only - 11, 13, 16-28, 35, 29-32 gobos, 46/48 tabletop crops. No perspective vanishing lines in the surface.
* Folded (Fo): same as F plus sweeps (stand on floor with horizon at 55-65%) and shelves/steps; folded stacks also work on 15 with reflection.
* Cap (C): small subject; use calm low-texture surfaces (1, 2, 11, 21, 22, 34) or an out-of-focus lifestyle plate with a ground plane; props: dog tag/leash only if kept <12% area.

### B.5 Moving the scene (10 s)
* Structure: bg plate layer (1.2x size), subject layer, optional foreground blur layer, finishing (vignette + grain per frame). Order: bg -> bg gobo -> shadow -> subject -> light-wrap/rim -> foreground blur -> vignette -> grain.
* Gobo drift: translate gobo mask 12-30 px over 10 s (cloud/shadow movement) - cheap, large "photo-video" effect [eng].
* Avoid: the same background family back-to-back; vary hue family AND texture family each day (owner rule).

---------------------------------------------------------------------
## (c) Producing each concept programmatically

### C.1 Route per concept
| Concepts | Route | Notes |
|---|---|---|
| 1-10, 52 | PROC `sweep()` + colour params | vertical gradient with smoothstep horizon at 0.55-0.65, soft = 0.15-0.20; light pool exponent; grain on top. Paper variants add `paper()` fibres at 3-5% amplitude |
| 11-13, 16-17, 18, 21-23, 26 | PROC functions in bgkit.py below, or CC0 TEX | verified to run at 1080x1920 |
| 14, 15, 19, 20, 24, 25, 27, 28 | TEX: download 2K diffuse maps from Poly Haven/ambientCG (CC0, #32, #47), `polydown textures -s 2k -tf png --maps Diffuse` (#56) or API api.polyhaven.com (respect API terms, #47) | tile/crop to 1080x1920, grade with Lab shift to palette, add vignette+grain |
| 29-35 | PROC `gobo()` (multiply a blurred pane/stripe/leaf mask; blur 18-30 px; strength .25-.45) over any wall/floor; per #12, #13 farther gobo = more blur | for hard sun: blur 6-10 px, strength .5 |
| 36-51 | PHOTO: shoot your own (best licence) or CC0/Unsplash/Pexels (check #30, #31: no recognisable people/trademarks; keep source URL + licence in a manifest); crop 9:16, lower bg contrast 10-20% (#44), add haze (#43), apply vignette+grain | require a visible ground plane for people; pre-grade bg so key light is upper-left or flip horizontally to match |

### C.2 Compositing recipe order (per frame)
1. Prepare cutout: premultiplied alpha, erode 1 px, feather 0.8-1.2 px (halo defence #2, #16).
2. Scale to target (B.2), anchor to ground line.
3. Colour: tint <=6% toward bg mean colour; do NOT shift garment hue. If more cohesion is needed, apply Reinhard Lab transfer (#38, #39) at strength 0.05-0.15 only to L (lightness) and 0.05 to a/b.
4. Shadows (tight + ambient), tinted from bg 5th percentile x0.45 (#2, #26), squashed about the ground line.
5. Optional reflection (glossy surfaces): flipped alpha, start at contact, opacity .35-.45, steep fade, blur growing 2->8 px (#45, #46, #58).
6. Light-wrap: blur bg 30-40 px, screen at 25-40% inside 3-6 px of subject edge on the key side.
7. Foreground blur element, vignette, grain.
8. Checks (#2): blur-heavy, invert, desaturate, thumbnail 120x213: subject must still separate and no halo.

### C.3 Working code (tested on this machine: Python 3 + numpy + PIL; synthetic cutout, 1080x1920)
Saved as /home/claude/research/bgkit.py (same code as below). Known limits: plaster/concrete amplitude is subtle (raise `dark/light` spread for more texture); reflection stub is intentionally not implemented in `composite` - add the flipped-alpha recipe from C.2.5; leaf gobo is a rough polygon approximation.

```python
import numpy as np
from PIL import Image, ImageFilter, ImageDraw
W,H=1080,1920
rng=np.random.default_rng(7)

def fbm(h,w,octaves=6,base=4,persist=.5,seed=0):
    """multi-octave value noise, 0..1. Core of plaster/concrete/paper/marble."""
    r=np.random.default_rng(seed); out=np.zeros((h,w),np.float32); amp=1; tot=0
    for o in range(octaves):
        n=base*2**o
        g=r.random((n+1,int(n*w/h)+2)).astype(np.float32)
        im=Image.fromarray(g).resize((w,h),Image.BICUBIC)
        out+=amp*np.asarray(im); tot+=amp; amp*=persist
    out/=tot; return (out-out.min())/(out.max()-out.min()+1e-9)

def tint(gray,dark,light):
    d=np.array(dark,np.float32); l=np.array(light,np.float32)
    return d+(l-d)*gray[...,None]

def plaster(dark=(176,164,148),light=(214,204,190),seed=1):
    a=fbm(H,W,6,3,.55,seed); b=fbm(H,W,3,2,.5,seed+9)
    g=.65*a+.35*b                     # cloudy trowel marks
    return tint(g,dark,light)

def concrete(dark=(120,120,118),light=(176,176,172),seed=2,pores=900):
    g=.6*fbm(H,W,7,3,.6,seed)+.4*fbm(H,W,3,2,.5,seed+3)
    im=tint(g,dark,light)
    p=np.zeros((H,W),np.float32); r=np.random.default_rng(seed)
    ys,xs=r.integers(0,H,pores),r.integers(0,W,pores); p[ys,xs]=1
    p=np.asarray(Image.fromarray((p*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.6)),np.float32)/255
    return np.clip(im-p[...,None]*90,0,255)   # blown pores

def linen(base=(214,205,188),seed=3,pitch=5):
    y,x=np.mgrid[0:H,0:W]
    warp=.5+.5*np.sin(2*np.pi*x/pitch+fbm(H,W,4,6,.5,seed)*4)
    weft=.5+.5*np.sin(2*np.pi*y/pitch+fbm(H,W,4,6,.5,seed+1)*4)
    slub=fbm(H,W,5,20,.5,seed+2)
    g=.35*warp+.35*weft+.3*slub
    return np.array(base,np.float32)*(0.88+.24*g)[...,None]

def paper(base=(232,226,212),seed=4):
    g=fbm(H,W,5,60,.55,seed)         # fibres: high base freq
    return np.array(base,np.float32)*(0.95+.07*g)[...,None]

def wood(dark=(70,48,32),light=(120,86,58),seed=5):
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    n=fbm(H,W,5,3,.5,seed)
    rings=.5+.5*np.sin((y*.045+n*18))
    fine=fbm(H,W,6,40,.6,seed+1)
    g=.6*rings+.4*fine
    return tint(g,dark,light)

def marble(base=(236,234,230),vein=(110,112,118),seed=6):
    n=fbm(H,W,6,3,.5,seed); n2=fbm(H,W,6,3,.5,seed+5)
    y,x=np.mgrid[0:H,0:W].astype(np.float32)
    v=np.abs(np.sin((x/W*3+y/H*1.4+n*2.2+n2*1.2)*np.pi))
    v=np.clip(1-v*9,0,1)**2           # thin veins
    cloud=fbm(H,W,4,2,.5,seed+9)
    im=np.array(base,np.float32)*(0.96+.05*cloud)[...,None]
    return im*(1-v[...,None])+np.array(vein,np.float32)*v[...,None]*.9

def terrazzo(base=(226,218,204),chips=((150,120,100),(110,118,108),(190,170,140),(80,80,84)),n=420,seed=7):
    r=np.random.default_rng(seed); im=Image.fromarray(paper(base,seed).astype(np.uint8)); d=ImageDraw.Draw(im)
    for _ in range(n):
        cx,cy=r.integers(0,W),r.integers(0,H); R=r.integers(6,34); k=r.integers(5,9)
        a=np.sort(r.random(k))*2*np.pi; rad=R*(.6+.4*r.random(k))
        d.polygon([(cx+np.cos(t)*q,cy+np.sin(t)*q) for t,q in zip(a,rad)],fill=chips[r.integers(len(chips))])
    return np.asarray(im,np.float32)

def sweep(top=(205,196,183),floor=(176,166,152),horizon=.62,soft=.18,seed=8):
    """seamless studio sweep: wall->floor curve, light pool upper-left"""
    y=np.linspace(0,1,H)[:,None]; t=np.clip((y-(horizon-soft))/(2*soft),0,1); t=t*t*(3-2*t)
    col=np.array(top)*(1-t[...,None])+np.array(floor)*t[...,None]
    col=np.broadcast_to(col,(H,W,3)).copy()
    yy,xx=np.mgrid[0:H,0:W]; pool=np.exp(-(((xx-W*.3)/(W*.9))**2+((yy-H*.3)/(H*.55))**2))
    return col*(0.82+.28*pool[...,None])

def gobo(img,kind='window',angle=-14,strength=.38,blur=26,seed=0):
    """multiply a blurred shadow pattern: window panes / blinds / leaves"""
    m=Image.new('L',(W*2,H*2),255); d=ImageDraw.Draw(m)
    if kind=='window':
        for i in range(2):
            for j in range(3):
                x0=int(W*.25+i*W*.55); y0=int(H*.15+j*H*.42)
                d.rectangle([x0,y0,x0+int(W*.48),y0+int(H*.36)],fill=0)
        # lit panes are 0 => invert later; here lit=white
    elif kind=='blinds':
        for k in range(0,H*2,130): d.rectangle([0,k,W*2,k+70],fill=0)
    elif kind=='leaves':
        r=np.random.default_rng(seed)
        for _ in range(55):
            cx,cy=r.integers(0,W*2),r.integers(0,H*2); a=r.random()*6.28
            L=r.integers(90,260); wd=r.integers(25,60)
            pts=[(cx+np.cos(a)*L*s,cy+np.sin(a)*L*s+np.sin(s*3.14)*wd*c) for s in np.linspace(0,1,12) for c in (1,)]
            pts+=[(cx+np.cos(a)*L*s,cy+np.sin(a)*L*s-np.sin(s*3.14)*wd) for s in np.linspace(1,0,12)]
            d.polygon(pts,fill=0)
    if kind=='window': m=Image.eval(m,lambda v:255-v)  # panes = shadow-free light
    m=m.rotate(angle,resample=Image.BICUBIC,fillcolor=255).resize((W,H)).filter(ImageFilter.GaussianBlur(blur))
    a=np.asarray(m,np.float32)/255
    return img*(1-strength*(1-a))[...,None]

def vignette(img,amt=.14,power=2.4):
    yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)/1.414
    return img*(1-amt*np.clip(r,0,1)**power)[...,None]

def grain(img,sigma=6,seed=None,shadow_boost=1.0):
    r=np.random.default_rng(seed)
    n=r.normal(0,sigma,(H,W)).astype(np.float32)
    n=np.asarray(Image.fromarray(np.clip(n*4+128,0,255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(.5)),np.float32)
    n=(n-n.mean())/4
    lum=img.mean(2,keepdims=True)/255; w=1+shadow_boost*(1-lum)*.6
    return np.clip(img+n[...,None]*w,0,255)

def shadow_layer(alpha,offset=(8,16),sigma=18,opacity=.3,color=(30,24,20),squash=1.0,base_y=0):
    """alpha: HxW float 0..1 of the cutout placed on canvas. returns RGBA-ish (color, a)"""
    a=Image.fromarray((alpha*255).astype(np.uint8))
    a=a.transform(a.size,Image.AFFINE,(1,0,-offset[0],0,1/squash,base_y-base_y/squash-offset[1]))  # squash about the ground line
    a=a.filter(ImageFilter.GaussianBlur(sigma))
    return np.asarray(a,np.float32)/255*opacity

def composite(bg,cut_rgba,anchor_xy,scale_h,bg_tint=None,light_xy=(-1,-1),
              contact=True,ambient=True,reflect=0.0,shadow_col=None):
    """cut_rgba: PIL RGBA (transparent cutout). anchor_xy=(cx,bottom_y) in canvas px,
    scale_h = target height px. Subject colour is NOT altered except <=6% ambient tint."""
    cw,ch=cut_rgba.size; s=scale_h/ch
    c=cut_rgba.resize((max(1,int(cw*s)),scale_h),Image.LANCZOS)
    arr=np.asarray(c,np.float32); a=arr[...,3]/255
    # defringe: erode alpha 1px then 0.8px feather
    am=Image.fromarray((a*255).astype(np.uint8)).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(.8))
    a=np.asarray(am,np.float32)/255
    rgb=arr[...,:3]
    if bg_tint is not None: rgb=rgb*(1-.06)+np.array(bg_tint,np.float32)*.06
    x0=int(anchor_xy[0]-c.size[0]/2); y0=int(anchor_xy[1]-c.size[1])
    full=np.zeros((H,W),np.float32)
    ys0,xs0=max(0,y0),max(0,x0); ys1,xs1=min(H,y0+c.size[1]),min(W,x0+c.size[0])
    full[ys0:ys1,xs0:xs1]=a[ys0-y0:ys1-y0,xs0-x0:xs1-x0]
    out=bg.copy()
    dark=np.array(shadow_col if shadow_col is not None else np.percentile(bg.reshape(-1,3),5,axis=0)*.45,np.float32)
    ox=-light_xy[0]; oy=-light_xy[1]
    if ambient:
        sh=shadow_layer(full,(ox*14,abs(oy)*30),sigma=38,opacity=.28,squash=.35,base_y=anchor_xy[1])
        out=out*(1-sh[...,None])+dark*sh[...,None]
    if reflect>0:
        flip=full[::-1]; fade=np.clip(1-(np.arange(H)[:,None]-anchor_xy[1])/320,0,1)
        # (flat reflection recipe: shift flipped alpha so it starts at bottom_y; omitted for brevity)
    if contact:
        sh=shadow_layer(full,(ox*3,5),sigma=6,opacity=.5,squash=.97,base_y=anchor_xy[1])
        out=out*(1-sh[...,None])+dark*sh[...,None]
    fr=np.zeros((H,W,3),np.float32); fr[ys0:ys1,xs0:xs1]=rgb[ys0-y0:ys1-y0,xs0-x0:xs1-x0]
    out=out*(1-full[...,None])+fr*full[...,None]
    return out

def finish(img,vig=.14,gr=5):
    return Image.fromarray(np.clip(grain(vignette(img,vig),gr),0,255).astype(np.uint8))

def zoom_crop(im,z,dx=0.0,dy=0.0):
    """sub-pixel zoom about canvas centre (+drift dx,dy px) -> W x H frame. im is a PIL image >= W x H.
    Uses AFFINE+BICUBIC (float coords) -> no integer-rounding jitter."""
    w,h=im.size; sx=w/W
    a=1/z*sx; cx=w/2+dx*sx; cy=h/2+dy*sx
    return im.transform((W,H),Image.AFFINE,(a,0,cx-a*W/2,0,a,cy-a*H/2),resample=Image.BICUBIC)

def parallax_frame(bg,sub_layer,fg_layer,t,T=10.0):
    """bg/sub/fg: RGB/RGBA PIL layers at canvas size (bg ideally 1.2x). Subject moves less than fg, more than bg.
    bg 1.00->1.05, subject 1.00->1.025, fg blur elements 1.00->1.12 (my engineering values)."""
    k=t/T; e=k*k*(3-2*k)                         # smoothstep ease
    f=zoom_crop(bg,1+.05*e,dx=-10*e)
    f=f.convert('RGBA'); f.alpha_composite(zoom_crop(sub_layer,1+.025*e,dx=-5*e))
    if fg_layer is not None: f.alpha_composite(zoom_crop(fg_layer,1+.12*e,dx=14*e))
    return f.convert('RGB')
```

### C.4 ffmpeg assembly (frames rendered by Python at 24-30 fps, sub-pixel affine crop avoids integer-rounding jitter)
```bash
# frames -> 10 s reel; grain already baked per frame. If using ffmpeg zoompan on a still instead, upscale first (#40):
ffmpeg -y -framerate 30 -i frames/%04d.png -c:v libx264 -crf 17 -preset slow -pix_fmt yuv420p -vf "format=yuv420p" -movflags +faststart out.mp4
# still-image alternative (smooth zoom): upscale 4x before zoompan, centred zoom 1.00->1.05 over 300 frames
ffmpeg -y -loop 1 -i still.png -vf "scale=4320:7680,zoompan=z='1+0.05*on/300':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=300:s=1080x1920:fps=30" -t 10 out.mp4
# ffmpeg-only grain + vignette on a finished clip
ffmpeg -i in.mp4 -vf "noise=alls=7:allf=t+u,vignette=PI/5" -c:v libx264 -crf 17 out.mp4
```
Note: the `noise`/`vignette` flags and the 4x-upscale zoompan expression follow the zoompan parameters documented in #40/#53; their exact visual strength is [eng] and untested here. The "upscale before zoompan" advice is sourced (#40); the claim that it removes jitter is not confirmed by the sources.

### C.5 Real-photo workflow (for concepts 36-51)
1. Curate 30-60 plates from own phone shots (best: no licence risk), then CC0/Unsplash/Pexels; record URL+licence in `backgrounds/manifest.json`.
2. Reject plates with recognisable faces, readable logos, strong horizon tilt, no ground plane (people) or visible perspective lines (flat-lay).
3. Crop 9:16 at >=2160x3840 (so parallax zoom 1.2x stays sharp).
4. Apply: bg contrast -10..-20%, desaturate 6-12%, black-lift 4-8, warm/cool grade to chosen palette family, key-light direction normalised to upper-left (flip if needed).
5. Automate a "plate score" (mean L in ground area, edge density, colour distance to garment) and pick only plates whose garment ratio >= 3.0 (table B.3).
6. Cache; never reuse a plate or texture within the same 14-day window (owner variety rule).

### C.6 Acceptance checklist (for the automated reviewer)
* garment-to-bg ratio >= 3.0 (B.3); hero inside y 270-1440, x 100-940; ground shadow present and tinted; shadow direction consistent; no halo (invert test); thumbnail legible; no text over merchandise; grain present on subject and bg alike; plate not repeated in last 14 days; garment mean colour change <= 6% of original (colour fidelity).

# AlphaDog Art Analyzer — spec v1 (2026-10-28)

Owner rule: more rigorous than loose. Art must be beautiful AND work on the products/media.
Two layers: **A. Technical (measured in code, objective)** and **B. Critic panel (Gemini vision, 14 roles)**. Hard fails override scores.

## A. Technical checks (scripts/analyze_tech.py)
| # | Check | Why (source) | Gate |
|---|---|---|---|
| T1 | Pixel size vs print areas: full front 4500×5400 @300dpi, chest 4", cap 1200×720 | 300 dpi at physical size; upscaling blurs (Printify PNG guide) | upscale factor reported; >4× = REWORK |
| T2 | Background separability: flood-fill from edges; share of subject edge that is near-white | JPEG/white boxes print as boxes; must be transparent PNG | <80% clean separation = REWORK |
| T3 | Soft edges / semi-transparent risk: share of boundary pixels in mid-tones after cutout | Semi-transparent pixels → chalky underbase halo on dark tees | >25% = REWORK |
| T4 | Gradient load: share of subject in smooth gradients | Gradients print patchy on dark DTG; need halftone 35–45 LPI | >40% = flag |
| T5 | Palette: colors covering 95% of subject (k-means) | Embroidery ≤6 thread colors (Printify) | >6 = cap needs separate simplified art |
| T6 | Fine-detail survival at left-chest 4" and 1.5" thumbnail | Detail lost when small; thumbnails sell | survival <0.55 = flag |
| T7 | Garment contrast per color (white, black, heather gray, navy, sand) | Light art disappears on light shirts (print checklists) | min usable garments <2 = REWORK |
| T8 | Near-white share of subject | White fur on white tee vanishes; on dark needs heavy underbase | report + garment rules |
| T9 | Composition: fill ratio, centering, L/R symmetry | Front-facing icon set must be centered & symmetric | asymmetry >0.25 = flag |
| T10 | Edges touching canvas | Cropped art | any = REWORK |

## B. Critic panel (scripts/critic.py) — one structured JSON verdict per image
Pros: 1 Art director · 2 DTG/DTF print technician · 3 Embroidery digitizer · 4 AI-artifact inspector · 5 IP/compliance reviewer · 6 Series/brand designer (replicable to 25 breeds) · 7 Marketplace merchandiser (Etsy/eBay/TikTok thumbnail, saturation) · 8 Breed expert (accuracy) · 9 Likeness judge (vs Linda photo)
Customers: 10 Gen-Z TikTok shopper · 11 Millennial dog mom · 12 Male owner 35–55 · 13 Gift buyer · 14 Art lover/collector
Each: score 0–10 (calibrated: 5 = average sellable POD design, 9–10 rare), top problems, concrete fixes; customers add would_buy + price they'd pay.
Hard fails: any text/letters/watermark; resemblance to a specific famous artwork or protected character; major anatomy/eye artifact; not readable as the breed; art cropped; background not removable.

## Verdict
- PASS: no hard fail, weighted score ≥ 7.5, no tech REWORK.
- REWORK: fixable issues (prompt or post-processing).
- REJECT: hard fail or score < 5.5.
Weights: pros 60% (art director 10, print 10, artifacts 10, series 10, merchandiser 10, IP gate, others 4 each), customers 40%.

## v1.1 changes (after first runs)
- Verdict now judges CONCEPT (art + market + customers). Print/embroidery issues that the pipeline can fix automatically (upscale, background removal, hard alpha, despeckle, halftone) are listed as auto-fixes, not rejections. Only issues needing regeneration (low garment contrast, cropped art, detail lost small) block.
- PASS bar: concept >= 7.5, >= 4/5 customer personas would buy, their average price >= $24 (our tee price), no concept hard-fail.
- Critic model: gemini-3.1-pro-preview (2.5-pro retired for new users). ~7.5k tokens per review.
- Role ids normalized (model sometimes returns numbers).

## Results so far (Linda pilot)
- Round 1 (14 styles): best concept 6.25 (tattoo flash), 6.23 (pop art), 6.11 (groovy 70s). Nothing passes. Common critique: "generic AI pet portrait with a style filter", customers' price ceiling $8–24, below our $24 tee.
- Round 2 (9 REWORKs, prompts rewritten by critics): print-cleaner (white bg, hard edges, white coat) but blander; best 6.36 (folk embroidery). Lesson: don't fix print constraints by dumbing down the prompt — generate rich art, then fix production in automated post-processing.

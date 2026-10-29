# Art Analyzer Report

PASS needs: concept >= 6.8 (beats best market reference 6.77), >= 3/5 customers buy, avg price >= $20, no concept hard-fail, nothing needing regeneration.

| Rank | Design | Verdict | Concept | Pros | Customers | Would buy | Avg $ | Print | Cap | Auto-fixes | Needs regen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | r1_stencil | **REWORK** | 5.6 | 6.0 | 5.0 | 2/5 | 20.0 | 5 | 7 | 2 | - |
| 2 | r1_bridges | **REWORK** | 5.57 | 6.09 | 4.8 | 2/5 | 18.0 | 5 | 7 | 1 | - |
| 3 | r1_solid | **REJECT** | 5.04 | 5.33 | 4.6 | 2/5 | 18.0 | 6 | 6 | 1 | - |
| 4 | r1_badge | **REJECT** | 4.76 | 5.0 | 4.4 | 3/5 | 12.0 | 4 | 6 | 1 | - |

## r1_stencil — REWORK (concept 5.6)
Reads as: minimalist vector stencil silhouette
Scores: art_director=6, series_designer=7, marketplace_merchandiser=5, ai_artifact_inspector=6, breed_expert=6, likeness_judge=5, ip_compliance_reviewer=7, print_technician=5, embroidery_digitizer=7, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=5, gift_buyer=6, art_lover=4
Strengths: High contrast scales well for embroidery and left-chest prints.; Highly replicable style for a 25-breed series.; Clean, recognizable silhouette.
Must fix: Clean 12036px stray marks from the background.; Create an inverted white-ink version for dark tees.; Upscale >4x or vectorize for full front printing.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Too basic, looks like a millennial mom bumper sticker. | millennial_dog_mom: Cute but a bit stark in just black and white. | male_owner_35_55: A bit too cute with the tongue out. | gift_buyer: Safe bet, but maybe too generic. | art_lover: Zero artistic soul. It's a sterile vector trace.

## r1_bridges — REWORK (concept 5.57)
Reads as: Bold vector line art / high-contrast silhouette
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=6, likeness_judge=4, ip_compliance_reviewer=7, print_technician=5, embroidery_digitizer=7, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=5, gift_buyer=6, art_lover=3
Strengths: Clean, scalable lines; High contrast; Embroidery friendly
Must fix: Vectorize to fix low resolution for large prints; Create a dark-garment version with a white outer stroke
Auto-fixes in post: AI upscale to 4500 px
Customer reactions: genz_tiktok_shopper: Too basic, looks like a stock vector. | millennial_dog_mom: Cute, but the white tongue is weird. | male_owner_35_55: A bit too cutesy with the scalloped edges. | gift_buyer: Safe, but maybe too generic. | art_lover: Soulless vector art.

## r1_solid — REJECT (concept 5.04)
Reads as: solid black vector silhouette
Scores: art_director=5, series_designer=5, marketplace_merchandiser=5, ai_artifact_inspector=6, breed_expert=6, likeness_judge=4, ip_compliance_reviewer=7, print_technician=6, embroidery_digitizer=6, genz_tiktok_shopper=4, millennial_dog_mom=5, male_owner_35_55=6, gift_buyer=5, art_lover=3
Strengths: High contrast reads well at very small sizes.; Easily convertible to vector format.; Simple enough for basic chest embroidery.
Must fix: Vectorize to fix the 12.8x upscale requirement.; Create an inverted white version for dark garments.; Fix the unsettling eye shapes.
Auto-fixes in post: AI upscale to 4500 px
Customer reactions: genz_tiktok_shopper: Too basic. Gives generic craft-store vibes. | millennial_dog_mom: The eyes look a little scary and intense. | male_owner_35_55: A bit too much solid black for a big shirt print, might feel stiff. | gift_buyer: Safe but a bit boring. Doesn't look very expensive. | art_lover: Zero originality. Looks like a bucket-fill tool was used on a stock photo.

## r1_badge — REJECT (concept 4.76)
Reads as: High-contrast negative space vector badge
Scores: art_director=5, series_designer=6, marketplace_merchandiser=4, ai_artifact_inspector=5, breed_expert=5, likeness_judge=4, ip_compliance_reviewer=6, print_technician=4, embroidery_digitizer=6, genz_tiktok_shopper=4, millennial_dog_mom=5, male_owner_35_55=5, gift_buyer=5, art_lover=3
Strengths: High contrast reads well at small sizes.; Easily adaptable for embroidery if the background is removed.; Scalable format for a multi-breed series.
Must fix: Remove the solid black background circle to ensure printability on both dark and light garments.; Fix the irregular notch on the right eye.; Adjust the outer fur edge to be curly rather than spiky.
Auto-fixes in post: AI upscale to 4500 px
Customer reactions: genz_tiktok_shopper: Too basic, looks like a corporate logo. | millennial_dog_mom: A bit stark and heavy with all the black. | male_owner_35_55: Giant black circle on a shirt is uncomfortable. | gift_buyer: Safe, but unexciting. | art_lover: Zero artistic merit, looks auto-traced.
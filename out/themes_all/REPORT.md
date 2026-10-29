# Art Analyzer Report

PASS needs: concept >= 6.8 (beats best market reference 6.77), >= 3/5 customers buy, avg price >= $20, no concept hard-fail, nothing needing regeneration.

| Rank | Design | Verdict | Concept | Pros | Customers | Would buy | Avg $ | Print | Cap | Auto-fixes | Needs regen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | pfl31_sil_solid | **REWORK** | 6.57 | 6.82 | 6.2 | 3/5 | 24.6 | 7 | 6 | 3 | - |
| 2 | pfl31_geo_poly | **REWORK** | 6.51 | 6.45 | 6.6 | 3/5 | 24.0 | 5 | 7 | 2 | - |
| 3 | pnb21_sil_solid | **REWORK** | 6.27 | 6.58 | 5.8 | 3/5 | 21.6 | 4 | 6 | 2 | - |
| 4 | ppro3_sil_stencil | **REWORK** | 6.13 | 6.49 | 5.6 | 3/5 | 15.0 | 6 | 7 | 2 | - |
| 5 | pfl31_geo_circles | **REWORK** | 6.03 | 6.31 | 5.6 | 4/5 | 25.6 | 6 | 7 | 2 | - |
| 6 | ppro3_geo_circles | **REWORK** | 5.93 | 6.42 | 5.2 | 3/5 | 24.6 | 7 | 6 | 2 | - |
| 7 | pnb21_geo_circles | **REWORK** | 5.89 | 6.22 | 5.4 | 3/5 | 23.2 | 6 | 6 | 2 | - |
| 8 | ppro3_sil_solid | **REWORK** | 5.87 | 6.18 | 5.4 | 3/5 | 16.4 | 6 | 7 | 2 | - |
| 9 | pnb21_sil_stencil | **REWORK** | 5.84 | 6.27 | 5.2 | 3/5 | 15.0 | 6 | 7 | 2 | - |
| 10 | pnb21_geo_poly | **REWORK** | 5.65 | 5.82 | 5.4 | 3/5 | 21.4 | 6 | 6 | 2 | - |
| 11 | ppro3_geo_poly | **REWORK** | 5.63 | 5.91 | 5.2 | 3/5 | 20.4 | 6 | 7 | 2 | - |
| 12 | pfl31_sil_stencil | **REJECT** | 5.32 | 5.67 | 4.8 | 3/5 | 19.6 | 4 | 6 | 2 | - |

## pfl31_sil_solid — REWORK (concept 6.57)
Reads as: High-contrast vector silhouette with negative space line art
Scores: art_director=7, series_designer=7, marketplace_merchandiser=7, ai_artifact_inspector=7, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=7, print_technician=7, embroidery_digitizer=6, genz_tiktok_shopper=6, millennial_dog_mom=7, male_owner_35_55=7, gift_buyer=7, art_lover=4
Strengths: Clean, scalable vector style; Excellent breed recognition; High contrast ideal for POD printing
Must fix: Split image into two separate files for chest and back; Clean 164k px of stray background marks; Thicken internal lines for embroidery compatibility; Vectorize to fix upscale requirements
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks; symmetry check
Customer reactions: genz_tiktok_shopper: A bit too basic/millennial-core without edgy text or irony. | millennial_dog_mom: Slightly stark, might prefer a softer or more detailed look. | male_owner_35_55: None. Good masculine, clean aesthetic. | gift_buyer: Safe, universally recognizable, but could look cheap if printed poorly. | art_lover: Lacks artistic soul; looks like standard vector stock art.

## pfl31_geo_poly — REWORK (concept 6.51)
Reads as: geometric line art / low poly
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=8, likeness_judge=5, ip_compliance_reviewer=8, print_technician=5, embroidery_digitizer=7, genz_tiktok_shopper=6, millennial_dog_mom=7, male_owner_35_55=8, gift_buyer=7, art_lover=5
Strengths: Clean, modern geometric style.; Clearly identifiable as a French Bulldog.; Well-suited for embroidery and screen printing (once cleaned up).
Must fix: Clean up the stray marks and specks outside the artwork.; Ensure the design is generated at a higher resolution or use a high-quality upscaler.; Thicken the finer lines to ensure they print cleanly.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: It's a bit too plain. Needs some color or a cooler vibe. | millennial_dog_mom: It's cute, but I prefer designs that look more like my actual dog. | male_owner_35_55: I like the clean, geometric look. It's not too cutesy. | gift_buyer: It's a safe gift for a Frenchie owner, but maybe a bit generic. | art_lover: The geometric style is a bit cliché and lacks originality.

## pnb21_sil_solid — REWORK (concept 6.27)
Reads as: high-contrast vector silhouette with negative space line art
Scores: art_director=7, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=8, print_technician=4, embroidery_digitizer=6, genz_tiktok_shopper=4, millennial_dog_mom=7, male_owner_35_55=7, gift_buyer=7, art_lover=4
Strengths: Clean, high-contrast readability; Accurate general breed silhouette; Easily adaptable to 2-color printing
Must fix: Vectorize to fix the 9.84x upscale requirement; Remove the 203850px of stray marks flagged in the background; Thicken internal negative space lines for embroidery compatibility
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Too basic and 'millennial core'. | millennial_dog_mom: A bit stark in pure black and white. | male_owner_35_55: None, fits a clean, masculine aesthetic well. | gift_buyer: Safe design, but might look cheap if print quality is poor. | art_lover: Looks like generic vector stock art.

## ppro3_sil_stencil — REWORK (concept 6.13)
Reads as: minimalist black and white vector stencil
Scores: art_director=7, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=7, print_technician=6, embroidery_digitizer=7, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=7, gift_buyer=6, art_lover=5
Strengths: High contrast and excellent readability; Easily adaptable for embroidery; Highly scalable style for a 25-breed series
Must fix: Vectorize to fix 10.65x upscale requirement and remove 205887px of stray marks; Separate into two distinct files for left-chest and back printing; Fix eye asymmetry on the full-body graphic
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Too basic, lacks trendy aesthetic or irony | millennial_dog_mom: Black and white is a bit stark | male_owner_35_55: None, fits the bold, non-cutesy preference perfectly | gift_buyer: Needs clear presentation as a premium front/back set | art_lover: Lacks artistic soul, looks like standard clip art

## pfl31_geo_circles — REWORK (concept 6.03)
Reads as: Minimalist geometric intersecting circle line art
Scores: art_director=7, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=5, likeness_judge=5, ip_compliance_reviewer=7, print_technician=6, embroidery_digitizer=7, genz_tiktok_shopper=6, millennial_dog_mom=4, male_owner_35_55=6, gift_buyer=6, art_lover=6
Strengths: Highly scalable and ownable brand style.; Excellent candidate for embroidery and minimalist apparel.; High contrast and clean aesthetic.
Must fix: Clean the 101976px of stray marks flagged in the tech data.; Vectorize the artwork to solve the upscaling requirement.; Redesign the back view to look less like a rabbit and more like a muscular bulldog.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Likes the minimal, tattoo-like aesthetic. | millennial_dog_mom: Too abstract and cold. | male_owner_35_55: Appreciates the clean, non-cutesy design. | gift_buyer: Safe, modern design that fits most tastes. | art_lover: Enjoys the Bauhaus/geometric approach.

## ppro3_geo_circles — REWORK (concept 5.93)
Reads as: Geometric overlapping circle line art, minimalist vector
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=7, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=7, print_technician=7, embroidery_digitizer=6, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=6, gift_buyer=6, art_lover=4
Strengths: Highly scalable and consistent style.; Excellent contrast for DTG printing.; Easily recognizable breed silhouette.
Must fix: Remove white background to eliminate stray marks.; Vectorize or upscale for the large back print.; Simplify inner eye details for the 4-inch embroidery file.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: A bit too 'millennial Etsy' aesthetic. | millennial_dog_mom: A bit stark in just black and white. | male_owner_35_55: None, likes the clean, non-cutesy look. | gift_buyer: Safe design, but might feel a bit impersonal. | art_lover: Feels like automated vector tracing, lacks soul.

## pnb21_geo_circles — REWORK (concept 5.89)
Reads as: Geometric overlapping circle line art
Scores: art_director=7, series_designer=6, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=6, likeness_judge=5, ip_compliance_reviewer=7, print_technician=6, embroidery_digitizer=6, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=7, gift_buyer=6, art_lover=4
Strengths: Highly scalable vector-style aesthetic.; Clear, recognizable French Bulldog silhouette.; Cohesive pairing between the head emblem and full-body print.
Must fix: Remove the solid white background to create a transparent PNG.; Clean the 209972px of stray marks flagged by the tech data.; Simplify the internal overlapping lines for the 4-inch left chest version to ensure print/embroidery clarity.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Looks like a tech startup logo, not a cool streetwear graphic. | millennial_dog_mom: A bit stark and masculine. | male_owner_35_55: None, likes the clean, non-cutesy aesthetic. | gift_buyer: Might be too abstract for an older relative. | art_lover: Feels like a generic vector stock asset, lacks soul.

## ppro3_sil_solid — REWORK (concept 5.87)
Reads as: high-contrast vector silhouette, solid black and white stencil
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=6, print_technician=6, embroidery_digitizer=7, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=7, gift_buyer=6, art_lover=4
Strengths: High contrast and excellent readability at small sizes.; Easily adaptable for both DTG printing and embroidery.; Clear, unmistakable breed identification (French Bulldog).
Must fix: Vectorize the artwork to resolve the 9.6x upscale requirement.; Remove the white background (190,534px of stray marks) to ensure transparency.; Thicken internal detail lines for the cap embroidery file.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Looks like a basic stock vector, not trendy or aesthetic enough. | millennial_dog_mom: A bit stark in just black and white; lacks a cute factor. | male_owner_35_55: None, it's a clean, masculine design suitable for a hoodie. | gift_buyer: Safe but slightly generic gift option. | art_lover: Lacks artistic soul; feels mass-produced and automated.

## pnb21_sil_stencil — REWORK (concept 5.84)
Reads as: high-contrast vector stencil silhouette
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=7, print_technician=6, embroidery_digitizer=7, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=6, gift_buyer=6, art_lover=4
Strengths: Highly scalable across multiple breeds; Excellent contrast for thumbnail visibility; Easily adaptable for embroidery
Must fix: Clean the 202853px of stray marks from the background; Create an inverted white version for navy shirts; Upscale 10x for the back print
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Too basic, lacks irony or trendy aesthetic | millennial_dog_mom: A bit stark and masculine | male_owner_35_55: None, fits the demographic well | gift_buyer: Needs to feel premium to justify as a gift | art_lover: Looks like standard vector stock, lacks artistic soul

## pnb21_geo_poly — REWORK (concept 5.65)
Reads as: Geometric low-poly black and white line art
Scores: art_director=6, series_designer=6, marketplace_merchandiser=5, ai_artifact_inspector=6, breed_expert=6, likeness_judge=5, ip_compliance_reviewer=7, print_technician=6, embroidery_digitizer=6, genz_tiktok_shopper=6, millennial_dog_mom=4, male_owner_35_55=7, gift_buyer=6, art_lover=4
Strengths: Clean, bold lines suitable for multiple print methods.; Easily scalable to a 25-breed series.; Appeals strongly to male demographics.
Must fix: Vectorize to fix the 8.79x upscale requirement.; Clean the 220,400px of stray marks from the background.; Simplify the chest emblem mesh for embroidery viability.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: A bit basic, feels like 2016 hipster art. | millennial_dog_mom: Too harsh and masculine. | male_owner_35_55: None. Fits my preference for non-cutesy, graphic designs. | gift_buyer: Safe design, but feels a bit impersonal. | art_lover: Derivative stock-vector aesthetic.

## ppro3_geo_poly — REWORK (concept 5.63)
Reads as: Geometric low-poly line art
Scores: art_director=6, series_designer=6, marketplace_merchandiser=5, ai_artifact_inspector=6, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=7, print_technician=6, embroidery_digitizer=7, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=7, gift_buyer=6, art_lover=3
Strengths: Highly scalable across multiple breeds.; Excellent for embroidery and high-contrast printing.; Clear, unmistakable breed recognition.
Must fix: Vectorize the image to allow for 9.6x upscaling without quality loss.; Remove the 192k pixels of stray marks/background noise.; Simplify the smallest polygons for the 4-inch left-chest version.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Low-poly trend feels dated (2014 era). | millennial_dog_mom: A bit harsh and masculine. | male_owner_35_55: None. Fits demographic preferences perfectly. | gift_buyer: Might look cheap if print is faded. | art_lover: Looks like standard stock vector art.

## pfl31_sil_stencil — REJECT (concept 5.32)
Reads as: High-contrast black and white vector stencil
Scores: art_director=6, series_designer=6, marketplace_merchandiser=5, ai_artifact_inspector=5, breed_expert=6, likeness_judge=5, ip_compliance_reviewer=7, print_technician=4, embroidery_digitizer=6, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=6, gift_buyer=5, art_lover=3
Strengths: High contrast works well for basic screen printing.; Clear, recognizable breed silhouette.; Appeals to male demographic seeking non-cutesy apparel.
Must fix: Vectorize and upscale to resolve the 10.47x size deficit.; Remove the 174,182 stray background pixels to prevent white boxes on dark shirts.; Fix the melted linework on the full body's front leg.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: A bit basic. Needs more edge or irony. | millennial_dog_mom: Cute, but the eyes are a little intense. | male_owner_35_55: Clean and not overly cutesy. | gift_buyer: Safe bet, but looks like a generic stock image. | art_lover: Lacks artistic soul. Looks like an automated live-trace.
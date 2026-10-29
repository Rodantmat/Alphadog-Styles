# Art Analyzer Report

PASS needs: concept >= 7.5, >= 4/5 customers buy, avg price >= $24 (our tee price), no concept hard-fail, nothing needing regeneration.

| Rank | Design | Verdict | Concept | Pros | Customers | Would buy | Avg $ | Print | Cap | Auto-fixes | Needs regen |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 08_tattoo_flash | **REWORK** | 6.25 | 6.55 | 5.8 | 3/5 | 22.0 | 4 | 4 | 3 | - |
| 2 | 07_pop_art | **REWORK** | 6.23 | 6.51 | 5.8 | 2/5 | 13.0 | 4 | 3 | 4 | detail lost at small sizes |
| 3 | 03_groovy_70s | **REWORK** | 6.11 | 6.45 | 5.6 | 3/5 | 15.0 | 4 | 3 | 4 | - |
| 4 | 06_paper_cut | **REWORK** | 5.9 | 6.36 | 5.2 | 2/5 | 20.6 | 4 | 5 | 5 | - |
| 5 | 02_botanical_crown | **REWORK** | 5.71 | 6.18 | 5.0 | 2/5 | 19.0 | 4 | 3 | 4 | detail lost at small sizes |
| 6 | 04_woodblock | **REWORK** | 5.68 | 6.0 | 5.2 | 2/5 | 24.0 | 4 | 5 | 3 | - |
| 7 | 05_neon_synthwave | **REWORK** | 5.68 | 6.0 | 5.2 | 3/5 | 20.0 | 4 | 3 | 5 | - |
| 8 | 09_folk_embroidery | **REWORK** | 5.68 | 6.27 | 4.8 | 2/5 | 13.0 | 4 | 3 | 2 | - |
| 9 | 14_master_gold_leaf | **REWORK** | 5.57 | 5.82 | 5.2 | 2/5 | 24.0 | 5 | 4 | 2 | - |
| 10 | 12_master_impressionist | **REJECT** | 5.41 | 5.82 | 4.8 | 2/5 | 10.0 | 3 | 4 | 5 | - |
| 11 | 10_ink_watercolor | **REJECT** | 5.36 | 5.73 | 4.8 | 2/5 | 10.0 | 3 | 3 | 5 | - |
| 12 | 01_stained_glass | **REJECT** | 5.02 | 5.37 | 4.5 | 2/5 | 13.0 | 4 | 3 | 3 | - |
| 13 | 11_master_swirl | **REJECT** | 4.85 | 5.15 | 4.4 | 2/5 | 12.2 | 4 | 3 | 1 | - |
| 14 | 13_master_renaissance | **REJECT** | 4.64 | 5.2 | 3.8 | 2/5 | 8.0 | 3 | 2 | 5 | - |

## 08_tattoo_flash — REWORK (concept 6.25)
Reads as: American Traditional Tattoo Flash
Scores: art_director=6, series_designer=7, marketplace_merchandiser=7, ai_artifact_inspector=6, breed_expert=7, likeness_judge=6, ip_compliance_reviewer=7, print_technician=4, embroidery_digitizer=4, genz_tiktok_shopper=6, millennial_dog_mom=7, male_owner_35_55=5, gift_buyer=7, art_lover=4
Strengths: Strong, symmetrical composition ideal for t-shirt graphics.; High contrast and bold outlines ensure the design pops.; Successfully merges a popular pet niche with a trending aesthetic (tattoo flash).
Must fix: Vectorize or AI-upscale the 735px image to support a 9x enlargement for full-front printing.; Halftone all gradients to prevent patchy printing on dark garments.; Erase the 129px of stray marks in the background to prevent random ink spots.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments
Customer reactions: genz_tiktok_shopper: A bit too millennial-core and safe. | millennial_dog_mom: Loves the cute face, but might find the swallows too 'biker' or masculine. | male_owner_35_55: Tattoo style is appealing, but the dog itself is very fluffy and 'cutesy'. | gift_buyer: Safe, attractive design, but might hesitate if it doesn't look exactly like the recipient's specific dog. | art_lover: Digital gradients ruin the illusion of traditional flash.

## 07_pop_art — REWORK (concept 6.23)
Reads as: Comic book pop-art vector with halftone background
Scores: art_director=6, series_designer=6, marketplace_merchandiser=6, ai_artifact_inspector=7, breed_expert=7, likeness_judge=7, ip_compliance_reviewer=8, print_technician=4, embroidery_digitizer=3, genz_tiktok_shopper=5, millennial_dog_mom=8, male_owner_35_55=4, gift_buyer=7, art_lover=5
Strengths: Vibrant, eye-catching color palette; Clear, expressive facial features; Strong, clean linework on the main subject
Must fix: Remove or vectorize halftone background for DTG printing; Eliminate soft feathered edges on the cyan outline; Reduce color count and simplify lines for embroidery
Auto-fixes in post: AI upscale to 4500 px; background removal to transparent PNG; halftone gradients 35-45 LPI for dark garments; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: A bit too 'millennial pop art'. Needs to be more ironic or y2k aesthetic. | millennial_dog_mom: Cyan and yellow are a bit harsh for a cute fluffy dog. | male_owner_35_55: Too colorful and cartoonish. Wouldn't wear a pink and cyan halftone dog. | gift_buyer: Background makes it look a bit cheap/clip-arty. | art_lover: Superficial application of 'pop art' (just halftones behind a standard vector). Lacks true compositional elements.

## 03_groovy_70s — REWORK (concept 6.11)
Reads as: Psychedelic 70s / Lisa Frank hybrid
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=6, ip_compliance_reviewer=8, print_technician=4, embroidery_digitizer=3, genz_tiktok_shopper=7, millennial_dog_mom=7, male_owner_35_55=3, gift_buyer=6, art_lover=5
Strengths: Vibrant, eye-catching color palette.; Good capture of the dog's joyful expression (eyes and tongue).; Symmetrical and balanced composition.
Must fix: Clean the 23px of stray marks outside the main art.; Apply halftones to the heavy gradients to ensure clean DTG printing on darks.; Harden the soft edges to prevent underbase halos.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: Feels a bit 'millennial Lisa Frank' rather than ironic vintage 70s. | millennial_dog_mom: The face paint look is weird; I want the dog to look naturally cute. | male_owner_35_55: Way too colorful and psychedelic. Not my style. | gift_buyer: Might be too specific of a style if they don't love tie-dye/70s. | art_lover: Feels like a standard AI prompt. Lacks true artistic intent.

## 06_paper_cut — REWORK (concept 5.9)
Reads as: Simulated 3D paper cut illustration
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=5, ip_compliance_reviewer=8, print_technician=4, embroidery_digitizer=5, genz_tiktok_shopper=4, millennial_dog_mom=7, male_owner_35_55=4, gift_buyer=6, art_lover=5
Strengths: Cute, engaging expression with good eye contact.; Distinct layered style that stands out from standard photos.; Good use of negative space in the fur texture.
Must fix: Remove the soft drop shadow to prevent DTG underbase halos.; Vectorize the image to eliminate gradients and allow for clean upscaling.; Clean up the 28px of stray marks in the background.
Auto-fixes in post: AI upscale to 4500 px; background removal to transparent PNG; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: A bit too 'craft fair'. Needs more edge or irony. | millennial_dog_mom: Cute, but the cream color might wash out on lighter shirts. | male_owner_35_55: Too cutesy and craft-like for my taste. | gift_buyer: Safe gift, but looks a bit like generic clip art. | art_lover: Paper cut effect is simulated with gradients rather than true flat vector shapes, looking digitally generated.

## 02_botanical_crown — REWORK (concept 5.71)
Reads as: vintage botanical colored pencil illustration
Scores: art_director=6, series_designer=6, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=6, ip_compliance_reviewer=7, print_technician=4, embroidery_digitizer=3, genz_tiktok_shopper=4, millennial_dog_mom=7, male_owner_35_55=3, gift_buyer=6, art_lover=5
Strengths: Appealing, soft aesthetic that targets a specific demographic well.; Good capture of the dog's joyful expression and fluffy texture.
Must fix: Apply a hard clipping mask to remove all soft/semi-transparent edges to prevent underbase halos.; Erase 3986px of stray marks outside the main art.; Upscale >4x for full front printing.
Auto-fixes in post: AI upscale to 4500 px; background removal to transparent PNG; despeckle / remove stray marks; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: Feels a bit 'cottagecore grandma' rather than trendy or ironic. | millennial_dog_mom: Very cute, but delicate style might look faded on standard cotton tees. | male_owner_35_55: Too feminine and cutesy with the flower crown. | gift_buyer: Safe gift, but print quality issues (halos) might cause returns. | art_lover: Looks like a standard AI colored pencil filter.

## 04_woodblock — REWORK (concept 5.68)
Reads as: Faux woodblock or linocut illustration with digital woodgrain texture
Scores: art_director=6, series_designer=6, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=6, likeness_judge=5, ip_compliance_reviewer=7, print_technician=4, embroidery_digitizer=5, genz_tiktok_shopper=5, millennial_dog_mom=6, male_owner_35_55=5, gift_buyer=6, art_lover=4
Strengths: Clean, scalable linework; Strong, recognizable silhouette; Good use of negative space for fur texture
Must fix: Remove internal woodgrain texture to prevent DTG patchiness; Clean 63px stray marks; Upscale 8x for full front printing
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments
Customer reactions: genz_tiktok_shopper: A bit too traditional/craft-fair. | millennial_dog_mom: Woodgrain makes it look a bit rustic for a typical 'dog mom' aesthetic. | male_owner_35_55: Too cutesy and curly. | gift_buyer: Safe, but maybe too specific in style if the recipient doesn't like woodblock art. | art_lover: Faux woodgrain texture over a digital vector drawing looks cheap and inauthentic.

## 05_neon_synthwave — REWORK (concept 5.68)
Reads as: 80s neon synthwave / retrowave portrait
Scores: art_director=6, series_designer=6, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=6, likeness_judge=5, ip_compliance_reviewer=7, print_technician=4, embroidery_digitizer=3, genz_tiktok_shopper=6, millennial_dog_mom=6, male_owner_35_55=4, gift_buyer=6, art_lover=4
Strengths: High contrast and vibrant colors pop well for thumbnails.; Cute, engaging expression captures the essence of the reference dog.; Symmetrical design is easy to center on apparel.
Must fix: Clean up the 42px of stray marks outside the main art.; Apply halftone filters to the heavy gradients to ensure clean DTG printing on dark shirts.; Upscale the image significantly (9x) to meet full-front print resolution requirements.
Auto-fixes in post: AI upscale to 4500 px; background removal to transparent PNG; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: A bit basic. Needs more irony or a stronger aesthetic commitment. | millennial_dog_mom: The neon is a bit harsh. Usually prefers softer aesthetics. | male_owner_35_55: Too pink and cutesy. The circular badge feels like a cheap sticker. | gift_buyer: Fun, but synthwave might be too specific of a style for a general gift. | art_lover: Looks exactly like a generic AI prompt. Lacks human touch or unique composition.

## 09_folk_embroidery — REWORK (concept 5.68)
Reads as: Digital illustration mimicking folk floral embroidery overlaid on realistic fur
Scores: art_director=6, series_designer=7, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=7, likeness_judge=4, ip_compliance_reviewer=8, print_technician=4, embroidery_digitizer=3, genz_tiktok_shopper=4, millennial_dog_mom=7, male_owner_35_55=3, gift_buyer=6, art_lover=4
Strengths: Vibrant, eye-catching color palette; Symmetrical, balanced composition; Clear, engaging eye contact
Must fix: Hard-clip the semi-transparent fur edges to prevent white underbase halos on dark shirts.; Upscale the image by at least 6x using a texture-preserving AI upscaler for full-front printing.; Modify the harsh horizontal cut-off at the bottom to a more natural shape.
Auto-fixes in post: AI upscale to 4500 px; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: Feels a bit too 'grandma's couch' with the traditional embroidery style. Lacks irony or edge. | millennial_dog_mom: Very cute, but the flat bottom edge looks strange on a t-shirt. I wish it had the bandana from the photo. | male_owner_35_55: Too feminine and decorative. Not a style I would wear on a hoodie. | gift_buyer: Pretty, but looks a bit like generic stock art rather than a custom portrait of the specific dog. | art_lover: The 'embroidery' is clearly a fake digital filter over a standard AI dog. Lacks material authenticity.

## 14_master_gold_leaf — REWORK (concept 5.57)
Reads as: Art Nouveau / Klimt-inspired decorative gold leaf medallion
Scores: art_director=6, series_designer=6, marketplace_merchandiser=6, ai_artifact_inspector=6, breed_expert=5, likeness_judge=4, ip_compliance_reviewer=7, print_technician=5, embroidery_digitizer=4, genz_tiktok_shopper=5, millennial_dog_mom=6, male_owner_35_55=4, gift_buyer=6, art_lover=5
Strengths: Strong, symmetrical composition that works well as a central graphic.; High perceived value due to the ornate decorative style.; Clean facial features with good eye contact.
Must fix: Erase 201px of stray marks outside the circular medallion.; Upscale >4x for full front printing.; Adjust coat color to pure white to match the reference likeness.
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks
Customer reactions: genz_tiktok_shopper: Too traditional/grandma-core. | millennial_dog_mom: Beautiful, but coat color doesn't match her pure white dog. | male_owner_35_55: Too ornate and decorative. | gift_buyer: Looks expensive, but style is very specific if recipient's taste is unknown. | art_lover: AI interpretation of gold leaf is flat.

## 12_master_impressionist — REJECT (concept 5.41)
Reads as: Digital soft-brush pet portrait (faux-impressionist)
Scores: art_director=6, series_designer=5, marketplace_merchandiser=5, ai_artifact_inspector=6, breed_expert=7, likeness_judge=6, ip_compliance_reviewer=7, print_technician=3, embroidery_digitizer=4, genz_tiktok_shopper=4, millennial_dog_mom=7, male_owner_35_55=3, gift_buyer=6, art_lover=4
Strengths: Cute, appealing expression.; Good general likeness to the reference photo.; Strong appeal to the core dog-mom demographic.
Must fix: Hard-mask the soft edges to prevent DTG underbase halos.; Upscale resolution >4x for apparel printing.; Clean 160px of stray marks.
Auto-fixes in post: AI upscale to 4500 px; background removal to transparent PNG; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: Too 'Facebook mom'. Lacks irony or streetwear appeal. | millennial_dog_mom: A bit plain without a background, but very sweet. | male_owner_35_55: Too cutesy and soft. Looks like a greeting card. | gift_buyer: Safe and cute, but might look cheap if print quality is blurry. | art_lover: Lacks actual impasto texture; just looks like a digital smudge brush.

## 10_ink_watercolor — REJECT (concept 5.36)
Reads as: digital ink and watercolor wash
Scores: art_director=6, series_designer=6, marketplace_merchandiser=5, ai_artifact_inspector=6, breed_expert=6, likeness_judge=4, ip_compliance_reviewer=7, print_technician=3, embroidery_digitizer=3, genz_tiktok_shopper=4, millennial_dog_mom=7, male_owner_35_55=3, gift_buyer=6, art_lover=4
Strengths: Pleasant, harmonious pastel color palette; Strong eye contact and expressive face; Clean ink outlines on the facial features
Must fix: Apply a hard clipping mask to remove soft edges for DTG printing; Erase the 4204px of stray marks; Add the red and white checkered bandana to match the likeness; Create a simplified 4-color vector version for embroidery
Auto-fixes in post: AI upscale to 4500 px; background removal to transparent PNG; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: Aesthetic is too 'millennial mom' | millennial_dog_mom: A bit generic, looks like a stock image rather than my specific dog | male_owner_35_55: Too colorful and cutesy for a standard hoodie or cap | gift_buyer: Safe and cute, but lacks a personalized touch like a name drop | art_lover: Looks exactly like a standard Midjourney v5 prompt

## 01_stained_glass — REJECT (concept 5.02)
Reads as: Digital painting with a faux stained-glass border
Scores: art_director=5, series_designer=5, marketplace_merchandiser=5.5, ai_artifact_inspector=6, breed_expert=5.5, likeness_judge=4, ip_compliance_reviewer=7, print_technician=4, embroidery_digitizer=3, genz_tiktok_shopper=4, millennial_dog_mom=6.5, male_owner_35_55=3, gift_buyer=5.5, art_lover=3.5
Strengths: Cute, expressive face; Good symmetry for apparel placement; Clear thick outer outline for easy masking
Must fix: Clean 92px stray marks; Upscale 6.67x for front print; Change coat color to white to match reference; Halftone gradients for dark DTG
Auto-fixes in post: AI upscale to 4500 px; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments
Customer reactions: genz_tiktok_shopper: Looks like a millennial mom shirt. | millennial_dog_mom: Cute, but the stained glass border is a bit weird. | male_owner_35_55: Too cutesy and colorful. | gift_buyer: Safe gift, but the color doesn't match the reference dog. | art_lover: Fails as 'stained glass' art.

## 11_master_swirl — REJECT (concept 4.85)
Reads as: Van Gogh Starry Night pastiche / Impasto oil painting
Scores: art_director=5, series_designer=5, marketplace_merchandiser=5, ai_artifact_inspector=6, breed_expert=6, likeness_judge=5, ip_compliance_reviewer=4, print_technician=4, embroidery_digitizer=3, genz_tiktok_shopper=4, millennial_dog_mom=6, male_owner_35_55=3, gift_buyer=6, art_lover=3
Strengths: Good execution of impasto brushstroke texture on the fur.; Clear, engaging eye contact from the subject.; Strong contrast between the white dog and dark background.
Must fix: Generate at a much higher resolution to avoid 7.8x upscale artifacting.; Remove the hard circular crop and replace with a distressed/faded edge for better DTG printing.; Remove literal Starry Night elements (cypress tree, village) to avoid cliché and IP parody fatigue.
Auto-fixes in post: AI upscale to 4500 px
Customer reactions: genz_tiktok_shopper: Gives 'boomer Facebook ad' vibes. | millennial_dog_mom: Cute, but a bit generic. | male_owner_35_55: Too artsy and cutesy. | gift_buyer: Safe gift, but looks like something from a mall kiosk. | art_lover: Derivative pastiche of Van Gogh.

## 13_master_renaissance — REJECT (concept 4.64)
Reads as: soft digital pastel with heavy vignette
Scores: art_director=4, series_designer=4, marketplace_merchandiser=4, ai_artifact_inspector=6, breed_expert=7, likeness_judge=6, ip_compliance_reviewer=9, print_technician=3, embroidery_digitizer=2, genz_tiktok_shopper=3, millennial_dog_mom=6, male_owner_35_55=3, gift_buyer=5, art_lover=2
Strengths: Captures the happy expression and tongue-out pose well.; Good eye clarity and general facial proportions.
Must fix: Remove the black vignette background completely to prevent DTG underbase halos.; Upscale image by at least 6x for full front printing.; Clean 239px of stray marks outside the main subject.
Auto-fixes in post: AI upscale to 4500 px; background removal to transparent PNG; despeckle / remove stray marks; halftone gradients 35-45 LPI for dark garments; hard alpha threshold (no semi-transparent pixels)
Customer reactions: genz_tiktok_shopper: Looks like a boomer Facebook meme shirt. | millennial_dog_mom: Cute face, but the black background shadow is depressing. | male_owner_35_55: Too soft and cutesy. | gift_buyer: Dark halo might look bad on a shirt. | art_lover: Fails 'master renaissance' prompt completely.
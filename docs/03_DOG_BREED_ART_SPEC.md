# Niche 1 — Dog Breed Logo Collection (art spec v1)

Status: research done 2026-10-28 · awaiting owner pick of style test · no images generated yet

## Breeds (AKC 2025 ranking, published 2026)
1 French Bulldog · 2 Labrador Retriever · 3 Golden Retriever · 4 German Shepherd · 5 Dachshund · 6 Poodle · 7 Beagle · 8 Rottweiler · 9 German Shorthaired Pointer · 10 Bulldog · 11 Cane Corso · 12 Cavalier King Charles Spaniel · 13 Yorkshire Terrier · 14 Australian Shepherd · 15 Doberman Pinscher · 16 Pembroke Welsh Corgi · 17 Miniature Schnauzer · 18 Boxer · 19 Pomeranian · 20 Bernese Mountain Dog · 21 Shih Tzu · 22 Great Dane · 23 Boston Terrier · 24 Chihuahua · 25 Havanese
Reserve: Border Collie (rising), Siberian Husky, Shetland Sheepdog.
Candidates outside AKC (popular with buyers, not ranked by AKC): Goldendoodle/Labradoodle, Pit Bull.

## Research verdict
- Breed-specific beats generic ("Golden Retriever Mom" > "Dog Mom"); generic dog-mom text is saturated.
- Breed-specific apparel demand reported +41% (2022–2025) (third-party figure cited by Printify).
- Strongest documented apparel style: retro/vintage 70s–80s; minimalist line art also a consistent top seller; pet art trending toward abstract, minimalist, pop-art.
- Breed + hook (retro badge, "club", hobby) is recommended over a plain portrait.
- Risk: plain breed line art is crowded → need a recognizable, consistent brand system across all 25.

## Logo system (one design → all products)
Each breed gets 2 masters:
1. **Embroidery master** (caps, small chest on hoodies/shirts): flat, ≤6 thread colors (Printify 15-color palette), no gradients/photos, lines ≥0.05 in, text ≥0.3 in uppercase, no tiny gaps. Cap front max 4 × 2.25 in.
2. **Print master** (big back, big front, tank tops, mugs, totes): full color, transparent PNG, high-res (≥4500 px wide).
Placements: small left-chest (≈3–4 in) + large back; cap front embroidered; tank top front/back.

## Variants
Coat colors where buyers care (e.g., Lab black/yellow/chocolate, Frenchie fawn/brindle/cream, Dachshund smooth/long/wire). Counted as variants of one design, not new designs.

## Style test (before generating all 25)
Generate ONE breed (Golden Retriever) in 5 styles, score with critic panel, owner picks 1–2:
A. Retro badge/club emblem (e.g., "Golden Retriever Club · Est.") — strongest trend, embroidery-friendly
B. Minimal line art (single bold line + breed name) — top seller, crowded
C. Mid-century flat geometric color blocks — colored, abstract-leaning, embroidery-friendly
D. Pop-art halftone — colored, print-only
E. Abstract watercolor splash — colored, print-only
Then roll the winning style(s) across all 25 breeds (+ color variants).

## Image generation options (free)
- Cloudflare Workers AI FLUX (free 10k Neurons/day, hard-capped) — needs owner's Cloudflare account/token.
- Gemini via existing bridge (check if an image model is reachable).
- Vectorization of embroidery masters (potrace-style, free) for clean edges.

## Brand (owner, 2026-10-28)
- Brand name: AlphaDog. Logo (brand/alphadog_logo.png): white doodle silhouette, halo + wings, inside a circle, dark background.
- Logo goes on the INSIDE printed neck label only (Printify supports printed inner labels; inner label removes the manufacturer tag; size/fabric/origin/care still printed).
- Note: the store name on Etsy/eBay/TikTok Shop is public → run USPTO class 25 check on "AlphaDog"/"Alpha Dog" before opening stores.
- Style F (new): "AlphaDog house style" — solid silhouette inside circle badge, 2–3 colors, matches the logo, embroidery-friendly. Halo/wings = memorial sub-line only (pet memorial is a real category), not default.

## Quality + no-loss pricing (owner rule: thin profit OK, never lose money)
Blanks (sample before launch, compare 2 providers for caps):
- Tee: Bella+Canvas 3001 (claimed 100+ washes; ~$10.98 base free plan) — Gildan Softstyle 64000 as cheaper alternative.
- Hoodie: Gildan 18500 (~$23.20 base). Caps: dad cap embroidered (~$11.57–12.50). Tank: price-check Bella+Canvas tank.
Break-even incl. US shipping (Etsy fees 6.5% + 3% + $0.25 + $0.20 listing; Offsite Ads + Etsy Ads OFF):
| Product | Cost + ship | Etsy break-even | Launch price | Est. profit/sale |
|---|---|---|---|---|
| Tee | ~$15.97 | ~$18.15 | $23.99 | ~$5.30 |
| Hoodie | ~$30.20 | ~$33.90 | $39.99 | ~$5.50 |
| Cap | ~$16.50 | ~$18.70 | $24.99 | ~$5.70 |
Pipeline enforces a price floor per channel (eBay ~13–14% fees, TikTok ~6–8%).

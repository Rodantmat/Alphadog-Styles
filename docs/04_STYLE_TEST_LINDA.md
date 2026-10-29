# Style Test — Pilot: Linda (Bichon-look poodle)

Status: prompts ready · blocked on image generator route · 2026-10-28

## Owner direction
- Head only, front-facing (perspective like the breed-icon reference), NO wording.
- Rich, elaborate, fun, exciting — a signature art theme that can be replicated across all breeds.
- Pilot breed: poodle that looks like a Bichon, based on Linda (owner's late dog).
- Test 10 styles → pick 1–3 signature lines → 25 breeds each (up to 75 designs).
- The breed-icon image owner shared is a stock-site watermarked image: perspective reference only, never traced or copied.

## Reference
- linda/linda_head_ref.jpg (2014 groomer photo): frontal, round cream puff head, long fluffy ears, dark round eyes, black nose, pink tongue out.
- Locked features for every style: round cloud-shaped head, long drop ears, big dark eyes, button nose, tongue out (signature "happy" expression for the whole line).

## Shared prompt base (all styles)
"Front-facing head portrait of a fluffy cream Bichon-style poodle with a round cloud-shaped head, long fluffy drop ears, big dark round eyes, black button nose, happy open mouth with pink tongue out. Head and ears only, centered, symmetrical, isolated on a transparent/plain background, t-shirt graphic, no text, no letters, no watermark, no signature."

## 10 styles (no artist names → avoids derivative/IP issues)
1. **Stained-glass mosaic** — jewel-tone glass pieces, thick black leading lines, light glowing through.
2. **Botanical crown** — vintage engraving head with a crown/mane of wildflowers and leaves woven into the fur.
3. **Groovy 70s psychedelic** — fur made of flowing melting rainbow bands, wavy outlines, sunburst behind.
4. **Japanese woodblock** — woodblock-print textures, curling wave and cloud motifs forming the fur.
5. **Neon synthwave** — glowing neon line art on dark, magenta/cyan, retro grid sun behind the head.
6. **Layered paper-cut** — 5–6 layered paper sheets with soft depth shadows, pastel palette.
7. **Pop-art comic** — bold black outlines, bright flat colors, halftone dot shading.
8. **Tattoo flash (American traditional)** — bold outline, limited palette, roses and swallows framing (no banner text).
9. **Folk embroidery** — fur filled with stitched floral/geometric embroidery patterns, thread texture.
10. **Ink + watercolor splash** — loose ink linework with vibrant watercolor splashes and drips.
Bonus candidates: crystal low-poly, graffiti street art, cosmic galaxy fur, mosaic tiles.

## Production notes
- Rich styles = print versions (fronts/backs, tanks, mugs, totes). Caps need a simplified ≤6-thread embroidery version of the same head per line.
- Scoring: critic panel (personas) + owner pick. Keep the 1–3 most distinctive, consistent and replicable.

## Image generator route (pending owner)
Sandbox can't reach image APIs; the bridge's Gemini tool returns text only.
- A. GitHub Action in the new repo calling Gemini image model with Linda photo as reference (image-to-image = strongest likeness). Needs a Gemini API key as repo secret. Cost ≈ a few cents per image (paid tier; confirm free-tier availability).
- B. GitHub Action calling Cloudflare Workers AI FLUX (free 10k Neurons/day, hard cap). Text-only prompts → weaker likeness to Linda.
- C. Owner runs the prompts in any image app he already uses and drops results in a folder.

## Reference update (owner: front face, most recent photos)
- PRIMARY: linda/ref_2025-08_front_smile.jpg (Aug 2, 2025) — frontal, groomed round head, long ears, tongue out. Cropped to the dog only (strangers in background removed).
- SECONDARY: linda/ref_2025-01_front_fluffy.jpg (Jan 18, 2025) — frontal, ungroomed curly "cloud" fur, good for texture-heavy styles.
- Older 2014 groomer shot kept as backup.

## Old-masters line (owner idea, 2026-10-28)
Head-only Linda/breeds painted in public-domain master styles: impressionist (Monet-like), swirling post-impressionist (Van Gogh-like), Renaissance sfumato (Da Vinci-like), sculpted marble/fresco (Michelangelo-like). Also candidates: Klimt-like gold leaf, Hokusai-like woodblock, Mucha-like art nouveau, Rembrandt-like chiaroscuro.
- Legal: styles aren't protected and these artists' works are public domain; still never copy a specific painting composition, and keep artist names OUT of listing titles/tags (museum/estate trademarks exist in some markets) → use descriptive words ("impressionist oil painting dog").
- Market: "pet as famous painting" portraits are an established niche (competition), but head-only icon set across 25 breeds is a differentiated angle.

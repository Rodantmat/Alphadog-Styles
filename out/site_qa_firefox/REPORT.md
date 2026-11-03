# alphadogstyles.com: storefront QA report (2026-11-03)

- **Runner:** GitHub Actions `site-qa.yml`. Playwright with Chromium, split into 5 parallel shards, about 8 minutes per run.
- **Suite:** `scripts/site_qa/`.
- **First full run:** Actions run 41627285683, commit `ffda132`. It made 22,559 passing checks and 13 failing ones.
- **Machine results:** `SUMMARY.txt`, `results.json`, `<shard>.json`.
- **Screenshots and contact sheets:** `shots/`, `sheets/` and `manual/`.

**Safety.** No real order, email, login code, subscription, contact message or custom request was sent. In the browser, every `/api/*` call except `GET /api/health` was intercepted and given a mock answer. The order payloads were checked against a Python copy of the worker's `validItem()` rules.

## Coverage

| Area | Checks |
|---|---|
| Routes and pages: 24 routes × en/es/pt (72 renders), 404 handling | 510 |
| Links: 470 found and followed, 20 header/footer links clicked | 961 |
| Forms with mocked API: newsletter, contact, login, magic link, admin token prompt | 34 |
| Home page widgets | 16 |
| Shop: 12 filter combinations, 6 bad-link filters, search by all breed names (en/es/pt) and 8 edge cases, all 198 cards checked and clicked through to the designer | 2,513 |
| Designer: every product × color × size × front option × back option (3,042 states), checking preview, art, price and print area | 14,610 |
| Designer rules: dark colors blocked, options per product, quantity | 145 |
| Every breed × theme × style on front and back (396 combinations) | 794 |
| Other designer checks: garment switching, link parameters, save, race test | 22 |
| Cart and checkout: 44 lines, totals, shipping, quantity, reload, order payloads, Stripe redirect | 423 |
| Custom design and saved designs (mocked) | 23 |
| Mobile (iPhone 13) | 35 |
| Art assets: 396 SVGs, 67 garment photos, lookbook, logo | 2,435 |

## Defects found, and the fix applied

| # | Severity | Defect | Fix (commit `b923470`) |
|---|---|---|---|
| M1 | Medium | On a slow connection the preview could show a different design than the one selected (async render race in `pv()`). | `pv()` now has a sequence guard, so an older render can no longer overwrite a newer one. |
| M2 | Medium | "Complete the look" in the cart showed 6 broken "custom" cards when the first cart line was a custom design. | The section now uses the first real breed in the cart, and is hidden when there isn't one. |
| M3 | Medium | The cart page went blank after adding a design opened with an unknown theme or style in the link (`#/design?theme=bogus`). | The designer validates the theme and style from the link. `themeName()` and `styleName()` fall back safely instead of crashing. |
| M4 | Medium | The cart accepted unlimited lines, but the order API rejects more than 30 with a misleading message. | Adding is capped at 30 lines, with a clear message in all 3 languages. |
| M5 | Medium | Art: the Cavalier King Charles Spaniel Continuous Line · Heart head carried a stray squiggle. It was the full-body dog's tail, assigned to the wrong side when the art was split. | Re-vectorized from FINALS with the new `ASSIGN=near` option in `scripts/vectorize.py`. The tail is back on the full-body art, and the head is clean. A scan of all 198 FINALS found no other misassigned part. The Printify art swap is queued: `printify-artfix`, `breed=cavalier_king_charles_spaniel`, `des=line_heart`. |
| L1 | Low | The cart and checkout labeled the back "Full body" option as "Big body". | `designLabel()` now looks up the back options for the back side. |
| L2 | Low | Checkout State defaulted to "AL". | Added a required "State" placeholder with no value. |
| L3 | Low | Switching garments turned a body placement into "Head emblem" and didn't restore it on switching back. | The designer now keeps the body/head intent across garments and restores it. |
| L4 | Low | The designer accepted an unknown theme or style from the link. | Fixed together with M3. |
| L5 | Low | `#/shop?theme=bogus` showed zero designs. | Unknown filters are now ignored. |
| L6 | Low | "Full body" was untranslated in Spanish and Portuguese. | Added es/pt, plus the new "State" and cart-full strings. |
| L7 | Low | The cart "Remove" button was a 15 px tall tap target. | Raised to a 32 px minimum height. |
| I1 | Info | Language switching briefly replaced card mockups with digits (`data-i` collision). | The card attribute is renamed to `data-n`. |
| I2 | Info | Cart lines can't be edited. | No change; this was by design. |
| I3 | Info | Social logins are switched off. | No change; this is a configuration choice. |

## Not tested, and why

- Real payment, the Stripe webhook, Printify fulfilment, emails, real login codes, OAuth and real custom-request submission. All were mocked by design.
- The admin page beyond its token prompt.
- Safari and Firefox. Tests ran in Chromium only, with iPhone simulated inside Chromium.
- The full breed × style × product × option cross product (about 600,000 states). It is covered in parts instead: every product option state (3,042), every breed design on both sides (396), all 198 card click-throughs and 44 mixed cart lines.
- Whether each drawing is a good likeness of its breed. This was judged by eye on the contact sheets.

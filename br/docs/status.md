# Status - Brazil (pt-BR) site, 2026-11-07 (Pacific)
Branch `br-site` (repo rodantmat/alphadog-styles). Everything is under `br/`; no file in `store/` or any live workflow was changed on the branch.

## Done (tested with mocks, nothing deployed, nothing sent)
- Discovery + architecture + owner checklist: `plan.md` (also `br/docs/`).
- Geo/region routing module (country BR -> pt-BR at same URL, `/br/` canonical, cookie override, bots never vary, hreflang headers+tags): `br/worker/br.js` (`geoGate`, `decideRegion`).
- pt-BR storefront SPA: home, shop+filters, product (side/colour/size), cart, checkout (CPF/CNPJ, CEP+ViaCEP, live Gubo freight), order tracking, account/login, custom dog design intake + status + purchase, 8 info pages, footer/mailboxes.
- Gubo catalog builder + read-only pull + daily sync workflow; catalog currently = the 1 real product from the 2026-11-07 probe.
- Order pipeline: quote -> order (BRL centavos, CPF check, server-side price) -> Mercado Pago preference (placeholder) -> markPaid -> Gubo create (idempotent) -> cost guard -> pay from wallet -> signed Gubo webhooks (dedupe, versao) -> tracking/delivered emails (pt-BR, from pedidos@) + 10-min sweep for lost webhooks/low wallet.
- Mailboxes suporte@/customiza@/pedidos@: inbound mapping, outbound From, mail_bridge + `/api/internal/send` mapping, Email Routing script, pt-BR assistant prompt.
- Patch `br/patches/br-integration.patch` applies cleanly to current main files; the PATCHED real `index.js` passes the integration test. Also restricts store-deploy's push trigger to `main`.
- Tests: worker (ok), patched-worker integration (ok), catalog (ok), jsdom smoke of all routes (ok, run manually: `node br/tests/smoke_site.mjs` needs `npm i jsdom`).

## Not done / unverified
- **Real catalog (16 breeds x 12 designs) not loaded**: not in the repo, no live key here. Run `br-catalog-sync` after merge. Owner SKU spelling (LN/GE/CL/OC/CO) vs repo dump (LINE/CLASSIC) handled by the parser but untested on real data.
- Not run against real Gubo or Mercado Pago (mocked). MP field names/signature manifest are from memory -> TODO-verify in MP test mode. Gubo base URL `api.gubo.com.br/v1` is from the probe, docs say otherwise.
- Not deployed; BR checkout is closed until `MP_ACCESS_TOKEN` exists (503 by design).
- No scheduled task created (prompt drafted); no mailbox created; no DNS/Email Routing change; no secrets set; no email sent; no browser/Gubo UI/Printify UI use.
- Content that is policy, not fact, and needs the owner: returns (7-day), privacy/terms text, size table (Gubo's "Tabela de medidas" not captured -> page has no numbers), seller identity in footer, XG/XGG surcharge, free-shipping rule, BRL custom fee.
- Product images hotlink Gubo `imagem_url` (mockups on plain photos); our own art mockups for BR not generated. Brand label and NF-e "Preço de revenda" are Studio-side settings, not verifiable here.
- SEO: hash routes not indexable (as in the US site); prerendered `/br/` product pages = phase 2. Admin panel shows BR orders but formats money as USD.
- Social (tomorrow), payments connection (tomorrow).


## Update 2026-11-08 (branch br-site-2): all Gubo models + proportional prices
- Prices decided by method, not conversion: see `br/docs/pricing.md` (US retail/cost multiple x BR cost, owner de/por ratio, ,90 endings, 15% floor, ecobag/pet market cap). Padrao R$109,90 (de 139,90), Oversized 147,90, Tech Modal 140,90, Babylook 109,90, Cropped 80,90, Infantil 74,90, Moletom capuz 2/3 cabos 217,90/274,90, sem capuz 177,90, Ecobag 59,90, Pet 59,90. XG/XGG surcharge per model.
- SKU: Padrao unchanged `{BREED}-{LN|GE}-{CL|OC|CO}-{F|B}-{DK|LT}-{COLOR}-{SIZE}`; other models add a 6th product-code segment: OV TM BL CR KD H2 H3 HS EC PT (e.g. `LHA-LN-CL-F-LT-BL-BRAN-M`). Worker/site resolve the longest product code; a model with no configured price is refused.
- New breeds in `config/br_breeds.json`: LHA Lhasa Apso, MPN Pinscher Miniatura, VLT Vira-lata (SRD). The 16 approved breeds' Gubo codes are not in the repo (list empty, TODO): the storefront does not need them (reads breeds from the Gubo dump).
- Product page has a "Modelo" selector, crossed-out "de" price, XG/XGG surcharge; cart/checkout price per model. Checkout still closed (no MP token).
- Planned matrix: 19 breeds x 12 designs x 2 tones x 11 models = 5.016 Gubo products to exist in Studio (456 per model). `python3 -I br/scripts/br_matrix.py --csv out.csv` lists them.
- Tests: `test_pricing.py`, `test_catalog.py`, `run_worker_tests.sh`, `run_integration.sh`, `CATALOG=<multi.json> node smoke_site.mjs` all pass. US store files untouched.

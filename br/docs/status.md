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

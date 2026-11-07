# Alternatives to Dimona: Brazil POD / dropship apparel with better automation

Research date: 2026-11-07. Labels: VERIFIED = read on the cited URL on that date (raw copies of most pages are in `docs/brazil_data/alt/`, fetched by the GitHub runner probe tasks `alt`..`alt4` in `scripts/brazil/probe.py`). UNVERIFIED = not read from a primary source, or only claimed by a third party, or blocked. No logins, no accounts, no ToS violations. Prices are BRL unless stated.

## 0. Bottom line

1. **Nothing verified beats Dimona on the one thing we need: an API that creates orders for a marketplace seller.** Dimona already has more than SUMMARY.md said (see section 1). The real blocker with Dimona is not the API but the *label* and *Mercado Livre policy*, and that blocker is equally unsolved at every alternative we could read.
2. **Montink is not an alternative.** Its home page says it runs on Dimona infrastructure (VERIFIED). Same factory, no public API found, no Mercado Livre integration in its integrations list.
3. **Best API/webhook engineering found: Reserva INK** (HMAC-signed webhooks, 43 events, self-service token). But its public API has **no create-order endpoint**, costs about 1.4-1.8x Dimona per tee, the API needs the R$799/month plan, and it only connects to Shopify, Nuvemshop, CartPanda, Hotmart (not Mercado Livre). Good for reading/reconciling a store, not for pushing ML orders in.
4. **Best "real API, create order, webhooks, local-ish production": Printful v2** (draft/confirm orders, webhooks, shipments, self-service token, a Brazil fulfillment center, BRL). Unknowns: apparel really printed in Brazil, BRL price, NF, ML label handling.
5. **The decisive unknown is on the Mercado Livre side, not the supplier side**: which Mercado Envios mode our listings use, and whether Brazil allows seller-handled ("custom"/own) shipping so the supplier's own carrier label can be used. Settle that first (section 6).
6. **MCP vs worker**: a Cloudflare Worker (plus Claude scheduled task as safety net) is the right engine. An MCP adds interactive/ad-hoc control and docs lookup, but cannot receive webhooks. The *official* Mercado Livre MCP is a documentation-search server only (VERIFIED). Details in section 5.

## 1. Correction to SUMMARY.md about Dimona (VERIFIED, 2026-11-07)

Source: saved Postman collection `docs/brazil_data/dimona/postman_ateAuth_true_versionTag_latest.json` (publishedId 2sB2qdgLJQ, publishDate 2025-05-27).

- Dimona **does have webhooks**. Folder "Webhook": "Send a POST Request in every Status Update". URL is set in the account (camisadimona.com.br/loja/conta/avancado). Body: `{"api_key":"...","dimona_id":"462-424-866","status_id":13,"name":"Faturado","seller_id":"...","tracking_url":"..."}`. There is also a per-order `webhook_url` field on Create Order.
- Not signed (no HMAC); the `api_key` in the body is the only shared secret. Retry policy: not documented (UNVERIFIED).
- The API also has `POST /order/{id}/nfe` and `POST /order/{id}/shippingLabel` / `shippingDocuments` (needs an email to api@dimona.com.br first, per the collection). The help-center articles say Dimona refuses third-party labels and Mercado Livre/Shopee/Amazon. These two statements conflict. **Ask Dimona directly** (question list in section 6); it costs nothing and could make every alternative moot.
- Dimona API lacks: signed webhooks, documented retries, sandbox (UNVERIFIED), order-level DC-e/ML awareness.

## 2. Mercado Livre facts that constrain ANY supplier (VERIFIED, 2026-11-07)

| Topic | Fact | Source |
|---|---|---|
| Notifications | Callback URL per app; topics include `orders_v2`, `shipments`, `invoices` (Brazil Full only), `claims`, `items`, `messages`. POST body is only a signal (`resource`, `topic`, `user_id`, `attempts`); you GET the resource. **Must return HTTP 200 within 500 ms** or the topic can be deactivated. Retries for 1 hour; `GET /missed_feeds?app_id=` lists missed ones. Allowlist of 8 ML source IPs. | developers.mercadolivre.com.br/en_us/products-receive-notifications |
| Label | `GET https://api.mercadolibre.com/shipment_labels?shipment_ids=ID&response_type=pdf` (or `zpl2`). Ready when shipment is `ready_to_ship`. The seller must print the prepaid label. | developers.mercadolivre.com.br/en_us/mercadoenvios-mode-2 |
| Label unlock needs fiscal doc | For `drop_off`, `xd_drop_off`, `cross_docking`, `xd_same_day` the shipment sits in substatus `invoice_pending` until the seller imports an **NF-e (model 55)** via `POST /shipments/{id}/invoice_data/?siteId=MLB` (PJ contributors only). Homologation NF-e rejected. After the label is printed the NF cannot be changed. | .../pt_br/importar-nota-fiscal (updated 2026-08-03) |
| CPF sellers | PF and non-contributor PJ **do not use NF-e import**; they need a **DC-e** (Declaracao de Conteudo Eletronica), issued in Seller Central or via ML's DC-e API, within 3 days of the sale or the order is auto-cancelled. DC-e cannot be uploaded via API. | same page; DC-e API page `.../pt_br/integracao-dce` (title seen in search, body NOT read: UNVERIFIED) |
| Attach NF to buyer | `POST /packs/{pack_id}/fiscal_documents` (XML, optional PDF). Not allowed in MLB for drop_off, cross_docking, xd_drop_off, fulfillment. Does not unlock the label. | .../pt_br/anexar-nota-fiscal (updated 2026-04-07) |
| Seller-handled shipping | "Envios Personalizados": `shipping.mode = custom` (seller uploads a cost table and handles all logistics) or `not_specified`. The doc example is MLA/ARS. **Whether Brazil allows it for our category/account: UNVERIFIED.** | .../pt_br/envios-personalizados (updated 2024-12-10) |
| Dropship via third party | Blogs say: seller generates the label and sends it to the supplier who sticks it on the box and posts it. That is exactly what Dimona says it will not do. | nuvemshop.com.br/blog/dropshipping-mercado-livre (third-party, UNVERIFIED as ML policy) |
| ML search/seller listing API | Mostly 403 from our runner without an app token (SUMMARY.md). No scraping (ML T&C). | SUMMARY.md |

Consequence: for a **CPF seller on Mercado Envios**, the automatable path is: webhook -> fetch order+shipment -> create DC-e (ML API) -> pull ML label PDF -> hand the label to the supplier. Step 4 is the part nobody has confirmed. For a **CNPJ/MEI seller** the NF-e path (supplier or Bling issues NF-e, we import XML) is available. Montink's own docs say NF at sale value needs Bling + CNPJ + digital certificate.

## 3. Candidate-by-candidate

Fields: production | API/docs/auth/webhooks | marketplaces | label | NF | tee/hoodie price | min order | lead time | returns | reviews | CPF/CNPJ.

### 3.1 Montink (Belo Horizonte, since 2014; CNPJ 22.733.912/0001-05)
- Production: **"A Montink usa a infraestrutura da Dimona"** (VERIFIED, montink.com.br home, 2026-11-07, `alt/montink_home.txt`). The Nuvemshop listing says shipping is calculated from a depot in Duque de Caxias/RJ (VERIFIED, nuvemshop.com.br/loja-aplicativos-nuvem/montink). The ecommercenapratica line "backed by Dimona" is therefore plausible and consistent.
- API/webhooks: **none found.** Nuvemshop listing says no Montink API. Probes of /api, /integracoes, developers.montink.com.br: pages without API content or DNS fail (`alt/montink_api.txt` is the generic site, `montink_dev.txt` NAME_NOT_RESOLVED). UNVERIFIED that no private API exists.
- Integrations list (VERIFIED, sou.montink.com/integracoes-montink): Bling, Hotmart, Monetizze, Eduzz, Facebook, Sak, Lily, Jivochat, Shopify, Nuvemshop, Yampi, iSet, Monettize, Sympla. **No Mercado Livre, Shopee, Amazon, TikTok Shop in that list.** Nuvemshop listing claims products "can also be listed on Mercado Livre, TikTok Shop, Hotmart, Google Shopping, Facebook catalog" - that is store-feed language; the order/label flow is UNVERIFIED.
- Label/NF: Montink generates the label; NF issued by Montink at cost price by default; sale-value NF only via Bling with CNPJ + IE + certificate. Production starts when the label is printed; avg ~4 business days; Correios/carriers (VERIFIED, Nuvemshop listing).
- Price: plans R$149/mo, R$126.60/mo annual, Escalada R$199/mo annual, lifetime R$8,997; 7-day trial; plan prices are for the platform (store), per-unit cost is paid per sale. Catalog prices on montink.com.br/dropshipping (2026-11-07): Camiseta Quality 48.20, Classic Infantil 38.30, Baby Look Prime 58.54, Oversized 95.94, Moletom Canguru 160.95, Moletom Fechado 110.35, Moletom Zipper 143.35. Whether these are cost-to-seller or retail price: UNVERIFIED. They are higher than the Dropsimples 2024 PDF (hoodie 127.00).
- Reviews: Nuvemshop app 4.5/5 from 14 reviews (VERIFIED). Reclame Aqui / Trustpilot blocked (403/404 from runner): UNVERIFIED. siteconfiavel.com.br found no Reclame Aqui record under the montink.com domain (weak signal).
- CPF/CNPJ: not stated on pages read: UNVERIFIED.
- Verdict: same factory as Dimona, no API, no ML. **No gain.**

### 3.2 Reserva INK (Arezzo Industrial e Comercio S.A., CNPJ 16.590.234/0064-50)
- Production: own factory chain of the Reserva fashion group, Kornit Atlas DTG, distribution center in Rio de Janeiro, carriers integrated (Loggi mentioned) (VERIFIED, reserva.ink home + help center). White-label tags and recycled plastic bags (VERIFIED).
- **API (VERIFIED)**: developers.reserva.ink, `llms-full.txt` (356 KB saved as `alt/rink_llms_full.txt`). REST `https://api.reserva.ink/v1/stores/...`, Bearer token generated in the panel (no approval, no client secret), per-resource scopes (`store.orders.read` etc.), idempotency keys on writes, **100 req/min per store** (429 above), no Retry-After. Plan gate: **only INKrível (R$799/mo list, up to 66% off during Best Friday until 2026-11-30)**; downgrade auto-revokes tokens.
- **Webhooks (VERIFIED)**: 43 events, `X-Webhook-Signature` HMAC-SHA256 of raw body, `event_id` for dedupe, 5s connect + 5s response timeout, 5 attempts over ~45 min (immediate, 30s, 2m, 8m, 32m), then nothing is retried and the panel does not alert; 90-day delivery history; manual resend. Two store types: **INK storefront** (19 order events) and **integration store** (9 `external_order.*` events: created/canceled/refunded/waiting_to_be_sent/sent/delivery_in_progress/left_for_delivery/delivered/delivery_failure).
- **Gap that kills it for ML**: scope table shows `POST` exists for exchanges, products, collections, promotions, refunds, product clusters; **there is no `POST /v1/stores/orders` and no way to create an external order**. `external_orders` is read-only ("vendas fora da INK empurradas via API" are created by partner apps). Partner apps listed: **Shopify, Nuvemshop, CartPanda, Hotmart** (VERIFIED, help center). So a Mercado Livre order cannot be pushed in by us via the public API. Possible indirect route: ML -> Shopify/Nuvemshop (via an ERP/hub) -> INK app. Not tested; adds a monthly platform and a hub; UNVERIFIED.
- Label/NF: INK ships with its own carrier and tag; NF behaviour for integration stores: UNVERIFIED (docs mention `orders_nfe` table in financial exports only).
- Price (VERIFIED, reserva.ink/site/quanto-custa-reserva-ink, 2026-11-07), cost per piece by plan (Experimente 39.90/mo, Basico 159/mo, Aceleracao 499/mo, INKrivel 799/mo):
  - Camiseta Fem/Masc: 64.90 / 64.90 / 54.90 / 49.90
  - Camiseta Algodao Peruano: - / 79 / 74 / 65; Oversized - / 80 / 80 / 75
  - Infantil, Body, Regata: - / 62 / 53 / 46
  - **Hoodie Moletom: - / 159 / 147 / 119**; Suéter 139 / 128 / 99; Cropped Moletom 119 / 109 / 89
  - Shipping charged separately (dynamic by CEP; `GET shipping_simulation` returns business days).
- Min order: none (on demand). Lead time: production 2-5 business days (Nuvemshop article, May 2024; may be outdated) plus carrier. Returns: exchange/refund flows in API; refund only before production or up to 7 days after delivery (VERIFIED).
- CPF/CNPJ: **CPF is fine to start**, can switch to CNPJ later; they recommend MEI (VERIFIED, reserva.ink/site/print-on-demand FAQ).
- Reviews: self-reported 4.8 stars, 2.84M items sold, R$247M revenue (home page). Reclame Aqui blocked: UNVERIFIED.
- Verdict: **best-documented automation**, wrong shape (storefront-centric, no order injection), pricier, and API only at the top plan.

### 3.3 Printful (Charlotte NC; Brazil operation announced 2021)
- Production: Brazil page says "fulfillment center in Brazil", "products printed in Brazil", fulfillment 2-5 business days, **delivery to Brazil averages 10-25 business days** (VERIFIED, printful.com/print-on-demand-brazil, 2026-11-07). The two sentences together suggest only part of the catalog is produced locally. 2021 news: partners in Rio and Sao Paulo, "delivered in 1-5 business days", no customs duties; April 2022 update: Sao Paulo partner ended, non-apparel moved to Rio, **where apparel is made now is not stated** (VERIFIED news page; apparel location UNVERIFIED).
- API (VERIFIED, developers.printful.com/docs/v2-beta/, 2026-11-07): v2, bearer private token / OAuth, 120 requests per 60 s leaky bucket; orders are created as drafts then confirmed; order items, shipments, invoice, order estimation; shipping rates v2 with `customs_fees_possible`; **webhooks**: shipment sent/delivered/returned/out of stock/canceled/put on hold, order created/updated/failed/canceled/on hold/refunded, catalog stock/price changed, mockup finished; catalog filterable by `selling_region_name=brazil`. Signature scheme for webhooks: not found in the 100 KB read: UNVERIFIED. No NF (nota fiscal) support mentioned.
- Marketplaces: Shopify, Etsy, Wix, WooCommerce, Nuvemshop etc.; **no Mercado Livre** found. API order creation lets us bridge it ourselves.
- Label: Printful ships with its own carrier label; accepting an ML label: UNVERIFIED (very unlikely).
- Price: Brazil page shows "from $8.50" tee and "from $18.72" hoodie, currency sign `$`, BRL not given (VERIFIED text, currency ambiguous). Can charge buyers in BRL and pay Printful in BRL (VERIFIED). A Nuvemshop review summary says the main complaint is **high prices in Brazil** and no PIX (third-party).
- Min order: none. Returns: Printful policy not read: UNVERIFIED. Reviews: 4.8 from 4,020 reviews (self-reported, printful.com/br).
- CPF/CNPJ: not read: UNVERIFIED. Customs notes: Printful says Brazilian customers do not pay duties on locally produced items.
- Verdict: **best technical API of the ones with local production**, but delivery 10-25 days is poor for ML, price unknown, ML label/NF unknown.

### 3.4 Gelato
- Production: global network of local printers in 32 countries; Brazil page claims "quality local printing in Brazil" (VERIFIED, gelato.com/print-on-demand/brazil, `alt/gelato_br.txt`). The page is a template shared across countries; **which Brazilian partner prints apparel, and whether tees/hoodies are made in Brazil: UNVERIFIED.** dodropshipping.com says the Brazil examples it saw were posters, not apparel (third-party). PrintKK (competitor blog, 2026-04-16) says Gelato has local production in Brazil (UNVERIFIED, competitor).
- API (VERIFIED partly): v4 Order API; webhooks configured in Dashboard > Developer > Webhooks with custom auth header or query credential, test button, GET or POST (support.gelato.com article, 2025-10-30). Events: `order_status_updated`, `order_item_status_updated`, `order_item_tracking_code_updated`, `order_delivery_estimate_updated` (beta), `catalog_product_stock_availability_updated`, `store_product_*`. 3 attempts, 5 s apart, retry unless 2xx (developers.gelato.com/docs/webhooks, read through WebFetch; the runner got a Cloudflare challenge on developers.gelato.com, so the raw copy is not saved). Sandbox exists (help article title seen). API terms in a separate page.
- Marketplaces: Shopify, Etsy, TikTok Shop, Amazon, WooCommerce, Wix, Squarespace, BigCommerce (VERIFIED, gelato.com footer). **No Mercado Livre.** Make.com has a community Gelato app (Watch Orders, Create/Quote/Cancel Order, Make an API Call; Make does not maintain it, VERIFIED apps.make.com/gelato-l9p9ry.md). Composio has a Gelato toolkit page (title seen, not read).
- Label/NF: Gelato states it handles customs, cross-border invoicing, tax/VAT (marketing text). Brazilian NF-e/DC-e for domestic ML orders: UNVERIFIED. Third-party label: UNVERIFIED.
- Price: tee/hoodie BRL not obtained (pricing and product pages gave a Cloudflare challenge to the runner). Gelato+ plans $23.99/mo or $19.99/mo annual, up to 25% off (ecommerce-platforms.com review; check against the live page). Lead time: Brazil local tees UNVERIFIED.
- Reviews: 4.8 from 963 reviews on its own page (self-reported).
- CPF/CNPJ: UNVERIFIED.
- Verdict: good API and a Make module; Brazil apparel reality unproven.

### 3.5 Others checked
| Name | What was learned | Status |
|---|---|---|
| Printify | Brazil is not on the restricted list (VERIFIED, help.printify.com). A 2026 blog says Printify has no direct operations in Brazil. No Brazilian print provider verified. MCP exists (TSavo/printify-mcp, 41 stars) but covers products/images only, no orders. | Not a Brazil producer |
| Gooten | July 2022: added "a new apparel manufacturer in Brazil" (Bella+Canvas 3001/6004); 3-5 day production. Other items ship from abroad 10-30 business days with 10-35% import duty. 2022 post, current status UNVERIFIED. | Dated; skip unless confirmed |
| Cloudprinter | PrintKK blog says it connects to local printers in Brazil. No primary source read. | UNVERIFIED |
| Dogama (dogama.com.br) | General dropship catalog (not custom print). Integrates Mercado Livre, Shopee, Amazon, TikTok Shop, Magalu, Shein, etc., Bling, Tiny; NF-e auto-issue is beta; 6% commission per a third-party. | Not POD; useful as a model of ML integration |
| DSlite / Hayamax | DSlite has an API for catalog sync and XML/XLSX feeds; dropshipping mode requires CNPJ ("Necessario ser Pessoa Juridica"); "venda direta" mode does not. Suppliers listed are electronics, auto parts, home; no apparel POD (VERIFIED, `alt/dslite.txt`). Hayamax site 403. | Not apparel POD |
| Uma Penca (Chico Rei) | Free to start, you pay production on sale (ecommercenapratica, third-party). Site blocked from runner (connection reset); no API page found. | UNVERIFIED |
| Chico Rei / Camiseteria | Retail custom tees, free shipping from R$155 (home page). Not a supplier API. | Not applicable |
| Printi | Online graphic printer in Sao Paulo selling printed goods incl. t-shirts for resale; no API/dropship page found. | UNVERIFIED |
| Estampa Ja | HTTP 429 from runner. | UNVERIFIED |
| Zazzle, Spreadshirt, Custom Ink, Mooi, "Crie Sua Camisa" API, Qstomizer, Ink Dropshipping | Nothing Brazil-specific or API-relevant found in the searches run. | Not found |
| Brazilian review sites | Reclame Aqui: 403 Cloudflare or 404 from the runner for montink, reserva-ink, dimona, printful. Trustpilot 403. | Reviews UNVERIFIED for all |

## 4. Ranking (fit for: API order creation + webhooks + Mercado Livre bridge + CPF start)

Baseline row is Dimona with the corrections from section 1.

| Rank | Provider | Tee front print (BRL) | Hoodie (BRL) | Public API / create order | Webhooks | ML support (native) | ML bridge feasibility | Onboarding | Lead time |
|---|---|---|---|---|---|---|---|---|---|
| baseline | Dimona / Dropsimples | 36.90 (Classic, 2024 PDF) | 127.00 (2024 PDF) | Yes, `api-key`, create order, NFe + label endpoints (label needs email) | Yes, unsigned, per status | No, policy says no ML/Shopee/Amazon | Unclear: API has label endpoint, policy says no | CPF OK, no monthly fee | prod 3-5 d + ship 5-10 d |
| 1 | Printful v2 | UNVERIFIED (US$8.50 base listed) | UNVERIFIED (US$18.72 base listed) | Yes, bearer token, draft then confirm | Yes (shipment/order/stock), signing UNVERIFIED | No | Feasible for order+tracking; label/NF unknown; slow delivery | Self-service; CPF/CNPJ UNVERIFIED | fulfil 2-5 d + 10-25 d avg to BR |
| 2 | Reserva INK (INKrivel) | 49.90 (plan-dependent up to 64.90) | 119.00 (up to 159) | REST read/write for products/exchanges/refunds, **no order creation** | Yes, HMAC, 43 events | No (Shopify, Nuvemshop, CartPanda, Hotmart) | Not via public API; only through Shopify/Nuvemshop app | CPF OK; plan R$799/mo for API | prod 2-5 d + carrier (RJ DC) |
| 3 | Gelato | UNVERIFIED | UNVERIFIED | Yes, v4 + Make module | Yes (custom auth header) | No (TikTok Shop, Amazon, Shopify, Etsy...) | Feasible for orders; Brazil apparel and NF unknown | Self-service; CPF/CNPJ UNVERIFIED | UNVERIFIED |
| excluded | Montink | 38-161 catalog (cost vs retail UNVERIFIED) | 110-161 | None found | None found | No (claimed feed only) | Same factory as Dimona | Plans R$126-199/mo | ~4 d + carrier |

Reading the table: on *price* and *Brazilian speed* Dimona/Dropsimples wins; on *API engineering* Reserva INK wins; on *order-in API with webhooks* Printful and Gelato win, but their Brazilian speed and prices are unproven. If the Dimona email (section 6) confirms the label endpoint accepts an ML label, **stay with Dimona**.

## 5. MCP servers, connectors, and what each adds

### 5.1 Providers
- No provider publishes an MCP server we could find (searched Printful, Printify, Gelato, Montink, Reserva INK, Dimona). Third-party Printify MCP exists (TSavo/printify-mcp, 41 stars, products/images only; VERIFIED). Reserva INK ships `llms-full.txt` docs designed to paste into Claude/ChatGPT and states there is no n8n/Zapier connector yet (VERIFIED), so use generic webhook + HTTP blocks.
- Make.com: community Gelato app (above). Zapier/n8n: no Dimona, Montink, Reserva INK, Printful-Brazil connector verified. n8n/Zapier pages for Mercado Livre returned 404 on the runner; a Base.com page mentions Zapier but that is Base.com's own app. n8n community node "PickerPro Meli" exists (package page seen; scope UNVERIFIED, appears to be public-site endpoints).

### 5.2 Mercado Livre MCP servers
| Server | What it is | Verdict |
|---|---|---|
| **Official**, `https://mcp.mercadolibre.com/devsite/v1/mcp`, docs page developers.mercadolivre.com.br/pt_br/server-mcp (last updated 2026-09-10) | **Documentation search only**: tools `search_documentation` and `get_documentation_page`; OAuth 2.0 via the MCP client. (VERIFIED, `alt/ml_mcp_docs.txt`) | Useful for Claude to read ML docs while building the worker. Cannot read orders or labels. |
| github.com/mercadolibre/mercadolibre-mcp-server | Org-owned repo, README: endpoint `https://mcp.mercadolibre.com/mcp` with Bearer token, tools not listed, 6 stars, 1 commit (VERIFIED page). Whether this is the operational API server: UNVERIFIED. Docker MCP catalog also lists a "mercado-libre" server "Provides access to Mercado Libre E-Commerce API", requires secrets (VERIFIED). | Worth a 10 minute probe with a real app token; not proven. |
| gustavossouza/mcp_mercadolivre (npm @gustavohssouza/mcp-mercadolivre) | 42 tools: listings, questions, orders, shipments, returns, promotions, ads, catalog; read-only mode, tool profiles, confirmations, audit log; OAuth with refresh. ~10 stars. glama: updated 2026-09-30. (VERIFIED via mcpmarket + glama) | Best community candidate for interactive use. Invoice/DC-e support not mentioned. |
| lumile `mercadolibre-mcp` 0.3.2 (PyPI, 2026-10-29) | Alpha, 20 tools incl. `search_orders`, `get_order`, `get_shipment`, listings CRUD; 18 sites incl. MLB; local token files; no invoices (VERIFIED, PyPI). | Alpha. |
| rafaelprimeiro/rg-mcp-mercadolivre | 7 tools incl. `vendas_para_enviar`, `detalhes_envio`, `gerar_etiquetas` (PDF/ZPL); inactive since 2026-03-20; refresh token single-use stored in a local file (VERIFIED, glama). | Shows the label call works through MCP; unmaintained. |
| newerton/mcp-mercado-livre | One tool `get-produtos` (product data). 15 stars. | Product lookup; avoid anything that scrapes (ML T&C). |
| Mercado Livre Vendedor (mcp-dir), brmarket-mcp, mcp-brazil-marketplaces | Read-only seller data; or public search (brmarket uses x402 micropayments; the other scrapes OLX/ML). | Not for fulfillment. |

### 5.3 What an MCP would add versus a plain worker
- **Adds**: Claude can answer or act in a chat session ("show unshipped orders", "fetch label for shipment X", "answer this buyer question") without new code; docs lookup while coding; good for manual exception handling and debugging.
- **Does not add**: webhook reception. ML requires a public URL answering 200 in under 500 ms and Dimona/Reserva INK/Gelato push to URLs too. An MCP server is request/response driven by a client and cannot be that endpoint. Also unsuited: deterministic idempotent fulfillment, durable single-use refresh-token storage (community MCPs keep tokens in local files, which does not fit a cloud or scheduled session), HMAC verification, retry/dead-letter handling.
- **Recommended shape** (inside current Cloudflare $5 and GitHub plans; Worker, KV/D1 and Queues quotas not re-checked today: UNVERIFIED):
  1. Worker `/ml-notify`: verify source IP, return 200 within 500 ms, enqueue `{topic,resource}`.
  2. Queue consumer: GET order + shipment from ML (token in KV, single-use refresh handled with a lock), create supplier order (idempotency key = ML order id), DC-e or NF-e step, fetch label PDF, hand it to the supplier if allowed.
  3. Worker `/supplier-hook`: receive Dimona/Printful/Reserva INK status, push tracking/status back to ML.
  4. Claude scheduled task (daily or hourly) reconciles: `GET /missed_feeds`, supplier order list vs ML orders, alerts on stuck `invoice_pending`, DC-e deadline (3 days), and unshipped orders. This is the safety net for dropped webhooks (Reserva INK drops after ~45 min; ML after 1 h).
  5. Optional: add the gustavossouza MCP (read-only profile) or the official docs MCP to Claude for ad-hoc work. Do not make production flow depend on it.

## 6. Still unknown, and how to close each

| Unknown | Why it matters | How to close |
|---|---|---|
| Does Dimona's `POST /order/{id}/shippingLabel` accept an ML (Mercado Envios) label PDF, and for which seller type? | Decides whether we can stay with Dimona | Email api@dimona.com.br (the collection says to). Ask: (1) accept external label PDF for ML orders? (2) is it allowed for CPF accounts? (3) NF for CPF account on ML: DC-e flow or their NF? (4) webhook retry policy and signing? (5) sandbox? (6) rate limits? (7) formal exception to the "no ML" rule? |
| Which ML shipping mode applies to our account/category in Brazil; is `custom` / seller-handled allowed | If allowed, the supplier's own Correios/Jadlog label and tracking can be used, removing the label problem for every supplier | Create an ML developer app, read `GET /users/{id}/shipping_preferences`, test with a dummy listing (no scraping). |
| ML DC-e API details (auth, fields, who can emit, cost) | Required for CPF sellers on drop_off/cross_docking | Read `developers.mercadolivre.com.br/pt_br/integracao-dce` through the runner (title seen, body not read). |
| Printful: where apparel is made in Brazil, BRL tee and hoodie price, real delivery days to Brazil, webhook signing, CPF/NF | Could be a valid second source | Public catalog endpoint `GET /v2/catalog-products?selling_region_name=brazil` and shipping rates v2 need a token (free account, no order): build a probe. Needs the owner to create the account. |
| Gelato: any Brazilian apparel producer, BRL price, delivery time | Same | Same approach with a Gelato API key (free account), `GET catalog` + `quote`. |
| Reserva INK: any way to create external orders (private/partner API), NF behaviour for integration stores, API on promotional plan price | Would turn it into a strong candidate | Ask INK support whether a "pedido de integracao" create endpoint exists outside Shopify/Nuvemshop/CartPanda/Hotmart; ask for NF-e at sale value on integration stores. |
| Montink: any private API or ML order flow, CPF onboarding | Likely same as Dimona | Ask support; low priority since it is Dimona infrastructure. |
| Reviews (Reclame Aqui, Trustpilot) for all | Quality/risk | Blocked by Cloudflare/403 from the runner. Owner can check manually, or try the Reclame Aqui search through a browser session. |
| Return policy for Printful, Gelato, Montink | Cost of defects | Not read. |
| Cloudflare plan limits for KV/D1/Queues | Cost control | Check pricing page before building. |

## 7. Source index (all fetched 2026-11-07 unless noted)
- Dimona Postman collection (saved): docs/brazil_data/dimona/postman_ateAuth_true_versionTag_latest.json
- Montink home/integrations/catalog: montink.com.br, sou.montink.com/integracoes-montink/, montink.com.br/dropshipping (raw: alt/montink_*.txt)
- Nuvemshop Montink app: nuvemshop.com.br/loja-aplicativos-nuvem/montink; Printful app: .../Printful
- Reserva INK: reserva.ink/site/api, /site/quanto-custa-reserva-ink, /site/print-on-demand; developers.reserva.ink/llms-full.txt; help center cloudchat3.cloudhumans.com/hc/central-de-ajuda-reserva-ink (raw: alt/rink*.txt, alt/rinkh_*.txt)
- Printful: printful.com/print-on-demand-brazil; printful.com/news/printful-partner-facility-in-Brazil+ (2021, update 2022-04-05); printful.com/news/printful-localized-for-brazilian-market; developers.printful.com/docs/v2-beta/
- Gelato: gelato.com/print-on-demand/brazil; support.gelato.com/en/articles/8996576-how-do-i-configure-notifications-webhooks (2025-10-30); developers.gelato.com/docs/webhooks; apps.make.com/gelato-l9p9ry.md
- Mercado Livre developers: .../en_us/products-receive-notifications; .../en_us/mercadoenvios-mode-2; .../pt_br/importar-nota-fiscal; .../pt_br/anexar-nota-fiscal; .../pt_br/envios-personalizados; .../pt_br/server-mcp
- MCP: github.com/mercadolibre/mercadolibre-mcp-server; pypi.org/project/mercadolibre-mcp/; glama.ai/mcp/servers/rafaelprimeiro/rg-mcp-mercadolivre/tree; mcpmarket.com/server/mercado-livre; github.com/newerton/mcp-mercado-livre; github.com/TSavo/printify-mcp; glama.ai search "mercado livre"
- Third-party context: ecommercenapratica.com (POD platforms), dodropshipping.com/best-dropshipping-suppliers-in-brazil, printkk.com/blog/articles/print-on-demand-brazil (2026-04-16, competitor), gooten.com/blog/expand-your-print-on-demand-business-in-brazil (2022-07-14), nuvemshop.com.br/blog/dropshipping-mercado-livre, dogama.com.br/en/integracoes

# Brazilian apparel producers for a Mercado Livre seller: who automates, who takes ML, who is cheap

Research date: 2026-11-07. Method: web search + WebFetch for discovery, then the GitHub runner probe (`scripts/brazil/probe.py` tasks `prod`, `prod2`, `prod3`, workflow `brazil-probe.yml`, repo Rodantmat/Alphadog-Styles) to read vendor pages directly. Raw page text is saved in `docs/brazil_data/prod/`, `prod2/`, `prod3/`. No logins, no accounts, no bot-wall bypass (Reclame Aqui and Colab55 inner pages returned a Cloudflare challenge and were left unread).

Labels: **VERIFIED** = read on the vendor's own page on 2026-11-07 (URL given, raw copy saved). **UNVERIFIED** = third-party claim (blog, comparison site, competitor), a claim the vendor makes but does not document, or not retrievable. Prices BRL. "ML" = Mercado Livre. Prior notes (ALTERNATIVES.md, LABEL_BRIDGE.md, ML_OWN_SHIPPING.md, BRAZIL_STUDY.md) are not repeated; only referenced.

---------------------------------------------------------------------------
## 0. Bottom line

1. **No Brazilian producer has a VERIFIED, documented way to take a Mercado Livre order and ship it under the ML label.** Not one. That is the same wall as before (ML_OWN_SHIPPING.md: for T-shirts ME2 is mandatory, the ML label must be on the parcel). What changed is that two new candidates turned up that Dimona does not match.
2. **Gubo (gubo.com.br, Santo André SP) is the best automation by a wide margin and the only new one with a public API doc.** Self-serve REST API (bearer key, idempotency, signed webhooks, SKU linking, freight quote, test mode, no monthly fee, CPF or CNPJ recipients, NF-e at the seller's sale value in the package). Gaps: no field for an external shipping label, no ML mention anywhere, products must be created in their Studio (API cannot create products), production up to 7 business days. It is the one to build on **if** it will accept an ML label or if we use a non-label route. (VERIFIED, section 3.1.)
3. **Estampa Impressa (estampaimpressa.com.br) is the only producer whose own site says "integração automática com Shopee, Mercado Livre, Amazon".** Their site also says CPF is fine, NF included, 1 piece minimum, 1-2 business days production. But: no API doc, no prices, no legal entity or CNPJ shown on the site, founded 2024, catalog is mugs-first with apparel by sublimation or DTF, testimonials look generic. Treat as a lead to interrogate, not a supplier yet. (VERIFIED claim, UNVERIFIED substance, section 3.2.)
4. **Montink's own plan page lists "Integração com +20 Marketplaces (via Bling)" and "Configuração de ERP (Bling)"** (VERIFIED, sou.montink.com/comparativo-planos-montink). That is new versus ALTERNATIVES.md (which found no ML in their integrations list). It is a Bling-mediated flow and still runs on Dimona infrastructure, so the label problem likely stays. Also: the page `montink.com/mercado-livre` is just a Montink tenant store whose slug is "mercado-livre", **not** an integration (VERIFIED, checked so nobody repeats the mistake). dodropshipping.com's line "Montink integrates Shopify and Mercado Livre" is UNVERIFIED.
5. **Uma Penca, HotPrinti, YouDraw, Reserva INK, Colab55 are storefront-centric: sell inside their store or Shopify/Nuvemshop/Yampi. No ML, no order-intake API** (sections 3.5-3.9).
6. **The realistic ML-compatible class is not a platform at all: a small estamparia/DTF shop that physically accepts the ML label and drops the parcel at the Mercado Envios point** (example: Camisetas Rápido, SP, DTF/DTG with no minimum, 24-72 h). They have no API, but a human-operated shop is the only thing that can actually stick a third-party label. Automation then has to be on our side (e-mail/WhatsApp/spreadsheet drop). (section 3.10, UNVERIFIED that they would do it.)
7. **What decides everything is still one question to each producer**: "Aceita colar a etiqueta do Mercado Envios (PDF) e despachar na agência/Coleta, ou postar com rastreio próprio?" Section 6 has the exact wording per candidate.

---------------------------------------------------------------------------
## 1. Master list (everything found, with verdict)

| # | Name / URL | Where | Apparel | API / automatable intake | ML evidence | NF policy | Price 1 tee/hoodie with 1 print | Verdict |
|---|---|---|---|---|---|---|---|---|
| 1 | **Gubo** gubo.com.br (Gubo LTDA, CNPJ 28.139.292/0001-67) | Santo André, SP | tees, oversized, babylook, cropped, hoodies, kids, pet, ecobag | **Yes, public API + docs** (3.1) | none | **NF-e at seller's sale value, simplified DANFE without values (triangular op.)** | tee R$39.90 + R$11.90 = **R$51.80**; hoodie R$99.90 + 11.90 = **R$111.80** (Pix) | **Top candidate for automation** |
| 2 | **Estampa Impressa** estampaimpressa.com.br | SP (WhatsApp 11); no entity shown | tees, croppeds (sublimation or DTF), mugs, caps | Claimed auto integration; **no API doc** | **Claims ML, Shopee, Amazon, Magalu, TikTok Shop...** | "emissão de NF incluída no processo" (no detail) | not public | **Must interrogate**; trust risk |
| 3 | **Montink** montink.com / sou.montink.com | Belo Horizonte (company) / Dimona factory RJ | tees, hoodies, caps, ecobags | No public API found; Bling ERP + Nuvemshop/Shopify native | "+20 marketplaces via Bling" (own plan page) | at cost by default; sale-value NF via Bling + CNPJ + certificate (prior note) | catalog Quality tee R$48.20, canguru R$160.95 (cost vs retail UNVERIFIED) | Maybe; label unsolved |
| 4 | **Dimona / Dropsimples** camisadimona.com.br | Rio de Janeiro | full range | API V2 + unsigned webhooks | policy: **refuses ML**; API `shippingLabel` needs e-mail | NF at cost by default, own NF attachable | Classic tee R$36.90, canguru R$127 (2024 PDF) | Cheapest; ML blocked by policy (email api@dimona.com.br still open) |
| 5 | **Camisetas Rápido** camisetasrapido.com.br | São Paulo, since 2012 | tees, polos, DTF/DTG/silk/embroidery | none (quote by WhatsApp/e-mail) | none (B2B uniforms) | not stated | not public | **Class representative of manual estamparias**; only route that can physically take an ML label |
| 6 | **Uma Penca** umapenca.com (Crie Up LTDA, CNPJ 61.367.296/0001-78) | Juiz de Fora, MG | tees, kids, dry fit, ecobags, mugs, posters | none found | none | not stated | tee base R$47.90 (Aug 2026 press) | No: storefront only |
| 7 | **YouDraw** youdraw.com.br | São Paulo suppliers | 43 products, tees from R$30, hoodies from R$60 (site text) | **API "Em breve"**; Shopify, Nuvemshop, Yampi (Pro R$149/mo = 1 store) | none | not stated | tee from R$30, hoodie from R$60 (before print fee, UNVERIFIED) | No for now |
| 8 | **HotPrinti** hotprinti.com.br (CNPJ 11.888.086/0001-57) | not stated | tees etc. | none (own store product) | none | not stated | plans R$0 (15 products, wholesale min R$200) / R$99.90 / ... | No |
| 9 | **Reserva INK** reserva.ink (Arezzo) | Rio de Janeiro | tees, hoodies | REST read API; **no create-order**; HMAC webhooks; plan R$799/mo (prior) | none (Shopify, Nuvemshop, CartPanda, Hotmart) | per prior note | tee R$49.90-64.90, hoodie R$119-159 (prior, VERIFIED 2026-11-07) | No for ML |
| 10 | **Printful** | Charlotte NC + Brazil partner | 49 BR-region products (prior) | v2 API | none | none | USD, 10-25 d delivery | No for ML |
| 11 | **Cloudprinter** cloudprinter.com | NL, claims local printers worldwide | tee in catalog | **Print API (REST), Zapier** (VERIFIED home) | none | none | not public | UNVERIFIED Brazil apparel (its BR page 404; PrintKK blog claims local printers) |
| 12 | **Colab55** colab55.com | SP | artist marketplace (decor/fashion/stationery) | none found | none | handled by them | n/a | No (artist marketplace; inner pages Cloudflare 403) |
| 13 | Gelato | global | BR local claim | v4 API + Make | none | unknown | unknown | Already in ALTERNATIVES.md, unproven |

Looked at and **not** custom-apparel suppliers: Dogama, DSlite, Drop Nacional/Dropi, B2 Drop, Drophar (CNPJ required, 8% fee, multi-supplier catalog), Vendaecia, Conecta Moda (plain tees for Mentoria members), Hayamax (electronics), Printi (graphic printer; /camisetas 404), Goimage (photo books), Nicephotos/Digipix (photo products), Elo7 (closed per prior note). Not found at all despite searches: Pop Up Print, Print Factory, Studio Stamp, Camisa Pronta, Kapa, Printu, Mooma, Ink Dropshipping, Zazzle/Spreadshirt Brazil production, Tiendanube/"Printful BR" as separate entity. Estampa Já returned HTTP 429 (not read). Marcazo: site timed out; a blog comment (UNVERIFIED) says it is leaving Brazil.

---------------------------------------------------------------------------
## 2. Reputation (Reclame Aqui) - mostly unobtainable

Reclame Aqui served a Cloudflare challenge (HTTP 403) to the runner for montink, camisa-dimona, dimona, dropsimples, reserva-ink, hotprinti, estampa-impressa, printful, youdraw; gubo timed out. I did not try to bypass it. Only **Uma Penca** loaded (https://www.reclameaqui.com.br/empresa/uma-penca/, 2026-11-07): "Empresa Verificada", header "Resolve 84.6% das reclamações", but the performance panel says "Sem Reputação" (fewer than 10 evaluated complaints); 8 complaints received, 100% answered, resolution rate not shown. Other reputation data, all UNVERIFIED third party:
- Montink: 4.4/5 and 7.7/10 on Reclame Aqui per dodropshipping.com; Nuvemshop app 4.5/5 from 14 reviews (prior note).
- Gubo: self-reported "13 mil+ marcas já produzem com a Gubo" (VERIFIED as a claim on gubo.com.br/integracoes), founded 2017 per a competitor blog (UNVERIFIED).
- Estampa Impressa: self-reported "+500 vendedores", founded 2024 (claims only).
- HotPrinti: self-reported 39,173 partners.
- Uma Penca: press says 30,000 stores, ~R$4M revenue 2026 (startups.com.br, Aug 2026, UNVERIFIED).
Owner can open Reclame Aqui in his own browser for Gubo, Estampa Impressa, Montink, Dimona; I cannot.

---------------------------------------------------------------------------
## 3. Candidate cards

### 3.1 Gubo - gubo.com.br (VERIFIED, 2026-11-07; raw: prod/gubo/, prod2/, prod3/gubo_com_br_docs_api_*.txt)
- Entity: Gubo LTDA, CNPJ 28.139.292/0001-67, Rua Basílio de Magalhães 145, Guaraciaba, Santo André/SP. Factory in Santo André (gubo.com.br/integracoes).
- Contact: WhatsApp +55 11 97667-1256 (https://wa.me/5511976671256), Studio login https://studio.gubo.com.br. No e-mail on pages read.
- Products and price (gubo.com.br/precos): plain piece price, Pix (card ~5% more, 3x): Camiseta Padrão R$39.90, Oversized R$58.90, Tech Modal R$54.90, Babylook R$39.90, Cropped R$25.90, kids R$25.90, Moletom com capuz 2 cabos R$99.90, 3 cabos R$129.90, sem capuz R$78.90, ecobag R$25.90, pet R$25.90. Print by area, any colour: small R$5.90 (to 350 cm2), medium R$8.90 (to 700), large R$11.90 (to 1,050), mega R$16.90 (to 1,400). Basic printed label free; custom label R$1.50; kraft tag R$1.50; neutral packaging and art review included. Freight by CEP, normally passed to the buyer. No subscription. First purchase 25% off up to R$100.
  - **Standard tee with large front print: R$51.80 Pix** (R$54.53 card). Front+back large: R$63.70. Hoodie 2-cable with large front: R$111.80.
- Production: "até 7 dias úteis" (the freight doc also states 7 business days of production + carrier time). No minimum order.
- **API** (docs at gubo.com.br/docs-api/*, 22 pages, last update 2026-10-11): Bearer key (`gubo_test_` / `gubo_live_`), `POST /pedidos/por-variante` or `/por-produto`, `Idempotency-Key`, `referencia` unique, `POST /fretes/cotacoes`, `GET /fretes/servicos`, `PUT /vinculos` (link your SKU to their variant, 100 per call), `POST /pedidos/{id}/pagar`, `GET /carteira`, `GET /pedidos?atualizado_desde=`, `POST /pedidos/{id}/cancelar`. Webhooks with signed header (`Gubo-Assinatura: t=...,v1=...`, secret `whsec_`), events pedido.pendente / aguardando_pagamento / confirmado / em_producao / enviado (with `envio.rastreio`) / entregue / cancelado / recusado, at-least-once, dedupe by event id. Test mode with 1,000 test orders/day, no balance used. Limits: 200 orders/day and R$5,000/day paid via API by default, 600 req/min (raised on request). Official MCP server "previsto para a fase 2"; a "Integrar com IA" page exists.
  - **Limits that matter for us**: (a) "A API não cria produtos nem recarrega a carteira": designs/products must be created in the Studio UI, then linked by SKU; (b) payment is from a prepaid wallet (Pix top-up 5% off, or card auto top-up via Stripe); (c) carriers are "Olist Envios" Correios PAC, Jadlog, Pax (freight doc), chosen by us or cheapest; the order body has **no field for an external label or tracking input**; (d) recipient `documento` (CPF/CNPJ) is required.
- Integrations (VERIFIED, active): Nuvemshop, WooCommerce, Gubo Store (own storefront, 1.99% per sale, Mercado Pago payout), API. "Em desenvolvimento": Shopify, Yampi (waiting Yampi approval), **TikTok Shop "com a etiqueta de envio gerada pelo próprio TikTok"**, Wix. Instagram/WhatsApp orders registered manually in the Studio. **Mercado Livre is not mentioned.** The TikTok line is the only sign anywhere that Gubo is building third-party-label intake.
- NF policy: "NF-e discreta no pacote... DANFE simplificado, sem valores impressos... Informe o preço de venda para a Gubo usar na nota (operação triangular)." (gubo.com.br/como-funciona). Where the reference value is entered in the API: not found in the pages read (UNVERIFIED). Does the NF-e XML come back to us to import into ML (needed for ML drop_off/Coleta, see LABEL_BRIDGE 2): UNVERIFIED.
- Reputation: see section 2 (not obtained).
- Verdict: **best automation, best NF story, competitive price, unknown ML label acceptance.** Cheaper than Dimona on hoodies (R$111.80 vs R$127+R$0 in a 2024 PDF), about R$9-15 dearer on a basic tee with a large print.

### 3.2 Estampa Impressa - estampaimpressa.com.br (VERIFIED claims, 2026-11-07; raw: prod/estampaimpressa/)
- Header banner: "Integração automática com Shopee, Mercado Livre, Amazon e muito mais!" Integrations list: AliExpress, Amazon, Magalu, Mercado Livre, NuvemShop, Shein, Shopify, Shopee, Temu, TikTok Shop, WooCommerce. "Com a integração ativa, os pedidos chegam automaticamente... Emissão de nota fiscal incluída no processo... Suporte técnico para configurar sua integração." No Bling mention. **No API documentation.**
- FAQ: CNPJ not required (CPF ok, MEI ok); minimum 1 unit; production 1-2 business days; ships via Correios and partner carriers with tracking; unbranded ("seus clientes nunca saberão"); files PNG/PDF/TIFF 300 dpi; defects reprinted free. Payment: one FAQ says "Você vende, recebe o pagamento e então nos envia o pedido... paga apenas o custo de produção + frete" (post-paid or per-order, unclear).
- Apparel techniques: "estampas sublimadas ou DTF". Sublimation only works on polyester/light fabric; for cotton tees the DTF path matters. Fabric/blank brand not stated.
- Contact: WhatsApp (11) 94967-5638, contato@estampaimpressa.com.br.
- Red flags: founded 2024; no CNPJ/legal entity or address anywhere in the footer; mug-first catalog; testimonials ("80 canecas") are generic; no prices; the ML label mechanics are not described ("a página não menciona etiquetas"). Reputation not obtainable.
- Verdict: only one that claims ML; needs hard questions and a paid test order (small) before any trust.

### 3.3 Montink (prior notes + new)
- New VERIFIED: sou.montink.com/comparativo-planos-montink lists "Configuração de ERP (Bling)", "Integração com +15 Plataformas de Loja Virtual (via Bling)", "Integração com +20 Marketplaces (via Bling)", "Integração nativa com NuvemShop e Shopify", Hotmart/Eduzz/Monetizze; prices R$149/mo, R$126.60/mo annual, Escalada R$199/mo annual. The checkmark pattern per plan was not captured in the text, so which plan has the Bling items is UNVERIFIED.
- How an ML order would flow (UNVERIFIED, my reading): ML -> Bling (Bling's ML integration issues the ML label and NF-e) -> Montink product mapped in Bling -> Montink produces and ships with its own label (Dimona infrastructure). Then it is the same label conflict as Dimona. The Montink help centre (montinkhelp.zendesk.com) is behind Cloudflare, so the exact article could not be read.
- Catalog prices seen on montink.com (prior): Quality tee R$48.20, Moletom Canguru R$160.95; whether cost to seller or retail: UNVERIFIED.
- Verdict: a Bling route to ML exists on paper; ask whether the ML label/Mercado Envios flow is supported or only order import.

### 3.4 Dimona / Dropsimples
Unchanged: API V2, unsigned webhooks, cheapest (Classic tee with 1 print R$36.90, Prime R$49.90, canguru R$127, 2024 PDF), policy refusing ML/third-party labels (LABEL_BRIDGE 1.1). camisadimona.com.br returned Vercel Security Checkpoint HTTP 429 again; nothing new. The e-mail to api@dimona.com.br about the `shippingLabel` endpoint is still the single cheapest question in this whole study.

### 3.5 Uma Penca (VERIFIED, umapenca.com + RA page, 2026-11-07)
100% free store platform: you open a store on their site, they produce and ship. Plan "gratuito"; 10+ products (tees, kids, dry fit, ecobags, mugs, posters). No API, no ML, no marketplace feature on the pages read. Contact ola@umapenca.com.br. Blog says CPF ok. Reputation: section 2. Verdict: cannot be wired to ML.

### 3.6 YouDraw (VERIFIED, youdraw.com.br + /planos, 2026-11-07)
Plans: Grátis R$0 (own YD Store and "Vitrine na Loppi", no integrated store), Pro R$149/mo (1 integrated Shopify/Nuvemshop/Yampi store, 10% off production), Growth R$399/mo (3 stores, 15% off). **"API própria: Em breve".** Tees from R$30, hoodies from R$60 (home text). 48 h hub release for 80% of orders; label by them. Contact suporte@youdraw.com.br. Verdict: re-check when the API ships.

### 3.7 HotPrinti (VERIFIED, hotprinti.com.br, 2026-11-07)
Own-store platform (CNPJ 11.888.086/0001-57; WhatsApp +55 11 94600-9311; contato@hotprinti.com.br). Plans: Free (15 products, wholesale purchases with R$200 minimum), Iniciante R$99.90/mo, higher tiers not read. 24-48 h production claim. No API/ML. Verdict: no.

### 3.8 Reserva INK - see ALTERNATIVES.md 3.2 (home page re-read 2026-11-07, unchanged).

### 3.9 Cloudprinter - cloudprinter.com (VERIFIED home, 2026-11-07)
"Print API" (REST, unlimited calls, Zapier), global print network incl. men's T-shirt in catalog. Its Brazil page returns 404; PrintKK says it connects to Brazilian printers (UNVERIFIED, competitor). Requires an account to see Brazil printers/prices. Label intake unknown. Verdict: cheap to ask, unlikely to help with ML.

### 3.10 Manual estamparias (class) - e.g. Camisetas Rápido (VERIFIED, camisetasrapido.com.br, 2026-11-07)
São Paulo, since 2012, silk screen, embroidery, DTF, DTG, "prazo 24-72 horas úteis", DTF/DTG with no minimum (silk/embroidery minimum 20), WhatsApp +55 11 2589-5524 (from page link). B2B/uniform focus, no API, no marketplace mention, no price list. Such a shop can stick any label and walk the parcel to a Coleta/agency. Automation is on our side (order e-mail or shared sheet). Reputation and willingness: UNVERIFIED. There are hundreds of such shops; this is the type of partner to shortlist if no platform accepts the ML label.

### 3.11 Aggregators that do not print
Drop Nacional/Dropi (Empreender), B2 Drop, DSlite, Drophar, Dogama, Vendaecia: general catalogs, no custom printing (VERIFIED by pages and vendor listings read). DSlite and Drophar need CNPJ. Not relevant to made-to-order tees.

---------------------------------------------------------------------------
## 4. Ranking: automation x ML compatibility x cost

Scores 0-5 are my judgement from the evidence above (so UNVERIFIED as a metric; the evidence behind each is labelled in the cards). Automation = public API/webhooks/CSV/e-mail ingest we can drive without a human. ML = evidence the producer can ship under an ML shipment (label, NF, handling). Cost = one tee and one hoodie with one print, delivered unbranded.

| Rank | Producer | Automation | ML | Cost | Product | Why |
|---|---|---|---|---|---|---|
| 1 | **Gubo** | 5 | 2 | 3.5 | **35** | Documented API+signed webhooks+test mode; NF-e at sale value; TikTok-label roadmap suggests label intake is conceivable; ML silent; 7-day production hurts ML handling time |
| 2 | **Estampa Impressa** | 3 | 4 | 2 | **24** | Only explicit ML claim; but no docs/prices/entity; cost unknown (scored 2 for risk) |
| 3 | **Montink (via Bling)** | 3 | 3 | 2 | **18** | "+20 marketplaces via Bling" on own page; platform fee R$126-199/mo; Dimona label policy underneath |
| 4 | **Dimona / Dropsimples** | 4 | 1 | 4 | **16** | Best price and a real API, but refuses ML labels (unless the api@ e-mail yields an exception) |
| 5 | **Manual estamparia (e.g. Camisetas Rápido)** | 1 | 5 | 3 | **15** | Only kind that can physically use the ML label; we build the automation (mail/WhatsApp); quality and price unknown |
| 6 | Cloudprinter / Gelato / Printful | 5 | 1 | 1-2 | 5-10 | Great APIs, no ML, foreign/slow or unproven BR apparel |
| 7 | YouDraw | 2 | 1 | 4 | 8 | API "em breve" |
| 8 | Reserva INK | 2 | 1 | 2 | 4 | Read-only API, R$799/mo |
| - | Uma Penca, HotPrinti, Colab55 | 1 | 0 | 3 | 0 | No intake path |

The ordering depends on one unknown, ML label acceptance. If the answer from Gubo is "yes, send the PDF", Gubo wins outright. If every platform says no, rank 5 (manual shop) becomes rank 1 and Gubo's automation is moot for ML (still the best choice for an own-site channel).

---------------------------------------------------------------------------
## 5. Notes on the Mercado Livre constraint (so the questions make sense)
- ML_OWN_SHIPPING.md: for T-shirts the category is ME2; the seller (or whoever packs) must print the ML label (`GET /shipment_labels`), stick it, and drop at an agency/Coleta/Place; custom shipping / seller tracking is fenced off for ME2 categories.
- LABEL_BRIDGE.md: ML label stays locked until a NF-e (CNPJ contributor) or DC-e (CPF) is attached for drop_off/cross_docking. A producer that issues the NF-e **and** returns the XML/chave to us removes one blocker; Gubo is the only one that publicly describes issuing NF-e at the seller's sale value.
- ML handling time: producers with 7 business days of production (Gubo) conflict with the ML dispatch SLA unless the listing uses the made-to-order "prazo de disponibilidade" (BRAZIL_STUDY: MANUFACTURING_TIME max 45 days; category support to be checked). Estampa Impressa claims 1-2 days.
- Fallback hub (my inference, not verified anywhere): producer ships to a Brazilian relabel point we control (family/partner), which re-packs under the ML label. Adds a hand, a day and freight; mentioned only because it is the one thing that always works with any producer.

---------------------------------------------------------------------------
## 6. Questions to ask (Portuguese, short), top 5

**1. Gubo (WhatsApp +55 11 97667-1256)**
1. Vocês aceitam pedidos de vendedor do Mercado Livre? Posso colar/enviar a etiqueta do Mercado Envios (PDF) para vocês colarem no pacote e despacharem na agência/Coleta?
2. Se não aceitam etiqueta externa: posso postar com rastreio próprio (modalidade personalizada) e vocês só me informam o código?
3. A API aceita informar o valor de venda para a NF-e (operação triangular)? Recebo o XML/chave da NF-e por webhook ou API para importar no Mercado Livre?
4. Com CPF (sem CNPJ) vale a NF-e? E com MEI?
5. Prazo de produção real (a doc diz até 7 dias úteis): tem fila prioritária ou prazo menor? Dá para despachar em 2 dias úteis?
6. A API pode criar produtos/estampas (hoje só pelo Studio)? Há previsão de MCP/importação em lote por CSV?
7. Qual o mínimo e o limite diário de pedidos pela API, e o custo de defeito/reimpressão (prazo para reclamar)?

**2. Estampa Impressa (WhatsApp (11) 94967-5638, contato@estampaimpressa.com.br)**
1. Qual a razão social e o CNPJ? Onde fica a fábrica?
2. Como funciona a integração com o Mercado Livre na prática: vocês leem meu pedido? Quem gera/cola a etiqueta do Mercado Envios? Postam na agência/Coleta?
3. Camiseta de algodão: usam DTF ou sublimação? Qual a malha/gramatura e a marca da peça lisa?
4. Tabela de preços: camiseta e moletom com 1 estampa frente (e frente+costas), com NF. Tem API/planilha para pedidos em lote?
5. Como é a NF: no valor de venda ou de custo? Mandam XML para eu importar no Mercado Livre?
6. Aceitam CPF? Cobram no pedido (carteira) ou depois? Posso fazer 1 pedido-teste?

**3. Montink (via Bling)**
1. A integração "marketplaces via Bling" importa pedidos do Mercado Livre? Quem imprime a etiqueta do Mercado Envios e quem posta?
2. Posso enviar a etiqueta ME2 em PDF para colarem no pacote? A Montink usa a infraestrutura da Dimona, que recusa etiqueta de terceiros: há exceção?
3. Qual plano inclui o ERP Bling e os marketplaces? Preço de custo (não de venda) da camiseta e do moletom com 1 estampa?
4. NF no valor de venda: precisa de CNPJ + certificado + Bling? O XML volta para o Bling/ML?
5. Existe API ou webhook oficial para pedidos?

**4. Dimona / Dropsimples (api@dimona.com.br)**
1. O endpoint `POST /order/{id}/shippingLabel` aceita uma etiqueta externa (PDF do Mercado Envios) para pedidos de vendedor do Mercado Livre? É permitido para conta CPF?
2. Podem abrir exceção à política de marketplace (artigo "Política de Marketplace") para ME2 com etiqueta do ML?
3. A NF para conta CPF no Mercado Livre: DC-e ou NF de vocês? Retornam o XML?
4. Webhook: política de reenvio e assinatura? Existe sandbox e limite de requisições?
5. Há tabela de frete e prazo por CEP e custo da etiqueta de vocês quando o frete é pelo ML?

**5. Estamparia manual (ex.: Camisetas Rápido, WhatsApp +55 11 2589-5524)**
1. Fazem DTF/DTG de 1 peça para revenda no Mercado Livre, sem minimo, sem marca de vocês?
2. Aceitam receber a etiqueta do Mercado Envios (PDF), colar e levar à agência/Coleta no mesmo dia?
3. Preço por camiseta (algodão 30.1 ou 100% algodão) e moletom com 1 estampa; desconto para volume recorrente?
4. Aceitam receber pedidos por e-mail/planilha/WhatsApp com a arte em PNG 300 dpi, e responder com confirmação e código de rastreio?
5. Emitem NF-e? Reimprimem em caso de defeito? Qual o prazo de produção?

---------------------------------------------------------------------------
## 7. What to do next (cost-free order)
1. Send Q1 to Gubo and Q2 to Estampa Impressa and the Dimona e-mail (same day, no spend). Their answers re-rank section 4.
2. Create a Gubo account (free), generate a **test** key and run the Gubo quick start in test mode (no orders, no balance) to measure `POST /fretes/cotacoes` for real CEPs (SP-RJ-Manaus) and check what the order object returns about NF/label. This needs the owner's account (not created here).
3. If nobody accepts the ML label: shortlist 3 DTF/DTG estamparias in SP and test one real order end to end with a small ML test listing, using ME2 drop-off.

---------------------------------------------------------------------------
## 8. Sources (all fetched 2026-11-07 unless noted)
- Gubo: https://gubo.com.br/precos, /integracoes, /como-funciona, /contato, /sitemap.xml, https://gubo.com.br/docs-api/{visao-geral,criar-pedido,fretes,vinculos,webhooks,producao,pedidos,convencoes,erros,acompanhar,ia,changelog} (raw: prod/gubo, prod2, prod3)
- Estampa Impressa: https://www.estampaimpressa.com.br/ and /como-funciona-o-print-on-demand/ (raw: prod/estampaimpressa)
- Montink: https://sou.montink.com/comparativo-planos-montink, https://montink.com/mercado-livre (tenant store), https://montink.com/dropshipping (raw: prod/montink)
- Uma Penca: https://umapenca.com/, https://umapenca.com/central-de-ajuda/, https://www.reclameaqui.com.br/empresa/uma-penca/ (raw: prod/umapenca, prod2)
- YouDraw: https://youdraw.com.br/, https://youdraw.com.br/planos; Nuvemshop app page https://www.nuvemshop.com.br/loja-aplicativos-nuvem/youdraw (R$99/mo plan wording, WebFetch)
- HotPrinti: https://hotprinti.com.br/, /plano_precos/, /contato/
- Camisetas Rápido: https://camisetasrapido.com.br/ and 8 subpages
- Cloudprinter: https://cloudprinter.com/ (Print API, Zapier)
- Directory pages read for discovery (third party, UNVERIFIED): https://ecommercenapratica.com/blog/plataformas-de-print-on-demand/, https://blog.fornecedoresdeconfianca.com.br/fornecedores-para-dropshipping-de-roupas-opcoes-confiaveis/, https://dodropshipping.com/best-dropshipping-suppliers-in-brazil/, https://www.printkk.com/pt/blog/articles/print-on-demand-brazil, https://blog.umapenca.com/melhores-plataformas-de-print-on-demand-no-brasil/ (self-interested), https://startups.com.br/negocios/varejo/com-uma-penca-chico-rei-aposta-em-tech-e-cresce-no-b2b/, https://www.nuvemshop.com.br/loja-aplicativos-nuvem/categorias/dropshipping
- Blocked (not bypassed): Reclame Aqui (403 challenge) for most companies, Colab55 inner pages (403), camisadimona.com.br (429), estampaja.com.br (429), montinkhelp.zendesk.com (Cloudflare), vegascamisetas.com (robots), Reclame Aqui via WebFetch (client error).

## 3.2 Gubo test-mode results (VERIFIED 2026-11-07, raw: docs/brazil_data/gubo/*.json)
- Real API base: https://api.gubo.com.br/v1 (docs show a placeholder host). Test key works; header Gubo-Modo: teste.
- Products must exist in the Studio (API cannot create). Studio editor runs in a same-origin iframe with plain inputs (#arquivo file upload, #nome-produto, #sku-produto, #preco-revenda), so browser automation (Claude in Chrome: move #arquivo to top document, file_upload, drag art onto shirt, Revisar e cadastrar, Cadastrar produto) works. Test product CAV01 (Camiseta Padrão, black, Cavalier white-ink front 30.5x31.5 cm).
- Cost per piece shown by Studio/API: R$54.53 card (R$51.80 Pix), XG/XGG R$62.95. Only the colour selected is released (PRET); others report cor_nao_liberada.
- Freight quote (1 tee, 190 g, final prices): SP pax R$12.82 transport 1 bd / total 8 bd; Rio jet R$16.39 / 10 bd; Porto Alegre jet R$16.39 / 12 bd; Manaus imile R$32.33 / 22 bd (loggi R$61.42 / 17 bd; sedex R$106.22 / 11 bd). Carriers: Olist Envios (correios PAC/SEDEX, jet, jadlog, loggi, gfl, pax, imile).
- Order (test): POST /pedidos/por-variante -> aguardando_pagamento; POST /pedidos/{id}/pagar with valor_esperado_centavos -> 202, pago in ~5 s; /teste/pedidos/{id}/avancar -> em_producao, enviado (rastreio TESTE+9 digits, url_rastreio null), entregue. Order object has NO field for invoice/NF-e or label; sale value for the NF-e comes from the product's "Preço de revenda" set in the Studio (field not in order API). valor_venda_centavos does not exist.
- Wallet test debit R$67.35 (item 54.53 + freight 12.82). 

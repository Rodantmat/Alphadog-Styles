# Brazil arm - study (Nov 7 2026). V = verified from a page we fetched, U = unverified. Prices BRL. Owner decides after reading.

## Verdict in one paragraph
Full automation is feasible: a Brazil-based producer with CPF-only access, API and invoicing exists (Dimona/Dropsimples); Mercado Livre has webhooks for orders/shipments/messages/invoices. Blockers that need the owner: (1) a Brazilian seller of record (mother) with CPF and, realistically, a MEI/CNPJ - TikTok Shop BR requires CNPJ, Shopee forces CNPJ after R$81k or 90 days, marketplaces expect NF-e; (2) unit economics: Dimona cost for a front+back tee R$54.90-67.90 vs Brazilian market tee prices R$50-100 (A Gazeta, Ponto Frio R$63.90) - only works with premium pricing (see below); (3) several numbers are still U and must be pulled from accounts/APIs before any commitment.

## 1. Production + fulfilment (the key piece)
| Option | Made in BR | API | Cost (V = Dimona catalog PDF, undated) | Verdict |
|---|---|---|---|---|
| Dimona / Dropsimples | Yes (V) | Yes: API V2 with key, freight quote by CEP; spreadsheet upload; Nuvemshop/Shopify/Woo/Loja Integrada connectors (V). Endpoints/webhooks U | tee Classic R$36.90 +R$18 2nd print = R$54.90 front+back; Prime tee R$49.90 -> R$67.90; hoodie blusao R$97 -> R$115; canguru R$127 -> R$145; tank R$41.90 -> R$59.90; cap R$72.90 (Prime) or R$33, 1 print DTF; no monthly fee, CPF enough, Dimona issues NF (cost value if no CNPJ) (V). Brand label optional extra, price U. Shipping cost/time U. Print areas 29x42 cm front/back tee (V) | PRIMARY candidate |
| Montink (Dimona infrastructure) | Yes | WooCommerce plugin only, no public docs (U) | R$129/149/249 per month (V) | backup |
| Gelato | Yes, front/back only, NO neck/inner label print (V) | Yes: quote, create order, webhooks, BRL settlement (V); CPF/CNPJ mandatory for BR recipients | U (need API quote for 3001 tee, hoodie) | second route to test |
| Printful | Partial: Brazil partner facility for selected products (V) | Yes v2 (orders, rates, webhooks) needs token (V); our probe got 401 | U (USD only on page) | test with token |
| Gooten | 2022 post says 3001/6004 made in BR (V old) | Yes (not read) | U | check |
| Printify | NO Brazil provider (our probe, V). Ship to BR from abroad: tee first $10.39, extra $4, 10 days handling | Yes | n/a | out as producer |
Imports: since 12 May 2026 federal duty 0% up to US$50 on Remessa Conforme platforms but ICMS 17-20% still applies; above US$50: 60% less US$30 (V). Delivery from abroad 10-30 business days (Gooten, U-ish). Not recommended for apparel at our prices.

## 2. Sales channels (V = official page)
- Mercado Livre: best first channel. CPF can register (secondary source). Webhooks: items, orders_v2, shipments, messages, questions, invoices, claims; endpoint must answer HTTP 200 in 500 ms, retries ~1 h (V official). Listing POST /items, shipments GET /shipments/{id}, billing GET /orders/{id}/billing_info (V). Made-to-order "prazo de disponibilidade" field exists; MAX days U. Fees: Classic 10-14%, Premium 15-19%, fixed fee under R$79 up to R$6.75 (secondary, exact apparel % U). NF-e must be linked to the order before the label.
- Shopee BR: 20% + R$4.50 up to R$79.99; 14% + R$16-26 above (secondary). CPF must become CNPJ at R$81k/12 months or after 90 days of active sales. Open Platform API exists, coverage U.
- Amazon BR: CPF or CNPJ (V official); individual R$2 per item; professional free 12 months then R$19/mo; apparel 14% (min R$2) (V). SP-API Brazil coverage U.
- TikTok Shop BR: CNPJ required (MEI accepted), CPF no. Fees from 15 Jul 2026: under R$50 10%+R$4; R$50+ 6%+R$6. API for BR U.
- Magalu, Shein: CNPJ, skip. Instagram/Facebook: no native checkout in BR (traffic only).
- Own store: Nuvemshop R$0/69/164/449 per month, API (products, orders, webhooks, shipping carrier, 40-request bucket) (V); free-plan API access U. Alternative: our own Cloudflare worker store (needs BR payments, shipping API, NF-e).

## 3. Payments / shipping / tax / invoices
- Pix + card options (V vendor pages): Mercado Pago Pix 0.99%, card 4.98% instant / 4.49% 14d / 3.98% 30d; Asaas Pix R$0.79-1.59 flat, card R$0.49 + 2.99% (1x), PF can receive Pix; Efi Pix 1.19%, card 3.49%; Pagar.me Pix 0.99%, card 4.19%; Stripe BR Pix 1.19%, card 3.99%+R$0.39. API/webhook support for each U (assumed common, must check docs).
- Shipping APIs: Correios API (needs contract + cartao de postagem; no webhooks mentioned), Melhor Envio (quote/buy/label/tracking; webhooks section exists, CPF/CNPJ and NF requirements U). Rate examples SP-RJ / SP-Manaus U (run Melhor Envio calculator).
- MEI 2026: limit R$81,000/yr (R$6,750/mo); DAS = R$81.05 INSS + R$1 ICMS (commerce) or R$5 ISS (services), due 20th (V Receita). MEI exempt from NF to individual consumers, required for CNPJ buyers. Whether a MEI can legally carry "made-to-order printed apparel online" is U -> accountant. Listed CNAEs: 4781-4/00 apparel retail, 1340-5/01 garment printer, 1813-0/99 screen printing, 1412-6/01 seamstress (V Receita annex XI).
- NF-e APIs: Focus NFe Solo R$94.90/mo (100 docs); Retail R$62.90 (500 NFC-e + 100 NF-e); NFE.io R$190 (250 docs). ERP/order hub: Bling Cobalto R$60/mo (200 orders, API in all plans), Titanio R$120/200/450 (secondary).
- Trademark INPI reduced rate (PF/MEI/ME) R$440 total (R$142 + R$298) (secondary, Oct 2025); official table U.
- Money to the US: IOF 1.10% same-ownership transfer / 3.5% personal remittance (broker page); structure (pro-labore, distribution, contractor invoice) needs a Brazilian accountant. CDC 7-day withdrawal, LGPD: U (well known, not sourced).

## 4. Demand and design (Petlove PetCenso 2025, Cobasi Censo Pet 2025)
Top breeds: SRD/vira-lata 26% (Cobasi 13.4%), Shih Tzu 17% (15.7%), Yorkshire 6%, Spitz Alemao/Pomeranian 5% (5.6%), Lhasa 3%, Golden 3%, Pinscher 3%, Dachshund 2%, Pug 2%, Maltes 2%; Frances bulldog, Labrador, Poodle, Chihuahua, Border Collie, Husky, Pit Bull also popular (no numbers). Our US ban list (yorkshire, pomeranian, shih tzu, pug, maltese...) is about black cards awaiting approval - those ARE the Brazilian best sellers, so their approval matters for Brazil. Need new: generic vira-lata (caramelo), Lhasa, Pinscher, Spitz Alemao (Lulu da Pomerania).
Seasonality 2026: Maes 10 May, Namorados 12 Jun, Pais 9 Aug, Dia do Vira-Lata 31 Jul, Dia Mundial do Cachorro 26 Aug, Black Friday 27 Nov, Natal 25 Dec. Sizes P/M/G/GG (US L = G, XL = GG); give cm measurements, baby-look option. Instagram 130M+, Facebook 120M, TikTok ~100M, Pinterest ~73M, Kwai ~45M (blog citing DataReportal 2025). Pet market R$77.96B 2025 (V GlobalPETS). Mercado Livre/Shopee tee prices U (pages blocked); ranges seen R$49.90-100 (Gazeta), R$63.90 (Ponto Frio).

## 5. Unit economics (MY ARITHMETIC on partly unverified inputs - not a quote)
Premium Prime tee front+back cost R$67.90 + shipping to buyer (U, Dimona/Melhor Envio) + marketplace fee ~14-19% (Mercado Livre U exact) + payment fees. At R$149.90 sale: fee ~R$21-28, leaving ~R$54-61 before shipping; hoodie canguru cost R$145 needs price roughly R$279+. At R$89.90 a tee loses money. Conclusion: the exclusive/premium positioning must carry R$140-170 tees; unknown until shipping cost is known.

## 6. What the owner must provide / decide
1. Mother as seller of record: agrees; CPF, gov.br access, bank account in her name, smartphone for verification; open MEI/ME (accountant confirms CNAE).
2. Money route to the US (accountant).
3. Accept premium price points above.
4. Approve creating a Dimona account (free, no monthly fee) and a Gelato/Printful token for quotes.

## 7. Proposed automation plan (all via API/bridge, same model as the US arm)
Phase 0 (verification, no spend): create Dimona API key -> pull docs, exact freight by CEP, label price, delivery days, minimum order, webhook/CSV status; Gelato quote for 3001 tee + hoodie to SP/RJ/Manaus; Printful token quote; Melhor Envio calculator; Mercado Livre app registration + max made-to-order days + exact apparel fee via the seller fee calculator (browser); accountant call (MEI CNAE, IOF/remittance, NF).
Phase 1: Mercado Livre listings (ML API) + queue-first webhook receiver on Cloudflare worker -> orders -> Dimona API order -> tracking back to ML; Bling or Focus NFe for NF-e; support assistant in pt-BR (same hourly task pattern, new mailboxes suporte@/personalizado@ - domain needed, e.g. alphadogstyles.com.br U).
Phase 2: own store (Nuvemshop API or our worker with Asaas/Mercado Pago Pix) + Shopee/Amazon BR; TikTok Shop after MEI.
Phase 3: pt-BR social (Buffer: Instagram, TikTok, Facebook, Pinterest; Kwai U), breed set per section 4, calendar campaigns (Black Friday Nov 27 is too soon; target Dia das Maes 10 May 2027 and Dia do Vira-Lata 31 Jul).
Colombia later: Mercado Libre CO (8M+ users, 73k sellers V), POD provider U.

---
# Update Nov 7 (Phase 0 research round 2). Sources: 4 research agents. ML and Dimona official pages were unreadable from the sandbox (proxy/robots/CAPTCHA); ML fee numbers below are SECONDARY (blogs, Oct 2026) unless marked.

## A. ML <-> producer link (what is known)
V (ML dev docs): shipping modes drop_off / xd_drop_off / cross_docking / self_service(Flex) / fulfillment; GET /shipment_labels (pdf|zpl2) only once shipment is ready_to_ship; MANUFACTURING_TIME max 45 days (category support must be checked via /categories/{id}/sale_terms; not for Flex/Full items); GET /orders/{id}/billing_info gives buyer CPF/CNPJ; POST /packs/{id}/fiscal_documents (PDF/XML); webhooks orders_v2, shipments, messages, claims, invoices, items, questions (200 in 500 ms); OAuth with offline_access, refresh token rotates every time; return flow via /post-purchase/v2/claims/{id}/returns.
V (Dimona support/blog): API key, create_order/get_order/tracking via API (Perl client), order payload takes design+mock image URLs, address, shipping_speed; integrations listed: Montink, Loja Integrada, Nuvemshop, Shopify, Woo, spreadsheet. NO Mercado Livre connector found for Dimona (Montink page lists ML + TikTok Shop).
UNVERIFIED BLOCKERS: (1) can Dimona ship under an ML-generated label / does ML accept a third-party shipment (label carries ML sender); (2) ML handling-time rule vs production time; (3) whether CPF sellers get ME2/drop_off; (4) whether ML requires NF-e from CPF sellers and accepts Dimona cost-value NF; (5) Dimona API base URL, auth header, freight endpoint, artwork specs, webhooks, lead time, freight prices. => needs ONE real test listing/order or direct Dimona/ML answer. Fully automated flow design: ML webhook -> worker -> Dimona create_order -> poll tracking -> update ML shipment/ send tracking.

## B. Fees (BRL)
ML (secondary): commission moda Classico ~14%, Premium ~19% (one blog says Premium 13-16%); no monthly fee; free shipping mandatory from R$79; fixed fee under R$79 since 2 Mar 2026 ~R$5.65-8.75 by price/weight (sources conflict, ~R$8 for a tee at R$49-78.99); seller shipping share (ML logistics, up to 0.3 kg): under 19: 5.65; 19-48.99: 6.55; 49-78.99: 7.75; 79-99.99: 12.35; 100-119.99: 14.35; 120-149.99: 16.45; 150-199.99: 18.45; 200+: 20.95 (0.5-1 kg 200+: 23.65; 1-2 kg 200+: 24.65). Reputation thermometer starts after 10 sales; green thresholds complaints<=2%, cancellations<=1.5%, late<=10% (last 60 sales).
Shopee (secondary): 20% + R$4 up to R$79.99; 14% + R$16-26 above; CPF surcharge conflicting (R$3 or R$7). CPF limit ~R$81k/yr. Elo7 closed (May 2026, one source). Amazon BR apparel ~14%, individual R$2/item.
Own site payments (vendor pages): Mercado Pago Pix 0.99%, card 4.98% instant / 4.48% 14d / 2.95% 30d; Asaas Pix R$1.59 (promo 0.79), card R$0.49+2.99%; Efi Pix 1.19%, card 3.49%, accepts CPF (Efi Pro); Stripe BR card 3.99%+R$0.39, CPF sole prop allowed. Webhook support on card side not confirmed for any.
Fixed monthly: MEI DAS R$82.05 (commerce) V; Focus NFe Solo R$94.90 (100 docs) V or Asaas NF-e R$0.49/note; domain .com.br ~R$40/yr; Cloudflare/GitHub already paid; Nuvemshop optional R$0/69/164/449; Montink R$126.60-149/mo if used; ML ads suggested R$20-50/day (blog guidance, optional). Trademark INPI MEI price R$440 (+ same at registration step per table). IOF 3.5% on personal remittance (Safra, 2026), 1.10% investments; structure needs accountant.
Taxes: MEI limit R$81k; over by <=20% pay difference, >20% retroactive to Simples. CPF habitual commerce vs carne-leao: UNVERIFIED, accountant.

## C. Producer cost (Dimona catalog, ~2024) 
Tee Classic R$36.90, Quality 41.90, Prime 49.90, Oversized 83.90, Pima 94.90; hoodie blusao 97, canguru 127, zip 127; extra print +R$18; so front+back tee Classic ~R$54.90, Prime ~R$67.90, canguru front+back ~R$145 (my arithmetic). Freight, lead time, label price, returns: UNVERIFIED. Gelato: API quote exists (v4 orders:quote), BR prices unknown. Printful: delivery to BR 10-25 business days, production 2-5, tee from $8.50, hoodie from $18.72; CPF mandatory. Montink: ~4 business days production.

## D. Unit economics (my arithmetic from the secondary/V figures above; before Dimona freight, ads, DAS)
| Case | Price | Fees | Product | Left |
|---|---|---|---|---|
| ML Classic, tee Classic print, R$149.90 | 149.90 | 14% 20.99 + ship share 16.45 | 54.90 | ~57.6 |
| ML Premium, tee Prime print, R$149.90 | 149.90 | 19% 28.48 + 16.45 | 67.90 | ~37.1 |
| ML Classic, R$89.90 tee Classic | 89.90 | 12.59 + 12.35 | 54.90 | ~10.1 |
| ML, R$69.90 tee Classic (under 79) | 69.90 | 9.79 + fixed ~8 | 54.90 | ~-2.8 (buyer pays ship) |
| Own site Pix, tee Prime R$149.90 | 149.90 | 1.48 | 67.90 | ~80.5 (buyer pays ship) |
| ML Premium, hoodie canguru f+b R$279 | 279 | 53.01 + 24.65 | 145 | ~56.3 |
Conclusion: ML only works above ~R$120; own site carries the highest margin; R$79 is the key price line.

## E. 24-month units (ESTIMATES, unanchored: no verified sales counts; ML blocked automated reading and shows CAPTCHA) 
Total units: conservative 380, base 1,164, optimistic 3,763 (ML + own site). Month table in agent output; shape: base ML 4/mo -> 35 (m12) -> 70 (m24), own site 1 -> 10 -> 25. Illustrative profit at R$37-80 left per unit: conservative R$14-30k, base R$43-93k, optimistic R$139-300k over 24 months, before ads/DAS/freight. Base year-2 turnover ~R$129k at R$150 avg exceeds the MEI R$81k limit -> ME needed in year 2. NEEDS recalibration with real 'vendidos' data (Nubimetrics-type tool, or official ML API with seller credentials, or owner pastes result pages).

## F. Needed to close all questions before creating accounts
1. Approve browser access to mercadolivre.com.br, dimona.com.br / camisadimona.com.br / api.camisadimona.com.br (CAPTCHA on ML may need the owner once), or paste those pages.
2. Ask Dimona (suporte) in writing: ship under external ML label? freight table by CEP, lead time, returns, NF for CPF sellers, API webhooks.
3. ML: one real CPF test listing (no sale) to see which shipping modes and NF rules appear; sale_terms for the apparel categories.
4. Accountant: CPF vs MEI, CNAE, remittance.

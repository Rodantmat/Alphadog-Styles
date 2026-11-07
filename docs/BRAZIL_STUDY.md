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

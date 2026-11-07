# Montink x Mercado Livre: how it works and how far it can be automated

Study date: 2026-11-07 (all "fetched" dates below are this day). Method: public pages only, fetched from a GitHub Actions runner (`scripts/brazil/probe.py` tasks `montink` ... `montink10`, workflow `brazil-probe.yml`), plus web search. No accounts, no logins, no tokens, no ordering. Raw text of every page cited is in `docs/brazil_data/montink/` (help-center mirror in `montink/sak/`, API docs in `montink/api_docs_full.html`, third-party code in `montink/gh_src/`, `montink/gh_ext/`).

Labels: **VERIFIED** = read in the primary text, with URL and the page's own "Atualizado em" date (or fetch date). **UNVERIFIED** = inference, third-party claim, or needs a logged-in account.

This file **corrects** ALTERNATIVES.md section 3.1 and LABEL_BRIDGE.md 3.7. Those said "no public API" and "no Mercado Livre integration". Both were wrong or stale. The page they used (`sou.montink.com/integracoes-montink`) is an old marketing list; the real help center lists both (section 1).

---------------------------------------------------------------------------
## 0. Bottom line

1. **Montink has an official, live Mercado Livre integration** (help article "Agora é oficial", updated 2026-09-03, about 2 months old). It lists products in the seller's own ML account, imports ML orders into Montink automatically, and the supplier (Dimona infrastructure, Duque de Caxias RJ) produces and ships with **Mercado Envios**. Freight is paid through ML, not again to Montink. VERIFIED.
2. **Montink also has a public partner API** (`https://api.montink.com`, header `Authorizationtoken`, public docs at `admin.montink.com/apiMontink/docs` and Postman). It can list products, quote freight, **create orders**, read order status and register a **webhook**. VERIFIED. It cannot create products, upload designs, or push a label. VERIFIED by absence in the doc (endpoint list in section 3).
3. **Hard limits of the ML integration today**: only **Camiseta Quality (white or black only), Ecobag and Caneca** can be exported. No hoodie, no other tee colours, no Pet line. VERIFIED (same article).
4. **The prior blocker (supplier refuses ML labels) is bypassed by design**, not solved by us: the seller registers Montink's distribution center as the ML "Endereço de Envios", so ML generates the label for that address and the factory ships it. How the label PDF physically reaches the factory is not stated: UNVERIFIED (almost certainly Montink's authorized ML app pulling it).
5. **What is NOT automatic**: creating each design in the Montink editor, clicking Export per product, topping up the Montink wallet by Pix, getting Mercado Envios enabled for the account, and (probably) the fiscal document. Details in section 8.
6. **Verdict**: ML order -> production -> shipping -> ML tracking is **automated end to end by Montink for the 3 supported products, with a handful of manual or unconfirmed steps** (section 8). It is not a "fully hands-off" pipeline until the wallet funding and the NF/DC-e question are settled. A custom pipeline of our own (ML API + Montink API) is technically possible for ordering but **cannot ship under the ML label** (no label input in the API), so it is not a path for ME2 listings.

---------------------------------------------------------------------------
## 1. Montink's own pages: what exists

Primary help center (Zendesk `montinkhelp.zendesk.com`) answers 403 Cloudflare challenge to the runner and the Wayback copy stops at 2025, so I used the **official mirror `montink.sak.com.br`** ("Central de Ajuda Montink", the same articles, 150 pages crawled; linked from `admin.montink.com/apiMontink/docs`). VERIFIED.

| Topic | Source (all fetched 2026-11-07) | Page date |
|---|---|---|
| ML integration | https://montink.sak.com.br/integracao-com-mercado-livre-tudo-o-que-voce-precisa-saber | 2026-09-03 |
| Order + payment flow for marketplaces | https://montink.sak.com.br/fluxo-de-pedido-e-pagamento-montink-marketplaces | 2026-09-09 |
| Integrations list (includes "Mercado Livre" and "API Montink") | https://montink.sak.com.br/integracoes-disponiveis-na-plataforma | 2026-05-12 |
| API (help article) | https://montink.sak.com.br/integracao-da-montink-via-api | 2026-05-12 |
| TikTok Shop integration | https://montink.sak.com.br/como-integrar-a-montink-com-tiktok-shop-guia-rapido and `.../tik-tok-shop-por-que-e-necessario-emitir-a-nota-fiscal-do-pedido` | 2026-09-03 / 2026-05-12 |
| Fees | https://montink.sak.com.br/quais-sao-as-taxas-cobradas-pela-montink ; terms https://montink.sak.com.br/termos-e-condicoes-da-montink | 2026-05-12 |
| NF | https://montink.sak.com.br/como-e-emitida-a-nota-fiscal-de-um-pedido | 2026-06-03 |
| Order statuses | https://montink.sak.com.br/o-que-significa-o-status-do-meu-pedido | 2026-05-13 |
| Delivery times | https://montink.sak.com.br/tudo-sobre-prazos-de-entrega-como-funciona-interferencias-e-solucoes | 2026-05-14 |
| Returns / defects | https://montink.sak.com.br/trocas-e-devolucoes-regras-gerais-e-responsabilidades | 2026-05-12 |
| Stock-outs | https://montink.sak.com.br/produtos-sem-estoque-na-montink | 2026-10-30 |
| Print areas | https://montink.sak.com.br/area-maxima-de-impressao-e-tecnica-utilizada-na-impressao-por-produto | 2026-07-27 |
| Official catalog (CNPJ 22.733.912/0001-05) | https://sou.montink.com/catalogo/ | 2026 |

Montink's own blog post on TikTok Shop (https://blog.montink.com/tiktok-shop-no-brasil/, about 1 year old) said the TikTok integration was "em breve"; the 2026-09-03 guide shows it is now live. Same pattern for ML. Montink's blog has no ML post and even recommends Printify for ML (https://blog.montink.com/print-on-demand-produtos-pets/), so the blog is not a reliable signal; the help center is.

---------------------------------------------------------------------------
## 2. How the ML integration works (VERIFIED unless marked)

Source: ML integration article (2026-09-03) and marketplaces flow article (2026-09-09).

**Setup**
1. In the Montink dashboard: Apps e Integrações -> Mercado Livre -> "Sim, já tenho uma loja" -> country Brasil (OAuth link of the ML account).
2. In ML, add Montink's distribution center as the **shipping address** ("Meu Perfil - Endereços", type Endereço de Envios): Rodovia Santos-Dumont, 4791 Arm 108 BL 02, Caxias Park, CEP 25251-460, Duque de Caxias RJ (the TikTok guide names the entity: "Dimona e Malhas LTDA"). The seller's own address goes in as the **return address**. This is how the ML label is generated "correctly".
3. **Mercado Envios is not enabled automatically.** For "Moda" listings with variations created through an API, ML decides after internal review (verified account, minimum reputation, clean shipping history, manual support review). Montink tells the seller to open an ML support ticket asking for review. ML gives no deadline.

**Listing (Montink creates the ML listing in the seller's account)**
- Products tab -> My products -> the product (ML icon appears if eligible) -> Integrações -> Exportar -> set "taxa adicional" -> accept ML policies -> Exportar. Approval "up to 2 hours".
- Eligible: **Camiseta Quality (white or black), Ecobag, Caneca** only ("primeira versão").
- Image rules: pure white background (#FFFFFF), product centered at about 80 percent, no text, seals, prices, watermarks or borders, 1200x1200 recommended (500x500 minimum). **Montink's default mockups may be rejected by ML; the seller must create custom mockups.**
- Price: Montink product price (cost + profit configured in Montink) plus the "taxa adicional" you set, meant to cover ML sale fee (up to 20 percent), ML fixed cost (R$ 7 under R$ 79) and freight (Montink says simulated up to R$ 50). Example in the article: R$ 89.99 with R$ 30 profit, plus R$ 40 additional = listing at R$ 129.99. After export the seller can edit title, description and price inside ML.

**Order flow (from the article)**
1. Buyer pays at ML checkout; the money goes to the seller's ML/Mercado Pago account (Montink does not process it).
2. The order is imported automatically into Montink (Pedidos -> filtro **Pedidos externos**); if missing, a manual sync button exists in Adicionar Apps -> Configurar.
3. The seller must **pay the production cost** (wallet balance or a Pix QR) before anything is produced. "O pedido só entra em produção depois do pagamento do custo". Freight is not charged again by Montink ("já está incluso na venda realizada pelo ML").
4. Optional **automatic payment**: Configurações -> Pagamentos -> "Cobrança automática de pedidos integrações" + enough wallet balance. Then every integrated order is paid from the wallet and released to production with no click.
5. Montink supplier produces and ships directly to the buyer. Montink tracks status **only until production**; "posteriormente a este ponto, é obrigatório acompanhar o envio através do Mercado Livre" (ML's own tracking, from the ME2 label).
6. Not stated anywhere in the ML article: who issues the fiscal document and how the ML `invoice_pending` lock is released (see section 6).

**Which ML shipping mode**: the article says "Mercado Envios" and a distribution-center ship-from address, i.e. ME2 with the ML label; it does not say drop-off vs Coleta (the dropoff/Coleta choice is ML's, not Montink's). UNVERIFIED which sub-mode is used. Who pays shipping: the seller, through ML's deduction from the sale (VERIFIED by "frete já incluso na venda" and the taxa-adicional explanation); the buyer sees ML's price/freight rules.

---------------------------------------------------------------------------
## 3. The Montink partner API (this is new vs the earlier docs)

Primary: https://admin.montink.com/apiMontink/docs (public, no login, 200, fetched 2026-11-07, `montink/api_docs_full.html`). Postman: https://documenter.getpostman.com/view/32162527/2sAYkGJyWE ("API Pública Montink", an older shape: required `value_total`, saldo-only payment). Help article: https://montink.sak.com.br/integracao-da-montink-via-api (2026-05-12). Independent third-party code that matches the docs: https://github.com/noxsulivan/tshirtness-montink (WooCommerce plugin, created 2026-08-23, 0 stars, does catalog sync, freight quote, create_order and webhook; it calls `https://api.montink.com` with header `Authorizationtoken`) and https://github.com/brunoapolinariodev/montink_erp (Go client for `/orders`, `/order/{id}`).

Base `https://api.montink.com`. Auth: header `Authorizationtoken`; token generated in Dashboard -> Adicionar Apps -> API Montink -> Conectar -> Gerar token; valid 1 year. The docs recommend "supervisão de um desenvolvedor".

| Endpoint | Does |
|---|---|
| `GET /products` (`pga`, `pp`, `produto`, `categoria`, `produtoBase`, `colecao`) | Enabled products of the **token's store** only (id, `preco_final`, images, categories) |
| `GET /product/{id}` | Variations with stock (`variacoesEstoque`), images, print reference |
| `GET /calculate_shipping/{CEP}/{qty}` | `shipping_options[]` with `delivery_method_id`, `name` (examples in docs: J&T Express, Correios PAC, Correios Sedex), `value`, `business_days`, carrier CNPJ |
| `POST /create_cart` | Empty cart + token (docs say may return 404 in production: "ainda não está publicado nesse ambiente"); `create_order` works without it |
| `POST /create_order` | Required: customer name, email, CPF/CNPJ, phone, `payment_method` (pix, saldo or boleto), `address{zipcode, street, number, neighborhood, city, state}`, `products[]{product_id, quantity, sku or var1/var2/var3, price}`. Optional: `external_order_id` (unique per store), `shipping_id`. Returns `id`, `token`, `tracking_url`. Order lands in **Pedidos Externos** with status `waiting` |
| `GET /orders` | Order list (period/status filters), includes `custo`, `lojista_lucro` |
| `GET /order/{id}` | Full order, `linkRastreio`, `plataforma_pedido_id` (= your `external_order_id`) |
| `POST /webhook` (`webhook_url`) | Montink POSTs the order payload (`order.status`) to your URL, header `Authorizationtoken` = your token, when the supplier updates status |

Not in the API (VERIFIED by absence in the docs): create/edit products, upload artwork, export to ML, pay/charge wallet, cancel order, upload a carrier label, tracking push, NF. No Zapier/Make/Pipedream connector exists: zapier.com/apps/montink and make.com/integrations/montink return 404 (runner, 2026-11-07). No MCP server found. Two other repos found by GitHub search are job-test projects, not integrations.

Notes that matter for us:
- The product must already exist in the token's Montink store (so every dog-breed design must first be created in the Montink editor by hand).
- `create_order` is "import an external order"; the order stays unpaid until cost is paid. The older Postman text says orders are paid from wallet balance; the current docs also allow pix/boleto. Whether the "cobrança automática" switch also pays orders created by **API** (not by the ML app): UNVERIFIED.
- Freight chosen by `shipping_id` means Montink/the supplier ships with **its own** carriers and generates its **own** tracking. There is no field to supply an ML label. So for an ME2 listing this API cannot replace the integration.

---------------------------------------------------------------------------
## 4. Costs

**Platform plan** (needed even for the integration: "é necessário ter um plano na Montink" per the Nuvemshop article; for ML specifically UNVERIFIED but the app lives in the store dashboard):
- https://sou.montink.com/printiplus/ (2026-11-07): Start R$ 129, Essencial R$ 149, Escalada R$ 249 per month; 7 days free (page also says 6 days on another line). Same page lower down: "Montink Full" R$ 147/month or R$ 997/year (R$ 1,764 struck through). Nuvemshop listing (2026-11-07): from R$ 126.60/month annual, R$ 149 monthly, 5 percent off with Pix. ecommercenapratica (third party): lifetime R$ 8,997. **The pages disagree**; I would treat R$ 126-149/month as the entry price and confirm at signup. Terms: plans are paid in advance, auto-renew; refund only within **7 calendar days** (https://montink.sak.com.br/cancelamento-de-planos-e-reembolsos, 2026-05-29).
- Which plan unlocks the ML app: UNVERIFIED.

**Per-order fee** (terms, 2026-05-12): own-store orders pay R$ 2 per item + 10 percent of the supplier cost table + 5 percent of the seller's profit; **integration orders (incl. ML) pay only supplier cost + 10 percent + R$ 2, already inside the displayed cost**, no 5 percent profit fee. No fee per visit, product, or image. Withdrawal from the Montink wallet: R$ 3 per withdrawal, R$ 8 minimum; CPF accounts limited to R$ 1,900 per month of withdrawals (CNPJ unlimited but must configure NF). These withdrawal limits only matter for Montink-store profit; ML sales proceeds land in the ML account.

**Per-unit production cost** (official catalog https://sou.montink.com/catalogo/, 2026-11-07, `montink/page_sou_montink_com_catalogo_.txt`; the page does not say whether the price is cost or retail, but it is the CNPJ-owned catalog and the 5 percent profit fee does not apply to integration orders, so I read it as the cost base. **UNVERIFIED as exact cost**):

| Item | Catalog price |
|---|---|
| T-Shirt Quality (the ML-eligible tee) | **R$ 48.20** |
| T-Shirt Classic | R$ 43.25 |
| T-Shirt Prime | R$ 58.54 |
| Baby Long Quality | R$ 48.20 |
| T-Shirt Estonada | R$ 64.15 |
| Quality Infantil | R$ 43.25 |
| Moletom Prime Fechado / Canguru / Zíper | R$ 122.89 / 172.99 / 172.99 |
| Ecobag Grande / Caneca | R$ 24.99 / R$ 30.60 |

The landing-page simulator shows a generic "T-shirt preço de custo R$ 40.83" (undated, no model; older). A seller-run Montink store page showed Quality R$ 48.20 and hoodies R$ 110.35-160.95, i.e. same tee, different hoodie prices; hoodies are irrelevant for ML today. Front print on the Quality tee: DTG ("Silk HD"), area 29x42 cm front and back, 3508x4961 px at 300 dpi (https://montink.sak.com.br/area-maxima-de-impressao-e-tecnica-utilizada-na-impressao-por-produto, 2026-07-27). Back print costs: not separated in any page I found: UNVERIFIED.

**Illustrative margin (assumptions, not verified outcomes)**: cost R$ 48.20 + ML up to 20 percent of sale + freight up to about R$ 50 (Montink's own simulation) + no ML fixed fee above R$ 79 (Montink's text). At a R$ 129.99 listing: 48.20 + 26.00 + up to 50 = up to 124.20, leaving about R$ 5.80 in the worst freight case; at light-parcel freight (about R$ 20-25) about R$ 30-35. ML's real fee/freight tables were not re-read here; see ML docs in ML_OWN_SHIPPING.md. The point: freight on ME2 is the swing factor and Montink's own example needs a high price.

---------------------------------------------------------------------------
## 5. Production, delivery, minimum, cancellation, defects

- **Minimum order**: none ("sem pedido mínimo", Nuvemshop listing 2026-11-07).
- **Production**: average **4 business days**, counted from status "Etiqueta Impressa" (https://montink.sak.com.br/o-que-significa-o-status-do-meu-pedido). Everything ships from the Rio de Janeiro distribution center. A third-party review lists 7 business days total delivery (dodropshipping, 2026-11-07, UNVERIFIED).
- **Stock-outs happen**: orders pause in "Falta de estoque"; the seller chooses substitute, partial shipment, wait (can take up to 30 days) or cancel; refund then follows (2026-10-30 article). For ML this is a reputation risk (late dispatch or cancellation). Manual decision in the dashboard; no API found for it.
- **Edit/cancel**: native-store orders 24 h. For integration orders (ML) changes are possible **before the cost is paid** (2026-09-03 article). After supplier invoicing/shipping, no. Cancelling after paying cost: refund mechanics for integration orders not documented: UNVERIFIED.
- **Defects**: supplier reproduces the **same product, colour, size** and ships it to the buyer, no new order, customer sends photos (2026-05-12). Taste/size returns, regret within 7 days, and orders returned after 3 failed delivery attempts are the **seller's cost**; returns after the second reship are charged to the seller; a returned parcel takes about 20 business days to reach the CD. Under ML, buyer claims and reverse logistics run through ML to the **seller's return address** (set in step 2 of setup).
- **Branding**: no custom packaging or labels (https://montink.sak.com.br/posso-personalizar-a-embalagem-dos-meus-produtos, 2026-05-13). Samples: not free; buy your own at cost by setting profit to zero (2026-10-01).
- **Unsupported for hoodie on ML**: even though a hoodie exists in the catalog (DTF print, front 21x25, back 29x42 cm), the ML app cannot export it.

---------------------------------------------------------------------------
## 6. Invoices (NF) and what is still unknown

- Default: the **final customer receives an NF from the supplier, at cost value only**, not at the sale value (2026-06-03). To get an NF at the full sale value the seller needs **Bling + CNPJ + Inscrição Estadual + digital certificate** (https://montink.sak.com.br/como-integrar-minha-loja-com-o-bling, 2026-05-12). CFOPs listed there: 6108 / 6120 / 6122 and "remessa" 5923/6923.
- For **TikTok Shop** Montink states outright that the shipping label depends on the NF and the Bling-to-TikTok route is recommended (2026-05-12). For **Mercado Livre** the article says **nothing** about NF/DC-e. VERIFIED silence.
- From ML (LABEL_BRIDGE.md B4): ME2 labels stay locked at `invoice_pending` until the seller imports an NF-e (PJ contribuinte) or issues a DC-e (PF / non-contribuinte, 3-day limit, no API). Whether the Montink integration resolves this itself, or leaves it to the seller (Bling for CNPJ, DC-e by hand for CPF), is **UNVERIFIED and the single most important open question** for CPF vs MEI choice.
- CPF onboarding: the platform accepts a CPF registration (withdrawal rules mention "Pessoa Física"), VERIFIED. Whether a CPF ML account gets Mercado Envios for Moda-with-variations: see the ML approval step above; UNVERIFIED.

---------------------------------------------------------------------------
## 7. Seller experience and reputation

- **Reclame Aqui** https://www.reclameaqui.com.br/empresa/montink_190944/ (fetched 2026-11-07; the page shows data 2026-05-01 to 2026-10-31): reputation **"Ótima"** every month May-Oct 2026, verified company, 31 complaints in 6 months, 100 percent answered and 100 percent resolved, 83.3 percent would do business again, consumer average 8.72/10 (18 rated), average reply time **7 days 4 hours**, ranked 39th in "E-commerce - Moda". Recent complaint titles: auto-renewal charged and refund refused (2026-09-22), plan refund (2026-09-08), "suporte inexistente para integração de frete em Shopify" (2026-08-31), two paid test orders stuck "sem estoque" awaiting cancellation/refund (2026-08-26), wallet balance disappearing after a system crash at plan renewal (2026-08-10). Peers on the same page: Dimona 7.5, Reserva INK 6.0. Only summary read; individual complaint pages are behind a Cloudflare challenge (403).
- **Nuvemshop app listing** (https://www.nuvemshop.com.br/loja-aplicativos-nuvem/montink): 4.5/5 from 14 reviews; one 1-star "muito instável, não consegui configurar" (2025-12-14); praise for stock/tracking sync; criticism of mixed-cart limits. Third-party rating 4.4/5 (dodropshipping).
- **ML-specific seller reviews**: none found. The integration is two months old. YouTube has several Montink reviews (e.g. "Testei a MONTINK", "2 ANOS com a Montink", "Por que 90% das lojas na Montink não vendem?") but I could not read transcripts: content UNVERIFIED. Reddit blocked (403). Trustpilot blocked (403/404).
- Same-day freshness: the help center changed on 2026-09-03/09 (unified orders screen, ML and TikTok guides, fraud screen 2026-09-16). Expect rough edges.

---------------------------------------------------------------------------
## 8. Can the full flow be automated through Montink?

Target: ML order -> production -> shipping -> tracking to ML -> NF, for dog-breed printed apparel.

| Step | Mechanism | Automatic? | Cost | Status |
|---|---|---|---|---|
| Design / product creation | Montink web editor, "Modo Simples", upload PNG (3508x4961 for tee). No product API | **Manual per design** (browser automation of the seller's own dashboard is a possibility, not tested; terms read for bots, nothing explicit either way: UNVERIFIED) | plan | VERIFIED no API |
| Mockups that ML accepts | Seller makes own white-background mockups | Manual or ours (we can render them) | 0 | VERIFIED rule |
| ML listing | "Exportar" button per product, with taxa adicional | **Manual click per product**; ML API listings of our own would not be linked to Montink products | 0 | VERIFIED |
| Mercado Envios activation | ML support ticket for Moda+variations via API | **Manual, once**, ML decides, no deadline | 0 | VERIFIED |
| Order import ML -> Montink | Montink ML app | **Automatic** (+ manual sync if missing) | 0 | VERIFIED |
| Pay production cost | Cobrança automática toggle + wallet | **Automatic once enabled**, but wallet top-up = Pix QR in the dashboard, **no API**: keep a buffer, top up by hand | cost + 10% + R$2 per unit | VERIFIED; refill is manual |
| Production + ship | Supplier ships from the Caxias CD, ME2 label from ML address | **Automatic** | ML freight (deducted by ML) | VERIFIED flow; label hand-off UNVERIFIED |
| Tracking to ML | ML's own ME2 tracking from the label; Montink stops at "production" | **Automatic by ML**, Montink pushes nothing | 0 | VERIFIED |
| NF / DC-e | Default: supplier NF at cost to buyer. Full-value NF needs Bling+CNPJ+IE+certificate. ML `invoice_pending` handling: unknown | **Unknown**; likely manual DC-e for CPF, Bling for CNPJ | Bling plan | UNVERIFIED |
| Our own monitoring | ML `orders_v2`/`shipments` notifications + Montink `GET /orders`, `/order/{id}`, webhook | We can build it (GitHub Actions/Worker) | 0 | Feasible; Montink API needs the seller's token |
| Stock-out decisions, support tickets, claims | Dashboard / ML | **Manual** | 0 | VERIFIED |

**By mechanism**: (A) Montink's native ML integration is the only route that handles the ML label; it automates import, payment (after wallet is funded), production, and shipping. (B) Montink's API automates order injection and status, but ships with Montink's own carrier and tracking, so it is suitable for a **non-ME2 channel** (our own site, or any channel where the seller ships by itself), not for ML ME2 listings. A hybrid (A for ML, B for any other channel) shares the same wallet and designs.

**Recurring manual work**: wallet top-ups, exporting each new design to ML, claims/stock-out handling, and the NF/DC-e step until proven automatic. **One-time manual work**: plan signup, ML OAuth link, ship-from/return address setup, ML Mercado Envios review ticket, Bling (if CNPJ).

**Product fit for dog-breed apparel**: Quality tee white/black works as is. Colour range, hoodies and pet products are outside the ML integration today.

---------------------------------------------------------------------------
## 9. Evidence on Shopee, Amazon, TikTok Shop

- **TikTok Shop**: official integration live (guide 2026-09-03). Same three products (Quality tee black/white, mug, ecobag), Montink app installed from the TikTok Seller Center, the Dimona CD registered as warehouse, return address = seller's, NF mandatory via Bling-to-TikTok (label depends on it), tracking handed to TikTok after production. VERIFIED.
- **Shopee and Amazon**: no order/label integration found. The only mention is the "Produto externo" feature (https://montink.sak.com.br/como-criar-produtos-externos-na-sua-loja, 2026-05-11) which lets a Montink store link to a Hotmart, Shopee or Amazon product as an affiliate-style link; it is not fulfillment. Not in the integrations list (2026-05-12). VERIFIED. Shopee/Amazon labels: not supported as far as any page shows.
- Also in the list: Bling, Hotmart, Eduzz, Monetizze, Facebook catalog, Google Shopping, Shopify, Nuvemshop, Yampi, Sympla, SAK, Lily, Jivochat, Replay, Pinterest, Ovni, API.

---------------------------------------------------------------------------
## 10. Zero-order checks to close the unknowns (no sale, no ToS issue; they need the owner's own account)

1. Sign up for the 7-day trial with the intended CPF/CNPJ (full refund within 7 days).
2. In the dashboard confirm which plan exposes Mercado Livre and whether Export shows a Quality tee white/black only.
3. Ask Montink support (ticket) three things: how the ML label reaches the factory, who handles `invoice_pending` (NF-e or DC-e) for ML orders and whether a CPF seller is supported, and whether "cobrança automática" covers API-created orders.
4. In ML: Central de vendedores -> Envios shows whether Mercado Envios is active; open the review ticket with Montink's suggested sentence.
5. Export one tee at a very high price, paused, and read back `shipping.mode`/`logistic_type` through the ML API (no sale).
6. Generate an API token and call `GET /products`, `GET /calculate_shipping/CEP/1` to confirm the cost the catalog list implies (`preco_final`) and the actual freight options.

Open items, ranked: (1) NF / DC-e handling on ML; (2) label hand-off mechanics; (3) real unit cost vs catalog price; (4) which plan; (5) what ML ME2 reputation/dispatch penalties apply when the supplier is stuck on a stock-out.

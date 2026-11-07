# LABEL BRIDGE study: Mercado Livre order -> Dimona/Dropsimples -> tracking back to ML

Study date: 2026-11-07. Method: public docs and help pages only, fetched from a GitHub Actions runner (no accounts, no tokens, no login or CAPTCHA bypass). Raw text of every page cited is saved in `docs/brazil_data/bridge/` and `docs/brazil_data/dimona/`.

Labels: **VERIFIED** = read in the primary text, with URL and date. **UNVERIFIED** = inference, third-party claim, or not found. "Third-party" = blog or vendor, not ML or Dimona.

---------------------------------------------------------------------------
## 0. Bottom line

1. **A fully automatic, policy-compliant "ML order -> Dimona ships direct to buyer -> tracking back to ML" flow does not exist today for apparel.** The blockers are policy and ML mode rules, not missing code:
   - **B1 Dimona policy.** Dimona/Dropsimples states in writing that it does not operate on Mercado Livre/Shopee/Amazon and does not accept third-party shipping labels (VERIFIED, 1.1). Their API has a `shippingLabel` endpoint, but it is gated behind an email to api@dimona.com.br and documented only as `{"link": "..."}` (VERIFIED, 1.2). Whether they would enable it for an ML seller is UNVERIFIED and contradicts their published policy.
   - **B2 ME1 (seller's own carrier plus own tracking) is closed for T-shirts.** ML's developer doc: an item that has ME2 available "não poderá ser publicado pela modalidade ME1"; ME1 is for heavy/bulky goods and needs a commercial advisor (KAM) (VERIFIED, 2.4).
   - **B3 ME2 labels are ML-network documents.** ML issues the label (plus a CT-e in Brazil) and forbids custom labels. Route is Seller -> Coleta/Place/agency -> HUB -> ML-chosen carrier. Whether an ML-labeled parcel can be carried by Jadlog/J&T/Dimona's carriers is UNVERIFIED (almost certainly not).
   - **B4 Fiscal.** For ME2 drop_off / Places / Coleta in Brazil the label stays locked until the seller imports a valid NF-e XML (model 55) by API (PJ contribuinte), or issues a DC-e (PF / PJ não-contribuinte, not importable by API). Dimona's default NF is issued by Dimona at cost price; its API takes only chave/serie/numero/link (DANFE PDF link), not XML (VERIFIED, 1.4 and 2.5).
2. **The only ML mode with a clean, documented tracking API for "supplier ships with its own tracking" is ME1 (`POST /v2/shipments/{id}/seller_notifications`) and custom shipping (`PUT /shipments/{id}`).** ME1 is closed for apparel; custom is the one to test (availability for our category UNVERIFIED).
3. **ME2 label-forwarding** (4A) is buildable on the ML side, but its physical end (Dimona accepting an ML label, the parcel entering ML's network from Dimona's factory) is unknown and conflicts with Dimona policy.
4. **Our own website: feasible** with Dimona's documented API (quote, order, tracking, webhook_url). Gaps: payment is done in the Dimona panel (no API call documented), and NF handling (section 5).

---------------------------------------------------------------------------
## 1. Dimona / Dropsimples

### 1.1 Marketplace and label policy (VERIFIED; Zendesk help center, fetched 2026-11-07)
- Article 20267787637396 "Política de Marketplace - O Que Você Precisa Saber", updated 2024-02-26. https://suporte.camisadimona.com.br/hc/pt-br/articles/20267787637396-Pol%C3%ADtica-de-Marketplace-O-Que-Voc%C3%AA-Precisa-Saber [dimona/zendesk_articles.txt line 766]
  Exact: "Nós optamos por não operar em plataformas de marketplace, como o Mercado Livre, Shopee, Amazon e outras. A principal razão é que nosso sistema emite automaticamente etiquetas de envio personalizadas para cada pedido, o que impede a aceitação de etiquetas de envio de terceiros."
- Article 23382625110548 "Etiqueta de envio", updated 2024-02-02. https://suporte.camisadimona.com.br/hc/pt-br/articles/23382625110548-Etiqueta-de-envio [zendesk_articles.txt line 487]
  Exact: "Quando um pedido é gerado e pago no Dropsimples o sistema gera automaticamente nossa etiqueta de envio que nos faz uma cobrança via sistema independente do método de envio, isso impossibilita aceitarmos etiquetas de envio de terceiros dentro do nosso sistema. Outro ponto que impossibilita aceitarmos etiquetas de terceiros é que o ponto de coleta fixo fica dentro da nossa fábrica e não conseguimos que todas as transportadoras tenham acesso ao nosso centro de distribuição."
- Implications read from the text: Dimona charges its own label per order regardless of carrier (an external label would mean paying freight twice); only Dimona's carriers can collect at the factory.
- Carriers: Dropsimples has "PAC, SEDEX e Transportadora J&T", cheapest of three chosen by CEP (article 23380654847252, 2024-02-02; zendesk_articles.txt line 511). The API quote lists Correios Sedex, Jadlog and Buslog.
- Tracking is the seller's job: status "Enviado" -> "o código de rastreio ... será de responsabilidade do lojista pegar em nosso painel, e enviar para o cliente final" (article 14815928193812, 2023-10-23).
- Payment: "dentro do painel de lojista ... Boleto bancário, Cartão de crédito (podendo cadastrar um cartão para pagamentos automáticos), Pix" (article 14823630388116, 2025-01-09). After payment approval the order cannot be cancelled ("é gerada a etiqueta de produção"). No payment API call is documented (UNVERIFIED that none exists).

### 1.2 API endpoints for external label and NF (VERIFIED; Postman public collection "Dimona API V2", published 2025-05-27)
Source: https://api.camisadimona.com.br/ (publishedId 2sB2qdgLJQ). Saved: dimona/postman_readable.txt. Base: `https://admin.camisadimona.com.br`; header `api-key` (create account on camisadimona.com.br).

| Endpoint | Exact documented body | Notes |
|---|---|---|
| `POST /api/v2/order/{order-id}/shippingLabel` | `{"link": "link-to-label"}` | "Attention: Before using this endpoint send an email to api@dimona.com.br" |
| `POST /api/v2/order/{order-id}/nfe` | `{"chave":"33180513570097000110550010000166321270551123","serie":"1","numero":"1234","link":"https://link-para-pdf-danfe.com.br"}` | Same email warning. `link` example name = DANFE PDF. No XML field. |
| `POST /api/v2/order/5846776585/shippingDocuments` | `{"nfe":"https://s3-eu-west-1.amazonaws.com/printcloud.storage/edi/dev/edi/p5846776585_Invoice.pdf","label":"https://s3-eu-west-1.amazonaws.com/printcloud.storage/edi/dev/edi/p5846776585_DHLExpressBrazil.pdf"}` | Same email warning. Example names are PDFs and a DHL Express Brazil label: looks built for an EDI partner (inference, UNVERIFIED). |
| `POST /api/v2/order`, `/api/v3/order` | optional inline `nfe{chave,serie,numero,link}`, `webhook_url`, `delivery_method_id`, `shipping_speed` (pac/sedex), `customer_document`, `address{...}`, `items[{dimona_sku_id,qty,designs,mocks}]` | Whether the inline `nfe` is honored without the email approval: UNVERIFIED. |

Format answers:
- Label is passed **by URL**. VERIFIED. Only example is a **PDF**. ZPL, size, URL expiry, and whether URL must be public: UNVERIFIED (not documented).
- NF: chave (44 digits) + serie + numero + link to DANFE PDF. VERIFIED. XML: not documented.
- A given NF cannot be reused on two orders (article 23382914661140) because their carrier tracks by NF access key.

### 1.3 Order lifecycle and tracking (VERIFIED; same collection)
- `GET /api/v2/order/{id}` -> `status`, `status_id`, `shipping_method_name`, `shipping_cost`, `tracking_url` (ondeestameupedido.com), `tracking_code` (null until shipped).
- `GET /api/v2/order/{id}/tracking` -> event history; `/timeline` -> status changes, "Etiqueta ... criada", invoice events.
- `webhook_url` exists on order create; the "Webhook" folder in the public docs is empty, so **payload/events are UNVERIFIED**. Plan to poll.
- Quote: `POST /api/v2/shipping {"zipcode":"20061001","quantity":"1"}` -> Correios Sedex R$10.34 6d (id 2), Jadlog Econômica R$15.35 10d (177), Jadlog Express R$15.57 9d (176), Buslog R$24.32 5d (780).

### 1.4 Dimona invoices (VERIFIED)
- Article 14207402191124 (updated 2024-09-19): every order must carry an NF with product + freight. Seller can send its own NF (Tiny, Bling, etc., then associate in the panel) or Dimona issues one in Dimona's name at cost price + freight ("a nota fiscal da Dimona com o produto no valor de R$40,00 e não de R$100,00"). CPF-only sellers always get the Dimona NF (article 14214413830292).
- ML expects the seller's NF-e for the sale (2.5). Dimona's NF is not that.

### 1.5 Other
- Production 3-5 business days + shipping 5-10 (SUMMARY.md).
- Dropsimples integrations: Montink, Nuvemshop, Shopify, WooCommerce, Loja Integrada, spreadsheet, API. **No Mercado Livre integration** (articles 14849262318484, 20268619891988 etc.).

---------------------------------------------------------------------------
## 2. Mercado Livre side (official developer docs; runner fetch 2026-11-07)

Access: `developers.mercadolivre.com.br/pt_br/<slug>` returned HTTP 200 with full text once the exact slugs from the docs' navigation were used (pt-br and en_us variants of other slugs were not needed). Files: `bridge/developers_mercadolivre_com_br_pt_br_*.txt`. ML help-center pages are mostly 403/verification walls; one public page (id 827) worked. Nothing was bypassed.

### 2.1 Modes (VERIFIED)
https://developers.mercadolivre.com.br/pt_br/mercado-envios: ME1 = "utilizando sua própria logística ou serviços de terceiros"; ME2 = "modalidade de envio do Mercado Livre, onde se gerencia toda a logística utilizando diversos meios como correios, agências, entre outros" (Drop_off, Coletas cross_docking, Places xd_drop_off, Flex self_service, Turbo, Full); **Custom** ("o vendedor carrega uma tabela com os preços de envio por cada região e se encarrega da logística"); **Not Specified** (buyer and seller agree).

### 2.2 ME2 label: contents, carriers, who can carry
Sources: https://developers.mercadolivre.com.br/pt_br/mercado-envios-2 (updated 2026-07-06) and https://developers.mercadolivre.com.br/pt_br/envios-coletas-places (updated 2026-09-25). VERIFIED unless noted.
- API: `GET https://api.mercadolibre.com/shipment_labels?shipment_ids=ID1,ID2&response_type=pdf` (or `zpl2`), max 50 ids. Requires `mode=me2`, `status=ready_to_ship`, `substatus=ready_to_print` (reprint allowed in `printed`). Size 15x10 cm. "não é permitido criar etiquetas personalizadas para nenhum vendedor". Brazil only: NF has the same dimensions as the label and can be printed with it.
- Routes: Coleta (cross_docking) "Um carrier recolhe os produtos do domicílio do vendedor e os leva a um HUB ... Vendedor -> Coleta -> HUB -> Carrier -> Comprador"; Places (xd_drop_off) "Vendedor -> Place -> Coleta -> HUB -> Carrier -> Comprador"; Drop_off "O vendedor leva os produtos diretamente ao correio ou ponto de entrega designado ... O carrier é selecionado para a entrega final". Coleta/Places activation is reviewed weekly against delivery performance.
- ML chooses the carrier; `/shipments/{id}/billing_info` returns a `carrier` CNPJ block, and "emissão do CT-e (gerado pelo Mercado Livre)" releases the label (https://developers.mercadolivre.com.br/pt_br/importar-nota-fiscal, 2026-08-03).
- Correios appear behind drop_off per third parties (Bling blog 2025-10-28: ML "utiliza tanto os Correios quanto transportadoras parceiras"; label includes address, tracking code, cost, product info). The docs do **not** say the label works outside ML's network. Cross-carrier use: UNVERIFIED.
- Practical dropship step (third-party, independent source A): Nuvemshop blog https://www.nuvemshop.com.br/blog/dropshipping-mercado-livre/ (fetched 2026-11-07; article date not shown): "vendedores do Mercado Livre geram as etiquetas e as enviam ao fornecedor, para que ele as imprima, cole nas embalagens e poste a mercadoria em uma agência do Mercado Envios."
- One ship-from address per account (third-party, ecommercenapratica https://ecommercenapratica.com/blog/dropshipping-no-mercado-livre): "Você só pode cadastrar um único endereço de envio por conta"; dropshipping is incompatible with Full. Coleta picks up at the seller's registered address, so it would only fit if that address is where Dimona holds the parcel: UNVERIFIED and needs ML plus Dimona agreement.

### 2.3 Dispatch deadlines and penalties
- Official (https://developers.mercadolivre.com.br/pt_br/gerenciamento-de-envios, fetched 2026-11-07): `GET /shipments/{id}/sla` gives the max dispatch time; "No caso de que o vendedor despache seus envios posteriormente a esta data e hora ... impactará em demoras que afetarão na sua reputação e destaques." For Coleta the deadline is the scheduled pickup time. VERIFIED.
- ME1: "Comunicar os status shipped e delivered é obrigatório, estando sujeito a penalidades em caso de não atualização" (https://developers.mercadolivre.com.br/pt_br/status-de-pedidos-rastreamento, updated 2026-09-17). VERIFIED.
- DC-e sellers: 3 days to issue it or the order is auto-cancelled (importar-nota-fiscal). VERIFIED.
- Reputation targets (third-party, ecommercenapratica): complaints up to 1%, mediations up to 0.5%, at most 1 cancellation per 200 sales, shipping delays under 6%.
- **Penalty for dispatching an ME2 parcel with a carrier other than the one ML chose: not found in any readable official page. UNVERIFIED.**
- Whether a made-to-order item may declare 3-5 days of manufacturing under ME2 (handling-time/`manufacturing_time`) is not covered in the pages read: UNVERIFIED.

### 2.4 Seller-ships-itself options
- **ME1** (https://developers.mercadolivre.com.br/pt_br/mercado-envios-1, updated 2026-02-06; VERIFIED): "permite aos vendedores vender produtos pesados ou volumosos ... gerenciar a sua própria logística ou utilizar serviços de terceiros para o envio de produtos que não são elegíveis para o Mercado Envíos 2". "se um item tiver a modalidade ME2 disponível, ele não poderá ser publicado pela modalidade ME1." Activation through commercial advisor/KAM; ME1 activation requires ME2 already active. Caps 500 cm / 500 kg. FAQ https://developers.mercadolivre.com.br/pt_br/me1-me2-e-frete-gratis (2026-08-14): `PUT /items` with `me1` returns 200 but stays `not_specified` if ME2 is enabled on the account. Corroboration: Omie.HUB help 2026-06-11 https://ajuda.omie.com.br/pt-BR/articles/15452425-configurando-o-mercado-envios-1-me1-no-mercado-livre-via-omie-hub ("Anúncios elegíveis para Mercado Envios 2 (ME2) não podem ser ativados na modalidade ME1"). Conflict: UpSeller (https://upseller.com/pt/help-doc-article-1585, 2025-07-08) states ME1 is a prerequisite for ME2, the reverse of the official doc; official is newer.
  - So **ME1 is closed for T-shirts** (category-specific `shipping_preferences` not checked because it needs a token).
  - ME1 tracking (VERIFIED, 2026-09-17 doc): `POST https://api.mercadolibre.com/v2/shipments/{shipment_id}/seller_notifications` body `{"payload":{"service_id":11,"comment":"...","date":"<ISO8601 with tz>"},"tracking_number":"...","tracking_url":"...","status":"shipped|delivered|not_delivered","substatus":null}`. MLB service_id = 11. First event must be shipped with substatus null ("A caminho"); tracking_number and tracking_url go together or not at all; V1 ended 31/10; shipment id from `GET /orders/{order_id}/shipments`.
- **Custom** (https://developers.mercadolivre.com.br/pt_br/envios-personalizados, updated 2024-12-10; VERIFIED doc): item `shipping.mode="custom"` with `costs[]`. Tracking: `PUT https://api.mercadolibre.com/shipments/{shipment_id}` `{"speed":120,"status":"shipped","tracking_number":1234,"receiver_id":<buyer id>,"comments":"..."}`; later `{"status":"delivered","receiver_id":...}`; cancel via POST. "O campo tracking_number é requerido para a API, mas não será em nenhuma lista e/ou detalhamento de venda." `not_specified` has no shipment_id. Caveat in the doc: "Nos países onde o modo Mercado Envios está ativo, somente poderá adicionar envios personalizados grátis em categorias que não aceitem ME". Official help id 827 (https://www.mercadolivre.com.br/ajuda/827, fetched 2026-11-07) for "vender combinando a entrega": deliver in person, buyer pickup, or "Enviar o produto por uma agência conveniada ... compartilhar o código de rastreamento com o comprador"; "Envie o pacote no nome do comprador". **Whether a MEI/CNPJ seller can list T-shirts as custom/not_specified when ME2 covers the category: UNVERIFIED.** SuperFrete (third-party) claims sellers "não são mais obrigados" to use ML shipping.
- **Flex** (https://developers.mercadolivre.com.br/pt_br/envios-flex, 2026-10-15; VERIFIED): seller delivers itself same/next day, only in SP, RJ, Brasília, BH, Porto Alegre, Salvador, Curitiba; the Flex app is required and "não está disponível para integrações". Not suitable.
- Who can use what: ME2 drop_off/Places/Coleta normal sellers (Coleta/Places subject to performance); PF and PJ não-contribuinte have limited NF-e tools (Tray, citing ML); ME1 needs KAM and heavy items; Flex needs coverage; custom unknown for apparel.

### 2.5 Invoice rules that gate the ME2 label in Brazil (VERIFIED)
- https://developers.mercadolivre.com.br/pt_br/importar-nota-fiscal (updated 2026-08-03): PJ contribuinte sellers import NF-e for drop_off, xd_drop_off, xd_same_day, cross_docking. "A importação da Nota Fiscal ... altera o status do envio, destrancando o substatus invoice_pending e permitindo a geração da etiqueta de envio." `POST https://api.mercadolibre.com/shipments/{id}/invoice_data/?siteId=MLB`, `Content-Type: application/xml`, body = full `<nfeProc>`; model 55 only; production SEFAZ only; "Uma vez impressa a etiqueta, não será possível alterar a nota." PF / PJ não-contribuinte: DC-e, "Não é possível importar ou fazer upload de DC-e via API".
- NT 2025.001 (since 2025-09-01): card/Pix payment data in NF-e (tpIntegra=1, intermediary CNPJ 03.007.331/0001-41, tBand, cAut for cards).
- `POST /packs/{pack_id}/fiscal_documents` (multipart XML or PDF+XML; https://developers.mercadolivre.com.br/pt_br/anexar-nota-fiscal, 2026-04-07) is not allowed for cross_docking, xd_drop_off, drop_off, fulfillment in MLB; it is for ME1/custom.
- Buyer CPF: `GET /shipments/{id}/billing_info` -> `receiver.document`.

---------------------------------------------------------------------------
## 3. Real-world evidence (independent sources)

No source found documents a Dimona/Dropsimples-to-ML flow. Findings:
1. Nuvemshop blog (above): supplier prints the seller-generated ML label, sticks it, posts at a Mercado Envios agency.
2. Tray Escola https://tray.com.br/escola/dropshipping-mercado-livre/ (2026): "a responsabilidade pela venda continua vinculada ao seller"; PJ contribuinte NF-e vs DC-e; dispatch delays hurt reputation; PF has limited NF-e/shipping tools. No label mechanics.
3. ecommercenapratica (above): supplier ships; one ship-from address; no Full; reputation targets; send tracking code to buyer.
4. Omie.HUB help 2026-06-11: ME1 automated end to end (NF-e to ML automatically; "Shipped" only if tracking code exists in ERP; "Delivered" optional). Proves the ME1 bridge is routine, but only for ME1-eligible heavy items.
5. UpSeller ME1 status guide https://www.upseller.com/pt/help-doc-article-3363 (2026-08-19): needs tracking code + URL; Entregue/Não entregue are final.
6. Bling https://blog.bling.com.br/como-enviar-mercado-livre-correio/ (2025-10-28): ML order via Correios = print ML label + NF/DC-e, post at agency; freight pre-paid by ML.
7. Montink (POD maker): Nuvemshop app listing https://www.nuvemshop.com.br/loja-aplicativos-nuvem/montink says "Leve os mesmos produtos para Mercado Livre, TikTok Shop, ..." and ships "por Correios e transportadoras, com rastreio enviado ao cliente"; https://dodropshipping.com/best-dropshipping-suppliers-in-brazil/ says Montink "integrates with ... Mercado Livre". Marketing claims only. **Montink's label/NF/ME handling on ML: UNVERIFIED** [UPDATE 2026-11-07: now answered in MONTINK.md; official ML integration exists, ME2 label via the Dimona CD ship-from address; NF/DC-e step still open] (ajuda.montink.com.br SSL error, montink.com.br/marketplaces did not load). Likely mechanism (inference only): Nuvemshop's Mercado Livre channel, with the order still flowing through the Nuvemshop store.
8. Dogama official ML page https://dogama.com.br/en/mercado-livre/: automatic NF-e and Full inventory; nothing on labels outside Full.
Common ground: (a) the seller stays accountable to ML for dispatch; (b) with ME2 the supplier's parcel carries the ML label and goes to an ML/Correios agency; (c) automatic tracking handoff exists only for ME1/custom. None documents a supplier that insists on its own label.

---------------------------------------------------------------------------
## 4. Bridges

Common prerequisites (owner must create; we created nothing): ML developer app + seller OAuth tokens (refresh token as secret), notification URL (topics `orders_v2`, `shipments`), Dimona API key, NF-e issuer for the seller CNPJ. Cloudflare Worker receives ML notifications and queues; GitHub Actions or Worker cron does long steps. Stay within the $5 Cloudflare / $4 GitHub plans.

### 4A. ME2 label forwarding (ML side buildable; physical end UNVERIFIED; conflicts with B1)
1. Webhook -> `GET /orders/{id}`, `GET /shipments/{id}` (header `x-format-new: true`), `GET /shipments/{id}/billing_info` (buyer CPF).
2. Map `seller_sku` to `dimona_sku_id` + design/mockup URLs.
3. Issue NF-e (seller CNPJ, NT 2025.001 fields).
4. `POST /shipments/{id}/invoice_data/?siteId=MLB` (XML) when `substatus=invoice_pending`; wait for `ready_to_print`.
5. `GET /shipment_labels?shipment_ids={id}&response_type=pdf`; host the PDF at a public HTTPS URL.
6. Dimona `POST /api/v2/order` (`order_id`=ML order id, customer fields, `address`, items+designs, `delivery_method_id`, `webhook_url`, optional `nfe` with DANFE PDF link).
7. `POST /api/v2/order/{id}/shippingLabel {"link": "<pdf url>"}` (or `/shippingDocuments`) after Dimona enables it.
8. Pay Dimona order (panel; saved card auto-pay), Dimona produces and ships (carrier must enter ML flow: unknown).
9. Tracking back: none for ME2 (ML tracks via carrier scans). Poll Dimona only for "Enviado" and `GET /shipments/{id}/sla`.
Blockers: B1, B3, B4, and double freight.

### 4B. ME1 (fully automatable, closed for apparel)
After Dimona order creation: NF via `POST /packs/{pack_id}/fiscal_documents`; poll `GET /api/v2/order/{id}` until `tracking_code`; `POST /v2/shipments/{id}/seller_notifications` (service_id 11, shipped, tracking_number, tracking_url); later `delivered` when `GET /api/v2/order/{id}/tracking` shows "Entregue". Blocker B2.

### 4C. Custom shipping (best candidate to test first)
Same as 4B but tracking via `PUT /shipments/{id}` (`status:"shipped"`, `tracking_number`, `speed`, `receiver_id`, `comments`) and `status:"delivered"`. Dimona keeps its own label and carrier, which is compatible with its policy. Unknown: category eligibility, reputation and exposure effects, MEI fiscal class.

### 4D. Manual hybrid
Per order, send the ML label PDF to Dimona and someone posts the sticked parcel at an agency. Only if Dimona agrees (B1).

### 4E. What to ask
**Dimona** (api@dimona.com.br): (1) enable `shippingLabel`/`shippingDocuments` for an ML seller despite the marketplace policy? PDF 10x15 cm or ZPL? public URL? (2) can an ML-labeled parcel be handed to Correios/ML at the factory, or can ML Coleta pick up there; is your label fee still charged? (3) webhook payload spec. (4) API call or credit/balance mode to pay orders without the panel. (5) accept the seller's NF at order creation, and XML? (6) alternative tax model so the Dimona cost-price NF is not sent to the buyer.
**Mercado Livre** (seller support/KAM, developer ticket): (1) can a MEI/CNPJ seller list apparel as custom or not_specified; effect on reputation/exposure/free shipping; penalty for non-ML carrier on ME2. (2) can Coleta use the seller's registered address while the producer is another legal entity. (3) can ME1 be enabled for small ME2-eligible items with a producer's own carrier. (4) is a MEI "PJ contribuinte" (NF-e by API) or non-contribuinte (DC-e only). (5) handling time allowed for made-to-order items on ME2.
**Accountant**: tax model for POD with a third-party producer shipping directly to the consumer.

---------------------------------------------------------------------------
## 5. Bridge for our own website (VERIFIED against Dimona docs)

Endpoints on `https://admin.camisadimona.com.br`, header `api-key`.
1. Checkout quote: `POST /api/v2/shipping {"zipcode":"<CEP>","quantity":"<n>"}` -> `[{name,value,business_days,delivery_method_id}]`; keep the chosen `delivery_method_id`.
2. Optional stock check: `GET /api/v2/sku/{reference}/availability`.
3. After our payment is captured: `POST /api/v3/order` (named slots front/back/sleeves/labels) or `/api/v2/order` with `order_id`, `delivery_method_id`, `customer_name`, `customer_document`, `customer_email`, `webhook_url`, `items[{sku,name,qty,dimona_sku_id,designs,mocks}]`, `address{name,street,number,complement,city,state,zipcode,neighborhood,phone,country}`, optional `nfe{chave,serie,numero,link}`. 200 `{"order":"064-435-556"}`; 422 duplicate id.
4. Pay Dimona: panel only (Pix, boleto, card auto-pay). Gap: ask for an API/credit option.
5. Tracking: poll `GET /api/v2/order/{id}` (`status`, `tracking_code`, `tracking_url`) and `/tracking`; also accept `webhook_url` events (payload UNVERIFIED); email/WhatsApp the buyer and show `tracking_url` on the order page.
6. NF: with a CNPJ, issue via a fiscal API and send `chave/serie/numero/DANFE link` inline or via `POST /order/{id}/nfe` (email approval first); one NF per Dimona order. Without a CNPJ Dimona issues its NF at cost price (customer sees cost).
7. Errors: duplicate order (422), "Erro na transação" (inconsistent buyer data), no cancellation after payment approval.
Feasibility: yes, except the Dimona payment step and NF rules.

---------------------------------------------------------------------------
## 6. Verdict per question
1. Dimona external label/NF: VERIFIED. Policy refuses third-party labels (2 articles); API accepts label by URL and NF as chave/serie/numero/link, both gated by email. XML and ZPL not documented.
2. ML mechanics: VERIFIED for ME2 label API and routes, ML-issued CT-e, invoice lock, ME1 limits, ME1 tracking API, custom tracking API, Flex. UNVERIFIED: cross-carrier use of an ML label, penalty for non-ML carrier, custom mode in apparel, MEI classification.
3. Real-world: 8 sources; none shows a supplier with a mandatory own label. Montink-to-ML mechanics UNVERIFIED.
4. Conclusion: no fully automatic compliant flow with Dimona today. Test custom shipping (4C) first; 4A only with Dimona's written approval. Website bridge: feasible (section 5).

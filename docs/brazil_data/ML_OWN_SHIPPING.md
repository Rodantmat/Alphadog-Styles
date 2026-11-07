# Mercado Livre Brazil: can the seller (or a supplier) ship with its own carrier/label and just report tracking?

Study date: 2026-11-07. Method: public pages only, fetched from a GitHub Actions runner (`scripts/brazil/probe.py` task `ownship`, workflow `brazil-probe.yml`) plus web search. No logins, no accounts, no tokens, no CAPTCHA or ToS bypass. Raw text of every page cited is saved in `docs/brazil_data/ownship/` (file names are the slugified URLs). Prior findings: `LABEL_BRIDGE.md` (read first; this file extends its sections 2.4 and 4C and does not repeat its Dimona material).

Labels: **VERIFIED** = read in the primary text, with URL and date (the date is either "Última atualização" on the page or the fetch date 2026-11-07). **UNVERIFIED** = inference, third-party claim, not retrievable, or needs a logged-in account. "Third-party" = blog or vendor, not Mercado Livre.

---------------------------------------------------------------------------
## 0. Bottom line

**Short answer: at the API level yes, for T-shirts in practice no (not as a mode the seller can choose).**

1. **The mechanisms exist and are documented.** ML has three "seller ships it" mechanisms: ME1 (`seller_notifications`), `custom` (`PUT /shipments/{id}` with `tracking_number`) and `not_specified` ("entrega a combinar", tracking code shared with the buyer). The developer doc says "todos os vendedores têm habilitado custom e not_specified por padrão" (VERIFIED, 5.2).
2. **But they are fenced off from categories where ML's own shipping (ME2) is available.** Four independent signals, none contradicted by any source found:
   - ME1: "se um item tiver a modalidade ME2 disponível, ele não poderá ser publicado pela modalidade ME1" (VERIFIED, 2026-02-06, 3.1).
   - custom/not_specified: "Se o usuário tiver a opção default ME configurada, todas as suas publicações serão criadas sob essa modalidade, com exceção daquelas que têm uma categoria que não a suporta" and free custom shipping only "em categorias que não aceitem ME" (VERIFIED, 5.3).
   - ML support's own words to a seller on WhatsApp (Reclame Aqui complaint ID 163766681, dated 2023-04-29, VERIFIED text, but 3.5 years old): "Todos os vendedores que vendem em nossa plataforma agora usam o Mercado Envios nas categorias em que o serviço estiver disponível ... não será possível desativar o serviço para o envio dessa sua venda." and "Caso o envio seja postado por sua conta, não conseguimos estornar o valor da etiqueta." (5.4)
   - Cargoos synthesis of ML pages, 2026-10-14 (third-party but cites each ML page): "Com o Envios ativo na conta, os anúncios são criados nele, exceto em categorias que não o aceitam"; "frete a combinar ... Só dá para usar em produtos que não são elegíveis ao Envios do Mercado Livre, pela categoria ou pelo tamanho e peso." (5.5)
3. **T-shirts (MLB31447 "Camisetas e Regatas", vertical apparel, 6,156,564 items) are a mainstream ME2 category.** Its public category record lists `shipping_options: ["carrier","custom"]`, but the same value appears on phones and "Outros", so it does not discriminate (5.1). The category's `GET /categories/MLB31447/shipping_preferences` (the field that would show `me2_restrictions`) needs a token (403 without): **UNVERIFIED** for this exact category.
4. **So "supplier ships with its own label and we just paste the tracking" is not an ML-sanctioned path for a T-shirt listing.** What works instead: ME2 with the ML label printed by whoever packs (a supplier that agrees to stick ML's label and drop at an agency/Coleta). Dimona refuses third-party labels (LABEL_BRIDGE 1.1), so that is the blocker, not ML's API.
5. **Penalty if one ships ME2 with another carrier anyway:** the ME label is still charged and not refunded (ML support quote above); delivery status then never arrives from ML's network, the shipment shows delayed, and the seller is exposed on handling/dispatch SLA, claims and cancellations (sections 6 and 7). Precise sanction text: not found in any readable official page, **UNVERIFIED**.
6. **To settle it in a real account without selling anything:** section 9 (four zero-sale checks: `shipping_preferences`, category `shipping_preferences`, `POST /users/{id}/shipping_modes`, and a paused draft listing whose `shipping.mode`/`logistic_type`/tags are read back).

---------------------------------------------------------------------------
## 1. The modes in one table

| Mode | What it is | T-shirt / MEI-CNPJ fit | Verdict for "supplier's own label + report tracking" |
|---|---|---|---|
| ME2 drop_off (agência/Correios) | ML label, seller drops at agency; ML-chosen carrier | Open to normal sellers | NO own label; ML label mandatory. Supplier must print ML's label and post at agency |
| ME2 Coleta (cross_docking) | ML driver picks at the seller's registered address, to HUB | Performance-gated, weekly review | NO own label; one ship-from address per account |
| ME2 Places (xd_drop_off) | Drop at a Place, then Coleta, HUB | Performance-gated | NO own label |
| Flex (self_service) | Seller delivers same/next day in 7 metro areas, via Flex app | Own stock, coverage only | NO: not for a supplier, not integrable by API |
| Envios Agora (proximity) | 25-minute dispatch from seller stock, parcels <=50 cm side, 15 kg | Own stock | NO |
| Full (fulfillment) | Stock in ML warehouse | Needs stock; incompatible with dropship/made-to-order | NO |
| ME1 | Seller/third-party logistics, freight shown in the listing, tracking by `seller_notifications` | Heavy/bulky only; needs ME2 active, integrator, not red reputation | CLOSED for T-shirts |
| custom | Seller uploads a region price table, ships itself, tracking by `PUT /shipments/{id}` | All sellers "enabled" by default, but only in categories/items without ME | Mechanism perfect; availability for apparel UNVERIFIED and doubtful |
| not_specified ("a combinar") | No freight in the listing; buyer and seller agree; no shipment_id | Same as custom | Same as custom; worst conversion |
| local_pick_up / "retirada" | Buyer collects at the seller's address | Needs a physical pickup point | Not applicable to dropship |

Sources per row below.

---------------------------------------------------------------------------
## 2. Discovery: what mode does an account / category / item allow (API)

All VERIFIED in https://developers.mercadolivre.com.br/pt_br/mercado-envios (page "Última atualização 09/06/2026", fetched 2026-11-07, `ownship/developers_mercadolivre_com_br_pt_br_mercado_envios.txt`). Auth column: whether the endpoint answered without a token in my runner probe.

| Endpoint | Returns | Unauthenticated probe 2026-11-07 |
|---|---|---|
| `GET /sites/MLB/shipping_methods` | Carrier services (id, name, type, `shipping_modes[]` such as `["me2"]`, company, min/max time) | 403 PolicyAgent (needs token) |
| `GET /users/{user_id}/shipping_preferences` | `modes[]` among custom, not_specified, me2, me1; `option` (in/out/trial/null); `tags` (`optional_me1_allowed`, `optional_me2_allowed`, `turbo`, `flex2_migration`, `proximity`); `me2_enablers`; `local_pick_up`; `logistics`; `label` | not tested without token (docs say 401) |
| `GET /categories/{category_id}/shipping_preferences` | `logistics[]` with `mode` + `types` for me1/me2/not_specified/custom; `me2_restrictions` (fbm_non_totable, flex_ne, cbt_fulfillment, bulky_drop_off, farma, fragile, bulky_cross_docking, bulky_fulfillment); `restricted` (true/false); default `dimensions` | **403 for MLB31447 and MLB1430** (needs token) |
| `POST /users/{user_id}/shipping_modes` (headers `x-multichannel: true`, `X-Format-New: true`) | Pre-publication check: send item-like payload (category, price, catalog attributes, dimensions), get back which logistic types/modes the seller can use. Docs name it as the pre-check "antes de executar o POST do Item". The newer UP version supersedes `/users/{id}/shipping_modes` for already-created items but "permanece ativo ... para as validações antes de criar uma publicação" | needs token |
| `GET /categories/{id}` (public) | `settings.shipping_options`, `shipping_profile`, `simple_shipping`, `buyer_protection_programs`, `fragile` | **200, no token** |
| `GET /items/{id}` / `POST /items` | `shipping.mode` and `shipping.logistic_type`; values `me2`, `me1`, `custom`, `not_specified`; tags `me2_available`, `adoption_required` ("Item not_specified que ainda não adotou o ME2, que é o recomendado"), `optional_me1_chosen`, `lost_me2_by_dimensions`, `mandatory_free_shipping`, `self_service_in/out/available` | needs token |

Key semantic rules (VERIFIED, same page):
- Default account with ME2 and ME1 both active is `optional_me1_allowed`: "me2 é a opção mandatória, e me1 é a preferência de envio opcional". `optional_me2_allowed` is the reverse ("me1 é a opção padrão"). Changing it needs the commercial advisor with a justification.
- `option: "in"` = ME2 active on all listings; `trial` = some; `out` = had it, no longer; `null` = never had ME2.
- Mode mapping in the newer response: `me2` -> distribution/technology with network_provider meli; `me1` -> technology/external; `custom` -> `display_only` (i.e. ML only displays; it does not run the shipment).

Public category facts, VERIFIED 2026-11-07 (`ownship/api_api_mercadolibre_com_categories_MLB31447.txt`):
- MLB31447 "Camisetas e Regatas": `vertical: apparel`, `fragile: false`, `shipping_options: ["carrier","custom"]`, `shipping_profile: optional`, `simple_shipping: optional`, `immediate_payment: required`, `buyer_protection_programs: ["delivered","undelivered"]`, `minimum_price: 8` BRL, 6,156,564 items, `children_categories: []`.
- Comparison: MLB264052 "Outros" and MLB1055 "Celulares e Smartphones" show the identical `shipping_options` and `buyer_protection_programs`. So these fields are generic ("carrier" = ML-run carriers, "custom" = seller-defined), not proof that custom is selectable for T-shirts.
- The doc example for MLA cellphones shows `shipping_modes: ["me1","custom","me2","not_specified"]`; the BR public record for MLB31447 does not expose a `shipping_modes` field, so the T-shirt mode list must come from the authenticated `shipping_preferences` call (9).

---------------------------------------------------------------------------
## 3. ME1 (Mercado Envios 1)

### 3.1 Who can use it (VERIFIED)
- https://developers.mercadolivre.com.br/pt_br/mercado-envios-1 (updated 2026-02-06): "permite aos vendedores vender produtos pesados ou volumosos ... gerenciar a sua própria logística ou utilizar serviços de terceiros para o envio de produtos que não são elegíveis para o Mercado Envíos 2". "se um item tiver a modalidade ME2 disponível, ele não poderá ser publicado pela modalidade ME1." ME2 must already be active on the account; caps 500 cm/500 kg; activation by commercial advisor/KAM or request via the landing page.
- https://developers.mercadolivre.com.br/pt_br/me1-me2-e-frete-gratis (2026-08-14): `PUT /items` with `me1` returns 200 but the item stays `not_specified` when the account has ME2 priority; conversion may need KAM intervention. Free-shipping badge/benefits are designed for ME2; in ME1 `free_shipping:true` does not unlock the automatic frontend benefits.
- Cargoos (third-party, 2026-10-14, https://cargoos.com.br/blog/me1-mercado-livre): five account requirements cited from ML's "como ativar o ME1" note: not red reputation; listings in "entrega a combinar" that cannot go through ML shipping; active contract with a certified dynamic-freight integrator; an integration hub to migrate listings; contingency table (.xlsx up to 7 MB, review every 3 months). Quote: "Se o produto cabe no ME2, ele vai pelo ME2. O ME1 é para o que sobra." Also: ML's own ME1 page tells sellers to "parar de usar a entrega a combinar e migrar para o ME1".
- Developers doc on dynamic freight (`ownship/developers_mercadolivre_com_br_pt_br_frete_dinamico.txt`, updated 2026-09): the integrator must answer in under 400 ms with price, `handling_time` (business days; 0 if unknown) and shipping time; `promise = handling_time + shipping_time`. This is how ME1 shows freight/deadline to the buyer.

**Verdict:** ME1 does not apply to a T-shirt. Same as LABEL_BRIDGE 2.4; now corroborated by a second doc and a 2026-10 secondary source.

### 3.2 How the buyer sees cost/deadline
Freight and deadline appear in the listing once the buyer types the CEP (dynamic freight), the buyer pays product + freight at the Mercado Pago checkout (Cargoos citing ML pages; the doc's mechanism section confirms the quote flow). Third-party, consistent with the official dev doc.

### 3.3 Tracking/status API (VERIFIED, https://developers.mercadolivre.com.br/pt_br/status-de-pedidos-rastreamento, updated 2026-09-17)
`POST https://api.mercadolibre.com/v2/shipments/{shipment_id}/seller_notifications` with `status` shipped|delivered|not_delivered, optional `tracking_number` + `tracking_url` (together or neither), MLB `service_id` 11 (details in LABEL_BRIDGE 2.4). "Comunicar os status shipped e delivered é obrigatório, estando sujeito a penalidades em caso de não atualização." Delivery promise cannot be changed via API. Phone `receiver_phone` is exposed only on ME1 orders (https://developers.mercadolivre.com.br/pt_br/gerenciamento-de-envios, 2026-09-18).

### 3.4 Tools that automate it (third-party)
- Omie.HUB (2026-06-11) and UpSeller (article 288, "Atualize no 12 Aug,2026") both automate ME1 end to end: UpSeller flow "Alocar método de envio -> Programar Envio (subir o número de rastreio) -> Enviado"; automatic or manual tracking upload. UpSeller also documents "logística offline" and "outras logísticas": at "Programar Envio" you enter the shipping method name and tracking number and the order moves to Enviado (`ownship/upseller_com_pt_help_doc_article_288.txt`). This shows the tooling exists for "ship elsewhere, type a tracking number", but it presupposes an order whose shipping mode lets it.

---------------------------------------------------------------------------
## 4. custom and not_specified ("envio por conta própria", "combinar com o comprador")

### 4.1 What they are (VERIFIED)
- https://developers.mercadolivre.com.br/pt_br/envios-personalizados (updated 2024-12-10; identical text on `.com.ar/en_us/custom-shipping`, `.com.ar/es_ar/envios-personalizados`, `.com.mx/es_ar/envios-personalizados`, `.com.br/en_us/custom-shipping`): "O envio personalizado permite que os vendedores gerenciem a logística das suas vendas de maneira independente".
  - `custom`: seller uploads a price table per region (`shipping.costs[{description,cost}]`, `methods: []`) and handles all logistics and delivery.
  - `not_specified`: seller sets no freight; buyer must contact the seller to agree details and cost; "Só para esses casos, não há shipment_id".
- Constraint text (same page): "Nos países onde o modo Mercado Envios está ativo, somente poderá adicionar envios personalizados grátis em categorias que não aceitem ME." and "Se o tipo de envio não for especificado na criação do item, será 'to_be_agreed'. Se o usuário tiver a opção default ME configurada, todas as suas publicações serão criadas sob essa modalidade, com exceção daquelas que têm uma categoria que não a suporta."
- `GET /items/{id}/shipping_options?zip_code=...` shows the custom cost table to the buyer (option name, cost, `display: always`, `speed: null`), i.e. the buyer sees the seller's own price lines and no ML delivery promise.

### 4.2 Tracking/status API for custom (VERIFIED, same page)
1. Add tracking: `PUT https://api.mercadolibre.com/shipments/{shipment_id}` `{"tracking_number": ..., "receiver_id": <buyer id>}`.
2. "Entrega de produto" (doc says available only MX, BR, AR): when the order's custom shipment is `pending`: `PUT /shipments/{id}` `{"speed":120,"status":"shipped","tracking_number":1234,"receiver_id":12345678,"comments":"..."}`; `speed` is hours to deliver, promised date = hours counted from the day it is set. "O campo tracking_number é requerido para a API, mas não será em nenhuma lista e/ou detalhamento de venda." So the buyer does not see the carrier code in ML for custom; the seller should also message it.
3. Update promise only: `PUT` with `speed` and `receiver_id` while `shipped`.
4. Delivered: `PUT {"status":"delivered","receiver_id":...}` (can go back to pending/shipped).
5. Cancel: `POST /shipments/{id}` `{"status":"cancelled","receiver_id":...}` (terminal).
6. State machine: Pending -> Shipped | Delivered | Cancelled; Shipped -> Delivered; Delivered -> Pending | Shipped; Cancelled is terminal.
This is the API you would call to "just report the tracking code". It works; the open question is only whether a T-shirt listing can be created in this mode.

### 4.3 Official help for the not_specified flow (VERIFIED, https://www.mercadolivre.com.br/ajuda/827 "Como posso fazer o envio por conta própria?", fetched 2026-11-07)
- Options: deliver in person; agree buyer pickup at the seller's establishment; "Enviar o produto por uma agência conveniada. Nesse caso, lembre-se de compartilhar o código de rastreamento com o comprador".
- Safety: use only the sale messages; confirm the order is in the sales list; ship in the buyer's name; keep the agency receipt (address + date); for hand delivery get a signed form with operation number, product title, date, name, ID.
- Payment: "Ao enviar o pacote, marque 'Avisar entrega' pela lista de vendas." ML emails the buyer to confirm; until completion the sale shows "A caminho" and the money stays retained in Mercado Pago; once the buyer confirms, the sale detail shows the exact release date.
- "Se alguém fizer uma reclamação ou contestar o pagamento feito com cartão de crédito, os pontos acima te ajudarão" (this is the seller-protection evidence trail).
- Note: the 3030 help id returned an unrelated "não será possível entregar esta encomenda" page; the 3142/1182/3212/1041 help ids from guesses were 404 or blocked. The ML help centre is otherwise behind a verification wall.

### 4.4 Is it offered for T-shirts? What the evidence says
- VERIFIED that it is allowed in principle for all sellers (5.2 above) and for categories without ME.
- Evidence it is NOT offered where ME exists: 5.3, 5.4, 5.5 (all sections below).
- Evidence that ML nudges existing not_specified items to ME2: tag `adoption_required` (VERIFIED, https://developers.mercadolivre.com.br/pt_br/publicacao-de-produtos, updated 2026-01-09): "Item not_specified que ainda não adotou o ME2, que é o recomendado."
- UpSeller MX/Latam blog (https://upseller.com/es/blog-article-130, 2024-11-25, third-party, written for Mexico): products "no elegibles" for ME (very big/heavy, fragile/high-value, dangerous, regulated, live) must use "envíos personalizados" or "acordar con el vendedor"; "no existe un proceso formal para que los vendedores soliciten la inclusión de sus productos en Mercado Envíos". The same logic implies the reverse: an eligible product has no formal opt-out.
- SuperFrete (third-party freight reseller with an interest in the claim, 2026-02-03, https://superfrete.com/blog/transportadora-do-mercado-livre): "os lojistas não são mais obrigados a usar essa estrutura, como era antigamente ... podem optar por enviar os pedidos por conta própria". No mechanism, no category or ME2 condition, and it contradicts the official-quoted sources; **UNVERIFIED and weaker than the others.**
- Bling blog (https://blog.bling.com.br/mercado-envios-o-que-e-como-funciona/, fetched 2026-11-07, undated): lists "postagem nos Correios; coleta; envio próprio" and says envio próprio is "desde que autorizado pelo Mercado Livre (geralmente para produtos grandes, frágeis ou com regras especiais). Deve ser previamente aprovado pela plataforma e o vendedor precisa informar o código de rastreio no sistema. O prazo de entrega deve ser igual ou menor que o do Mercado Envios tradicional." Third-party, imprecise (blends ME1 with custom), but consistent with the conditional picture.

---------------------------------------------------------------------------
## 5. Evidence log (what each independent source says)

### 5.1 ML public category API (VERIFIED, 2026-11-07, runner probe)
See section 2. Not discriminating for custom.

### 5.2 ML developer doc, shipping preferences (VERIFIED, 2026-06-09)
"Lembrar que todos os vendedores têm habilitado custom e not_specified por padrão." URL https://developers.mercadolivre.com.br/pt_br/mercado-envios. English mirror with the same statement: `developers.mercadolivre.com.br/en_us/ship-products` (fetched 2026-11-07).

### 5.3 ML developer doc, custom shipping (VERIFIED, 2024-12-10)
Section 4.1 quotes. The doc is old (written for MLA with an Argentine example) but is still the current "Envios Personalizados" page in the 2026 navigation.

### 5.4 Reclame Aqui complaint (VERIFIED text; 2023-04-29; ID 163766681; "Não resolvido"; flagged "mais de 3 anos")
https://www.reclameaqui.com.br/mercado-livre/obrigatoriedade-de-envio-pelo-mercado-envios_YgglmEux9-zqDZOy/ — seller wanted another, cheaper carrier. Reply attributed to ML on WhatsApp case 252220803: "Todos os vendedores ... agora usam o Mercado Envios nas categorias em que o serviço estiver disponível, para que a experiência aos compradores seja ainda mais completa, por isso, não será possível desativar o serviço para o envio dessa sua venda." / "Caso o envio seja postado por sua conta, não conseguimos estornar o valor da etiqueta." Other Reclame Aqui titles found (`obrigatoriedade-de-uso-do-mercado-envios`, `nao-consigo-tirar-o-mercado-envios`, `entrega-a-combinar`) returned 403 to the runner, so their text is **UNVERIFIED** (titles only, from search).
Caveat: single complaint, user-reported chat transcript, 2023.

### 5.5 Cargoos (third-party, 2026-10-14)
https://cargoos.com.br/blog/me1-mercado-livre. Summarises ML pages (Central de Vendedores notes, ME1 landing, developer docs). Relevant, quoted:
- Comparison table: ME2 = "Sempre que o produto for elegível"; ME1 = "Produto fora do ME2"; Entrega a combinar = "Produto fora do ME2, sem ME1 ativo".
- "Algumas categorias, pela natureza do produto, só aceitam entrega a combinar, segundo a ajuda sobre dimensões permitidas." (so a category list exists; apparel is not named).
- FAQ "Como colocar frete a combinar no Mercado Livre?": "Só dá para usar em produtos que não são elegíveis ao Envios do Mercado Livre, pela categoria ou pelo tamanho e peso. Com o Envios ativo na conta, os anúncios são criados nele, exceto em categorias que não o aceitam."
- Payment release (summarising ML's table, which I could not open): sales with Envios do Mercado Livre are released "de 8 a 12 dias após a entrega"; hand delivery or other service "de imediato a 28 dias conforme o aviso de entrega e a confirmação do comprador". **UNVERIFIED against the ML table**; Bling (same fetch set) says the sale amount is held until the buyer confirms and released automatically after 7 days if no problem. The two third-party numbers disagree, so treat release timing as "must read ML's table in the account".
- Seller protection for hand/own delivery: the "Programa de Proteção ao Vendedor" coverage depends on the signed delivery form (matches ML help 827).

### 5.6 Other independent sources, what they add
| Source | Date | Relevant statement | Label |
|---|---|---|---|
| Nuvemshop blog https://www.nuvemshop.com.br/blog/dropshipping-mercado-livre/ | fetched 2026-11-07, undated | "vendedores do Mercado Livre geram as etiquetas e as enviam ao fornecedor, para que ele as imprima, cole nas embalagens e poste a mercadoria em uma agência do Mercado Envios." Also: "a plataforma costuma favorecer seu próprio sistema de entregas, o Mercado Envios" | VERIFIED text, third-party |
| ecommercenapratica https://ecommercenapratica.com/blog/como-vender-no-mercado-livre-dropshipping-fornecedor/ | fetched 2026-11-07 | dropship needs the supplier's address registered as sender; Brazil only; one supplier at a time; no Full; strict dispatch deadlines | VERIFIED text, third-party |
| ecommercenapratica https://ecommercenapratica.com/blog/dropshipping-no-mercado-livre | fetched 2026-11-07 | one ship-from address per account; "informe o código de rastreio aos clientes" via ML messages | VERIFIED text, third-party |
| Tray https://tray.com.br/escola/dropshipping-mercado-livre/ | fetched 2026-11-07 | PF seller may have limited NF-e and shipping-mode tools "Segundo o próprio Mercado Livre"; CNPJ recommended | VERIFIED text, third-party |
| Mercado Pago blog https://www.mercadopago.com.br/blog/empreendedorismo-digital-no-mercado-livre | fetched 2026-11-07 | ML itself says buyers see the seller as responsible; dropship "não elimina obrigações do vendedor"; delivery "diretamente ou por um fluxo combinado com você" | VERIFIED text, ML group |
| Bling dropship blog https://blog.bling.com.br/vender-no-mercado-livre-sem-estoque-com-dropshipping/ | fetched 2026-11-07 | "dropshipping ... aceito pelo Mercado Livre"; align supplier lead time; "Habilite o Mercado Envios" | VERIFIED text, third-party |
| UpSeller 288 (Brazil) | 2026-08-12 | offline/other-logistics order flow with manual tracking upload; "retiradas pessoalmente e pedidos enviados por vendedor" flow ("O comprador já está com ele em mãos") | VERIFIED text, third-party |
| UpSeller 1585 | 2025-07-08 | ME1 = seller picks carrier, makes labels, uploads freight table; ME2 = ML automated. Contradicts the official order of ME2/ME1 activation (already noted in LABEL_BRIDGE 2.4) | third-party, partly contradicted |
| Omie.HUB help | 2026-06-11 | ME1 flow; ME2-eligible listings cannot be ME1 | VERIFIED text, third-party |
| Nubimetrics https://academia.nubimetrics.com/pt/mudancas-mercado-livre | fetched 2026-11-07 | general platform changes; nothing on own shipping | no relevant content |
| hunterhub dropshipping blog | - | HTTP 429 from the runner | UNVERIFIED (not read) |
| YouTube transcripts | - | Not retrievable from the runner or the search tool; **no YouTube evidence obtained** | UNVERIFIED |
| ML Community (comunidade.mercadolivre.com.br) | - | host does not resolve; no community thread retrieved | UNVERIFIED |
| tecnoblog forum threads | - | 403 | UNVERIFIED |

---------------------------------------------------------------------------
## 6. Reputation, penalties, protections (what applies to each choice)

VERIFIED unless stated.
- **Reputation doc** (https://developers.mercadolivre.com.br/pt_br/reputacao-de-vendedores, updated 2025-08-11): the thermometer uses cancellations, claims and delayed handling time. Claims count "sem diferenciar a modalidade de envio nem o pagamento". Delayed handling time "Só consideraremos os vendedores que utilizarem Mercado Envios e tiverem 10 ou mais vendas enviadas. Os outros não serão atingidos por esta métrica"; formula `delayed handling time rate = vendas com envio atrasado / vendas enviadas com me2`; window 60 days (365 if under 60 sales in MLB). Handling time = `ready_to_ship` to carrier "shipped" scan. So a seller who never uses ME has no dispatch-delay metric, but cancellations and claims still bite.
- **Dispatch SLA** (https://developers.mercadolivre.com.br/pt_br/gerenciamento-de-envios, 2026-09-18): `GET /shipments/{id}/sla`; dispatching after the limit "impactará em demoras que afetarão na sua reputação e destaques".
- **ME1 status duty** (2026-09-17): shipped/delivered reporting mandatory, "sujeito a penalidades em caso de não atualização".
- **Cancellations:** Bling (https://blog.bling.com.br/cancelar-venda-no-mercado-livre/, fetched 2026-11-07, cites ML): above 2.5% cancellations may bring temporary sales suspension or loss of exposure (third-party). The earlier ecommercenapratica figures (claims 1%, mediations 0.5%, delays 6%) are third-party too.
- **Buyer protection ("Compra Garantida"/"Compra protegida")**: https://www.mercadolivre.com.br/seguranca (fetched 2026-11-07): when a buyer pays, "ele [vendedor] não pode usar o dinheiro imediatamente. Assim, se você tem algum problema com a compra, podemos devolver seu dinheiro"; ML says "Todos os envios são rastreados desde que são despachados até que sejam entregues". With custom/not_specified there is no ML tracking, so the evidence trail is the seller's receipt/tracking and the sale messages (help 827). Category setting `buyer_protection_programs: ["delivered","undelivered"]` for MLB31447 (public API) means both "not received" and "received different" protections apply to T-shirts irrespective of mode (interpretation of field names, **UNVERIFIED**).
- **Payment release:** held until delivery confirmation; with ME release is computed from delivery scans; with own delivery the buyer's confirmation or the "Avisar entrega" notice drives it (help 827). Exact day counts differ between sources (5.5), so **UNVERIFIED**.
- **Label cost if you ship ME with someone else's label:** not refunded (5.4 quote).
- **Penalty for using a non-ML carrier on an ME2 shipment:** no text found; **UNVERIFIED**.

---------------------------------------------------------------------------
## 7. Who can use what (CPF / MEI / CNPJ / reputation / minimum sales)

- No official page found that gates custom or not_specified by CPF vs CNPJ, reputation or sales count. The dev doc says all sellers have them enabled (5.2).
- ME2 drop_off and agency: all sellers; Coleta/Places: activation reviewed weekly against delivery performance (VERIFIED, https://developers.mercadolivre.com.br/pt_br/envios-coletas-places, 2026-09-25, per LABEL_BRIDGE).
- ME1: not-red reputation, ME2 active, certified integrator and contingency table (Cargoos, third-party summary of ML notes). Reputation levels beyond "not red" and minimum-sales thresholds: **UNVERIFIED**.
- Flex: only 7 metro regions, own stock, app required, not integrable (VERIFIED, https://developers.mercadolivre.com.br/pt_br/envios-flex, 2026-10-15). Envios Agora: own stock, 25-min SLA, since 2026-06-06 (VERIFIED, https://developers.mercadolivre.com.br/pt_br/mercado-envios-agora, 2026-06-10).
- Full: ML warehouse; "No dropshipping, você não pode usar o Mercado Livre Full" (ecommercenapratica, third-party). Made-to-order has no pre-stock, so Full is out.
- PF (CPF) sellers have "acesso limitado a algumas ferramentas relacionadas à emissão de NF-e e modalidades de envio" (Tray citing ML; third-party). MEI as "contribuinte" vs "não contribuinte": **UNVERIFIED** (open question in LABEL_BRIDGE 4E).
- T-shirt category minimum price BRL 8 (public API); no minimum-sales rule for the category found.

---------------------------------------------------------------------------
## 8. Made-to-order and dropshipped goods with a supplier's label: accepted in practice?

1. **Dropshipping itself is accepted** by ML as a business model but the seller stays accountable (Bling, Tray, Mercado Pago blog, Nuvemshop, ecommercenapratica above; the Mercado Pago blog is ML group). Not found: an ML policy page banning it.
2. **Supplier's own label on an ME2 sale: no evidence it is accepted.** Every practical guide describes the opposite: the seller creates the ML label, the supplier prints it and posts at an ML agency (Nuvemshop), with the supplier's address registered as sender (ecommercenapratica). ME2 labels are ML-network documents; "não é permitido criar etiquetas personalizadas para nenhum vendedor" (VERIFIED, LABEL_BRIDGE 2.2).
3. **Made-to-order lead time is a supported concept.** The items doc (https://developers.mercadolivre.com.br/pt_br/itens-atributos-de-envio-e-dimensoes, updated 2026-08-14) states the `sale_terms` attribute `MANUFACTURING_TIME` must be a non-null integer of manufacturing days (0 if immediately available) or publication is blocked. That gives a legitimate place to declare 3-5 days of production; the maximum allowed value for MLB31447 is **UNVERIFIED** (the category `sale_terms` endpoint is 403 without a token; `attributes` list truncated at 20 kB in my probe did not reach it). Whether delayed-handling metrics count production days or only `ready_to_ship` -> shipped is per the reputation doc: handling time starts at `ready_to_ship`, so production before that status is not penalised by that metric (interpretation, **UNVERIFIED** in an account).
4. **Reports of sellers shipping T-shirts with a non-ML carrier and posting the code:** none found. Montink's claim to "integrate with Mercado Livre" remains unexplained (LABEL_BRIDGE 3.7).

---------------------------------------------------------------------------
## 9. How to confirm in a real account without selling anything

Order of cost (all read-only or paused-draft; none creates a sale, none touches a buyer). Needs the owner's ML developer app + seller token (the owner creates it; I created nothing).

1. **UI check (no code):** Vender -> Publicar, category Camisetas e Regatas, fill the listing until the "Envio" step. Record exactly which shipping options appear (Mercado Envios only? any "Combinar com o comprador/Envio por sua conta", "Retirada pessoal"?). Do not publish; save as draft or abandon. Screenshot for the record.
2. `GET /users/{USER_ID}/shipping_preferences` -> read `modes`, `option` (in/out/trial/null), `tags` (`optional_me1_allowed` or `optional_me2_allowed`), `me2_enablers`, `local_pick_up`. If `option` is `in` and `modes` contains `me2`, T-shirts will be forced to ME2.
3. `GET /categories/MLB31447/shipping_preferences` -> `logistics[]`: which `mode`s are listed (me1, me2, not_specified, custom) and `me2_restrictions`/`restricted`. For T-shirts expect `restricted: false`, `me2_restrictions: null` (ME2 fully available). If `restricted: true` or ME2 missing, custom/not_specified opens.
4. `POST /users/{USER_ID}/shipping_modes` (headers `x-multichannel: true`, `X-Format-New: true`) with a T-shirt payload (category MLB31447, price, catalog attributes from `/categories/MLB31447/attributes`, package dimensions in cm/g). The response lists the logistic types ML will allow for exactly this item and seller. This is the ML-documented pre-publication check.
5. **Draft listing test:** `POST /items` with `"shipping":{"mode":"custom","local_pick_up":false,"free_shipping":false,"methods":[],"costs":[{"description":"Entrega do fornecedor","cost":"18"}]}` (and, separately, `"mode":"not_specified"`), then `GET /items/{id}` and read back `shipping.mode`, `shipping.logistic_type`, `shipping.tags` (`me2_available`, `adoption_required`, `lost_me2_by_dimensions`). Pause immediately (`status: paused`) and close; if ML silently converts it to `me2`, the answer is "not selectable". Keep price high or stock 0 variations unavailable so it cannot sell; alternatively use an ML test user (the nav lists "Realização de testes"; API for test users: **UNVERIFIED here**, not read).
6. **Final authority:** developer ticket or seller support/KAM with the exact question from LABEL_BRIDGE 4E.1 (can a CNPJ/MEI seller list apparel as custom/not_specified; consequences for reputation, exposure and free shipping; sanction for a non-ML carrier on ME2).
7. **Do not** try to dodge ME2 by entering fake oversize dimensions (tag `lost_me2_by_dimensions` exists precisely to catch that; it would also misprice freight and risk ToS action). Not tested, not recommended.

---------------------------------------------------------------------------
## 10. Verdict per question

| Question | Answer | Basis |
|---|---|---|
| Can a seller ship himself with his own carrier and report tracking to ML? | Yes in categories/items where ML shipping is not available (custom/not_specified, plus ME1 for heavy). Tracking APIs verified. | 3.3, 4.2, 5.2 |
| For T-shirts MLB31447? | Probably not selectable: ME1 barred for ME2-eligible items; custom/not_specified listings are created as ME where the category accepts ME; ML support says ME cannot be switched off. Exact behaviour for this account/category is UNVERIFIED until the section-9 checks. | 3.1, 4.1, 5.4, 5.5 |
| Can the supplier ship with its own carrier/label and we paste tracking? | Not as an ML-sanctioned ME2 flow. As a custom/not_specified shipment: only if the listing can be created in that mode. | 4, 8 |
| What happens if we do it anyway on ME2? | ME label cost lost; no ML delivery events; dispatch/claim/cancel exposure; sanction text not found. | 5.4, 6 |
| Buyer-visible freight/deadline | ME2: ML quote and promise. ME1: dynamic quote from integrator. custom: seller's own cost lines, `speed` hours set at ship time. not_specified: nothing, buyer must ask. | 3.2, 4.1, 4.2 |
| Payment release | Held until delivery/confirmation; ME uses carrier scans, own delivery uses "Avisar entrega"/buyer confirmation; day counts disagree between sources. | 4.3, 5.5 |
| Made-to-order | `MANUFACTURING_TIME` days is a supported listing field; label/tracking route stays the open problem. | 8 |
| Implication for Dimona | Dimona will not take ML's label (LABEL_BRIDGE 1.1) and ME2 does not accept Dimona's. Realistic options: (a) own site; (b) a supplier or in-house packer that accepts ML's label; (c) test custom/not_specified (section 9); (d) accept that ML T-shirt listings need ME2 and put a repacking step in between. Do not rely on a 2023 chat transcript or one freight vendor's blog either way. | 0, 5 |

---------------------------------------------------------------------------
## 11. Files and reproduction

- Probe code: `scripts/brazil/probe.py` task `ownship` (URL list in `scripts/brazil/ownship_urls.txt`, last list overwritten per run; each run's outputs stay committed). Workflow: `gh api -X POST repos/Rodantmat/Alphadog-Styles/actions/workflows/brazil-probe.yml/dispatches -f ref=main -f 'inputs[task]=ownship'`.
- Raw evidence: `docs/brazil_data/ownship/*.txt`. Most important: `developers_mercadolivre_com_br_pt_br_mercado_envios.txt` (modes, preferences endpoints), `..._envios_personalizados.txt`, `..._mercado_envios_1.txt`, `..._me1_me2_e_frete_gratis.txt`, `..._status_de_pedidos_rastreamento.txt`, `..._reputacao_de_vendedores.txt`, `www_mercadolivre_com_br_ajuda_827.txt`, `www_reclameaqui_com_br_mercado_livre_obrigatoriedade_de_envio_pelo_mercado_envios_*.txt`, `cargoos_com_br_blog_me1_mercado_livre.txt`, `upseller_com_pt_help_doc_article_288.txt`, `api_api_mercadolibre_com_categories_MLB31447.txt`.
- Blocked or empty (so UNVERIFIED): `/users/{id}/shipping_preferences` and `/categories/{id}/shipping_preferences` and `/sites/MLB/shipping_methods` (403 without token), `/categories/MLB31447/sale_terms` (403), ML help centre pages other than id 827, ML community, Reclame Aqui pages other than one, tecnoblog threads, hunterhub (429), YouTube.
- The `www.mercadolivre.com.br/a/store/mercado-envios-1` landing redirects to an account-verification wall for the runner and is robots-disallowed for the fetch tool; its content is known only through Cargoos' summary.

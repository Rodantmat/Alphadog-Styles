# Preços BR (pt-BR) - método "proporcional" e tabela final
Data: 2026-11-08 (Pacific). Branch `br-site-2`. Código: `br/scripts/br_pricing.py` (única fonte; `--write` grava em `br/config/br_config.json` > `pricing.models`; `br/tests/test_pricing.py` trava a tabela).
Legenda: **V** = verificado em arquivo/página do repo; **U** = não verificado / suposição.

## 1. O que a loja dos EUA faz de fato (V, lido do repo)
| Item | EUA | Fonte |
|---|---|---|
| Camiseta Premium (Bella+Canvas 3001), 1 lado | **US$ 27,99**; 2 lados 32,99; 2XL +2,00; 3XL +4,00 | `store/data/catalog.json` |
| Moletom (Gildan 18500), 1 lado | **US$ 49,99**; 2 lados 57,99; 2XL +4,00; 3XL +8,00 | idem |
| Custo Printify camiseta BC3001, 1 lado | **US$ 11,29** (2XL 13,82, 3XL 16,12) | `out/fabric2.json` |
| Custo Printify moletom, 1 lado | **US$ 21,58** (2 lados 27,90) | `out/costs.json` |
| Múltiplo preço/custo | camiseta **2,479x**, moletom **2,316x** | 27,99/11,29 e 49,99/21,58 |
| Final de preço | sempre **,99**; frete grátis acima de US$ 75, senão US$ 4,99 (frete embutido) | `catalog.json`, `store/js/app.js` |
| Preço "de" (riscado) | **não existe** na loja dos EUA (busca em todo `store/`: zero ocorrências). O "de/por" é um recurso de marketing só do Brasil, definido pelo dono (139,90 -> 109,90) | grep |
| Margem EUA | camiseta ~US$ 15,6 líquido (59,7% sobre o preço antes da taxa Stripe) (U: taxa Stripe 2,9%+0,30) | cálculo |

Observação: o custo 2 lados da BC3001 (~US$ 17,20) é derivado (custo Gildan 16,01 + 1,20 da troca de malha, memória do dono); não é usado na tabela BR porque cada produto BR é de **um lado** (SKU `-F-` ou `-B-`).

## 2. Custos Gubo (V, `docs/brazil_data/BR_PRODUCERS.md` 3.1 e probe 2026-11-07)
Peça lisa (preço Pix): Padrão 39,90 | Oversized 58,90 | Tech Modal 54,90 | Babylook 39,90 | Cropped 25,90 | Infantil 25,90 | Moletom capuz 2 cabos 99,90 | 3 cabos 129,90 | sem capuz 78,90 | Ecobag 25,90 | Pet 25,90.
Estampa por área (qualquer cor): pequena 5,90 (até 350 cm2) | média 8,90 (700) | grande **11,90** (1.050) | mega 16,90 (1.400). Etiqueta personalizada **+1,50** (o dono exige a etiqueta). Cartão ≈ +5,27% sobre o Pix (V só para o Padrão: 51,80 Pix -> **54,53 cartão**, medido no probe; para os outros modelos é suposição **U**).
Frente e costas custam o mesmo se a arte couber em 1.050 cm2 (U: se a arte das costas passar disso o Gubo cobra "mega" +5,00; a tabela foi testada também nesse pior caso e continua acima do piso). Frete: pago pelo cliente (cotação ao vivo do Gubo), não entra no preço.

## 3. Fórmula (não é conversão de câmbio)
1. **C** = (peça + estampa + etiqueta) x 1,0527  (custo no cartão, o mais conservador; o Pix do Gubo sai ~5% mais barato e recarregar a carteira por Pix tem 5% de desconto).
2. **De** (riscado) **L** = C x **K**, arredondado **para cima** ao próximo ,90. K = múltiplo dos EUA: **2,479** (camisetas, ecobag, pet) ou **2,316** (moletons).
3. **Por** (preço de venda) **P** = L x **0,7856** (= 109,90/139,90, a razão do dono, ~21,4% de "desconto"), arredondado ao ,90 mais próximo.
4. **Piso**: P ≥ 1,15 x C **e** ainda ≥ 1,15 x C depois da taxa do cartão (4,98%, U). Se não, sobe ao próximo ,90. (Nenhum modelo precisou.)
5. **Teto de mercado** só para acessórios (ecobag e camiseta pet): R$ 59,90 (U: no estudo, camisetas de raça/pet na Amazon BR têm mediana R$ 55-62; a fórmula daria 76,90 / 59,90 de "De" e 80,90 / 74,90 de "Por" sem o teto).
6. **XG/XGG** = parcela do preço que a loja dos EUA cobra no 2XL (200/2799 camiseta, 400/4999 moletom) x P, em reais inteiros (mantém o ,90). Custo Gubo XG/XGG no Padrão: +8,42 (V).
Checagem de coerência: o método **reproduz sozinho o R$ 139,90 / R$ 109,90 do dono** para o Padrão (C 56,11 x 2,479 = 139,1 -> 139,90; x 0,7856 = 109,90).

## 4. Tabela final (R$; "Por" é o preço da loja; cor clara = escura; frente = costas)
| Cod | Modelo | Custo c/ etiqueta (cartão) | De (riscado) | **Por** | Piso (15% + taxa) | XG/XGG | Lucro após taxa (sobre custo) |
|---|---|---|---|---|---|---|---|
| PD | Camiseta Padrão | 56,11 | 139,90 | **109,90** | 68,90 | +8 | 48,32 (86%) |
| OV | Camiseta Oversized | 76,11 | 188,90 | **147,90** | 92,90 | +11 | 64,42 (85%) |
| TM | Camiseta Tech Modal | 71,90 | 178,90 | **140,90** | 87,90 | +10 | 61,98 (86%) |
| BL | Babylook | 56,11 | 139,90 | **109,90** | 68,90 | - | 48,32 (86%) |
| CR | Cropped | 41,37 | 102,90 | **80,90** | 50,90 | - | 35,50 (86%) |
| KD | Camiseta Infantil | 38,21 | 94,90 | **74,90** | 46,90 | - | 32,96 (86%) |
| H2 | Moletom c/ capuz 2 cabos | 119,27 | 276,90 | **217,90** | 144,90 | +17 | 87,78 (74%) |
| H3 | Moletom c/ capuz 3 cabos | 150,85 | 349,90 | **274,90** | 182,90 | +22 | 110,36 (73%) |
| HS | Moletom sem capuz | 97,16 | 225,90 | **177,90** | 117,90 | +14 | 71,88 (74%) |
| EC | Ecobag | 41,37 | 76,90 | **59,90** (teto) | 50,90 | - | 15,55 (38%) |
| PT | Camiseta Pet | 38,21 | 76,90 | **59,90** (teto) | 46,90 | - | 18,71 (49%) |
Todos acima do piso de 15%, inclusive se o Gubo cobrar a estampa como "mega" (testado). Estampas médias (Infantil, Pet = 8,90) e as demais categorias de tamanho/área dos outros modelos são **U** até o Gubo confirmar; o `br-catalog-sync` agora avisa `PRICE BELOW FLOOR` se o custo real lido da API ficar acima do piso para qualquer tamanho.

## 5. Sanidade e pontos que o dono precisa ver
- Em dólar (R$ 5,45-5,50 por US$ em 3-4/nov/2026, V manchete brasil61): R$ 109,90 ≈ US$ 20,2 = 72% do preço dos EUA (27,99), enquanto o custo Gubo (R$ 56,11 ≈ US$ 10,3) é 91% do custo Printify (11,29). Ou seja, o preço BR é proporcional ao **custo** local, não ao câmbio (converter dava R$ 154).
- O múltiplo de venda real fica em **1,96x** do custo (109,90/56,11) contra 2,48x nos EUA: o "desconto" de 21% sai da margem. O preço "De" (139,90) é o múltiplo cheio dos EUA. Lucro por camiseta ≈ R$ 48 (≈ US$ 8,9) contra ≈ US$ 15,6 nos EUA; sem frete grátis no Brasil (o cliente paga o frete). **Alternativa** se o dono preferir o mesmo múltiplo dos EUA sem "desconto": vender a R$ 139,90 (coluna "De").
- Comparação de mercado (U, não consegui abrir páginas de varejistas aqui): estudo anterior: camisetas R$ 50-100 em marketplaces, mediana Amazon BR de camiseta de raça R$ 61,80; faixa de moda de marca (Reserva etc.) é maior. R$ 109,90 fica acima do marketplace comum e na faixa de marca; confirmar olhando 5 concorrentes antes do lançamento.
- Taxas Mercado Pago (Pix 0,99%, cartão à vista 4,98%) são de fonte secundária (U); parcelado em 12x custa bem mais e **não** está no piso: se o dono oferecer parcelamento sem juros, rodar de novo com a taxa certa (muda uma constante: `FEE_CARD`). Impostos: MEI (DAS fixo) não incide por venda; como ME (Simples ~4%) o lucro cai ~R$ 4-6 no Padrão (U).
- Tamanhos dos outros modelos (P/M/G/GG, infantil 2-14, ecobag "UN") são suposição até o sync ler o Gubo.

# Montink para WooCommerce

Integração de **dropshipping** entre WooCommerce e a plataforma [Montink](https://montink.com). O plugin sincroniza o catálogo da Montink, cria produtos variáveis e variações vinculadas, calcula frete na página do produto e no checkout, envia pedidos pagos à Montink e recebe atualizações de status via webhook.

> **Aviso**: projeto independente. Não é afiliado à Tshirtness nem à Montink. O nome "Montink" é usado apenas para identificar a plataforma integrada.

## Recursos

- **Sincronização de catálogo**: importa produtos Montink agrupados por nome, cria/atualiza produtos variáveis com variações de **Modelo × Tamanho × Cor**, cada uma vinculada ao produto Montink correspondente.
- **Imagens**: baixa os mockups (por modelo e por cor) para a biblioteca de mídia e os atribui às variações.
- **Filtro de variações**: na página do produto, esconde tamanhos/cores que não pertencem ao modelo selecionado.
- **Frete Montink**:
  - Método de envio WooCommerce *Frete Montink* (preço + prazo por modalidade, com cache).
  - Calculador na página do produto consultando a API Montink via REST (sem depender de AJAX).
  - O pedido envia o `shipping_id` exato escolhido pelo cliente.
- **Pedidos**: envia automaticamente pedidos pagos (`processing`/`completed`) à Montink via `create_order` (CPF/CNPJ, endereço completo, data de nascimento), armazena ID/status/rastreio e recebe atualizações via webhook REST.
- **Sincronização em pedaços**: o sync roda em chunks com barra de progresso para evitar timeouts (504).

## Requisitos

- WordPress 6.5+ · PHP 8.1+
- WooCommerce ativo
- Conta Montink com token da API (Dashboard → Adicionar Apps → API Montink → Conectar → Gerar token)

## Instalação

1. Baixe o plugin e envie em **Plugins → Adicionar novo → Enviar plugin** (ou copie a pasta em `wp-content/plugins/`).
2. Ative o plugin.
3. Em **Montink → Configurações**, cole o token da API e escolha a forma de pagamento dos pedidos (`pix`, `saldo` ou `boleto`).
4. Em **Montink → Sincronização**, clique em **Executar sincronização** para importar o catálogo.
5. Em **WooCommerce → Envio → Zonas**, adicione o método **Frete Montink** à sua zona e desative outros métodos se quiser.
6. Clique em **Cadastrar webhook na Montink** (nas configurações) para receber atualizações de status.

## Configuração

### Campos de checkout brasileiros

A API Montink exige CPF/CNPJ, bairro e número no endereço. O plugin lê as chaves padrão usadas por plugins brasileiros de checkout (ex.: *Calculadora de Frete e Campos Checkout para o Brasil*, *Brazilian Market*):

- `_billing_cpf` / `_billing_cnpj` / `_billing_document`
- `_billing_number` / `_billing_neighborhood` (e `_shipping_number` / `_shipping_neighborhood`)
- `_billing_birthdate`

Caso seu checkout use outro nome de campo, ajuste `TSM_Orders::document()` em `includes/class-tsm-orders.php`.

### Endpoints REST do plugin

| Rota | Método | Descrição |
|---|---|---|
| `/wp-json/tsm/v1/webhook` | POST | Recebe atualizações de status enviadas pela Montink |
| `/wp-json/tsm/v1/shipping?cep=01310100&qty=1` | GET | Opções de frete da Montink (página do produto) |

## API Montink utilizada

| Endpoint | Uso |
|---|---|
| `GET /products` | Listagem do catálogo |
| `GET /product/{id}` | Detalhe do produto (variações, preços, imagens) |
| `GET /calculate_shipping/{cep}/{qtd}` | Cálculo de frete |
| `POST /create_order` | Importação do pedido |
| `POST /webhook` | Registro da URL de webhook |
| `GET /order/{id}` | Detalhe/status do pedido |

Documentação oficial: https://admin.montink.com/apiMontink/docs

## Estrutura

```
tshirtness-montink/
├── tshirtness-montink.php        # Bootstrap do plugin
├── assets/
│   ├── css/tsm-shipping.css      # Estilo do calculador de frete
│   └── js/                       # Filtro de variações + calculador de frete
└── includes/
    ├── class-tsm.php             # Container principal
    ├── class-tsm-api.php         # Cliente da API Montink
    ├── class-tsm-attributes.php  # Atributos/variations WooCommerce
    ├── class-tsm-settings.php    # Página de configurações
    ├── class-tsm-sync.php        # Sincronização do catálogo (chunked)
    ├── class-tsm-orders.php      # Pedidos + webhook
    └── class-tsm-shipping.php    # Método de envio + calculador REST
```

## Desenvolvimento

### Changelog

**0.7.0** — Calculador de frete Montink na página do produto (REST) + método de envio *Frete Montink* com preço e prazo.
**0.6.0** — Método de envio WooCommerce consultando a API de frete da Montink.
**0.5.x** — Fase de pedidos: envio automático, webhook de status e meta box no pedido.
**0.4.0** — Sync em pedaços com barra de progresso (sem 504) e download de imagens.
**0.3.0** — Download de imagens, filtro de variações e threshold de variações.
**0.2.1** — Variações com atributos persistidos e preço por modelo.
**0.1.0** — Sincronização básica do catálogo.

### Validar sintaxe

```bash
for f in tshirtness-montink.php includes/*.php; do php -l "$f" || exit 1; done
```

## Licença

GPL-2.0-or-later. Veja [LICENSE](LICENSE).

---

**Autor**: [Sulivan Rodrigues](https://github.com/noxsulivan)
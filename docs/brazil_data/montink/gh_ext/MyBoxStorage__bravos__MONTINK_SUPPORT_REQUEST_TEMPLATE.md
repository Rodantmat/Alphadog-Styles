# Template de Solicitação de Suporte - API Montink

## Assunto
Solicitação de Documentação da API Pública para Criação de Pedidos

---

## Mensagem

Olá equipe Montink,

Estamos desenvolvendo uma integração com a API pública da Montink (api.montink.com) e precisamos de informações sobre o endpoint para criação de pedidos.

**Contexto:**
- Estamos integrando nosso sistema de e-commerce com a plataforma Montink
- Já utilizamos com sucesso os endpoints GET documentados:
  - `GET /order/{IDPEDIDO}` - Buscar pedido
  - `GET /products` - Listar produtos
  - `GET /calculate_shipping/{CEP}/{QTD}` - Calcular frete

**Solicitação:**
Precisamos da documentação oficial do endpoint para **criar pedidos** via API, incluindo:

1. **Método HTTP:** POST, PUT ou outro?
2. **Path/Endpoint:** Qual é o caminho completo? (ex: `/order`, `/orders`, `/api/order`)
3. **Autenticação:** 
   - Header necessário? (ex: `Authorization: Bearer {token}` ou `Authorizationtoken: {token}`)
   - O token usado é o mesmo `MONTINK_API_TOKEN`?
4. **Request Body:**
   - Quais campos são obrigatórios?
   - Estrutura JSON esperada
   - Exemplo de payload completo
5. **Response:**
   - Estrutura da resposta de sucesso
   - Campos retornados (especialmente o ID do pedido criado)
   - Códigos de status HTTP e tratamento de erros

**Informações Adicionais:**
- Estamos usando integração server-to-server (backend Node.js/Express)
- Precisamos criar pedidos automaticamente quando pagamentos são confirmados
- Temos todos os dados necessários: endereço completo, itens (productId + quantity), dados do cliente

**Contato:**
- Email: [SEU_EMAIL]
- Empresa: BRAVOS BRASIL
- Sistema: E-commerce integrado com Mercado Pago

Agradecemos antecipadamente pela atenção e aguardamos retorno.

---

## Onde Enviar

- **Email:** suporte@montink.com.br
- **Ou:** Através do painel administrativo da Montink (se disponível)

---

## Notas para Desenvolvimento

Após receber a documentação oficial:
1. Implementar `createMontinkOrder()` em `server/integrations/montink/orders.ts`
2. Atualizar tipos `MontinkCreateOrderRequest` e `MontinkCreateOrderResponse` em `server/integrations/montink/types.ts`
3. Testar com pedidos de teste
4. Ativar feature flag `MONTINK_CREATE_ORDER_ENABLED=true`

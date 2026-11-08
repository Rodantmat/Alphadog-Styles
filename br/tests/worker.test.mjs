import assert from "node:assert/strict";
import crypto from "node:crypto";
import * as BR from "./worker/br/br.js";

// ---------- pure functions
assert.ok(BR.cpfOk("529.982.247-25")); assert.ok(!BR.cpfOk("111.111.111-11")); assert.ok(!BR.cpfOk("529.982.247-24"));
assert.ok(BR.cnpjOk("11.222.333/0001-81")); assert.ok(!BR.cnpjOk("11.222.333/0001-80"));
assert.equal(BR.brMailbox("Suporte@alphadogstyles.com"), "br_suporte"); assert.equal(BR.brMailbox("customiza@x.com"), "br_custom"); assert.equal(BR.brMailbox("pedidos@x.com"), "br_pedidos"); assert.equal(BR.brMailbox("support@x.com"), null);
const D = BR.decideRegion;
assert.equal(D({ country: "BR", path: "/" }).serve, "br");
assert.equal(D({ country: "US", path: "/" }).serve, "us");
assert.equal(D({ country: "BR", bot: true, path: "/" }).serve, "us");               // crawlers never get a different page for the same URL
assert.equal(D({ country: "BR", cookie: "us", path: "/" }).serve, "us");            // manual override beats geo
assert.equal(D({ country: "US", cookie: "br", path: "/" }).serve, "br");
assert.deepEqual(D({ country: "BR", qs: "us", path: "/" }), { redirect: "/", setCookie: "us" });
assert.equal(D({ country: "US", path: "/br/" }).serve, "br");
assert.equal(BR.priceCentavos("M"), 10990);
const ok = BR.resolveSku("CAV-LINE-CLASSIC-F-DK-PRET-M"); assert.ok(ok && ok.price === 10990 && /Cavalier/.test(ok.nome));
assert.equal(BR.resolveSku("CAV-LINE-CLASSIC-F-DK-BRAN-M"), null);                  // colour not released on a dark product
assert.equal(BR.resolveSku("CAV-LINE-CLASSIC-F-DK-PRET-XX"), null);
assert.equal(BR.priceItems([]), null);

// ---------- fake DB (only the statements br.js issues)
const tables = { orders: new Map(), kv: new Map(), custom: new Map() };
const DB = { prepare(sql) { let b = []; const o = { bind(...a) { b = a; return o; },
  async first() { if (/FROM orders WHERE id=\?/.test(sql)) return tables.orders.get(b[0]) || null; if (/FROM custom_requests/.test(sql)) return tables.custom.get(b[0]) || null; return null; },
  async all() { if (/FROM orders WHERE status=\?/.test(sql)) return { results: [...tables.orders.values()].filter(x => x.status === b[0]) }; return { results: [] }; },
  async run() {
    if (/^INSERT INTO orders/.test(sql)) { tables.orders.set(b[0], { id: b[0], email: b[1], data: b[2], total: b[3], status: b[4], printify_id: null, tracking: null }); return { meta: { changes: 1 } }; }
    if (/^UPDATE orders SET status='br_paid'/.test(sql)) { const x = tables.orders.get(b[1]); if (x && ["reserved", "awaiting_payment"].includes(x.status)) { x.status = "br_paid"; return { meta: { changes: 1 } }; } return { meta: { changes: 0 } }; }
    if (/^UPDATE orders SET status=\?,printify_id/.test(sql)) { const x = tables.orders.get(b[5]); Object.assign(x, { status: b[0], printify_id: b[1], tracking: b[2], data: b[3] }); return { meta: { changes: 1 } }; }
    if (/^UPDATE orders SET status='cancelled'/.test(sql)) { tables.orders.get(b[1]).status = "cancelled"; return { meta: { changes: 1 } }; }
    throw new Error("unhandled SQL " + sql); } }; return o; } };
const mails = [];
const H = { mail: async (env, to, subject, html, rt, from) => { mails.push({ to, subject, from }); return true; },
  kvGet: async (_, k) => tables.kv.get(k) ?? null, kvSet: async (_, k, v) => { tables.kv.set(k, v); }, rnd: n => crypto.randomBytes(n).toString("hex"), };

// ---------- mocked network (Gubo + Mercado Pago)
const calls = [];
globalThis.fetch = async (url, init = {}) => {
  const u = String(url), body = init.body ? JSON.parse(init.body) : null; calls.push({ u, m: init.method, body, h: init.headers });
  const R = (o, s = 200) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json" } });
  if (u.endsWith("/fretes/cotacoes")) return R({ id: "cot_1", situacao: "pronta", valida_ate: "x", opcoes: [{ servico: "pax", nome: "Olist Pax", transportadora: "Pax", preco_centavos: 1282, prazo_total_dias_uteis: 8, previsao_entrega: "2026-11-25" }, { servico: "jadlog", nome: "Jadlog", transportadora: "Jadlog", preco_centavos: 1776, prazo_total_dias_uteis: 12, previsao_entrega: "2026-12-01" }], escolha: { servico: "pax" } }, 201);
  if (u.endsWith("/pedidos/por-variante")) return R({ id: "ped_1", situacao: "aguardando_pagamento", versao: 2, valores: { itens_centavos: 5453, desconto_centavos: 0, frete_centavos: 1282, total_centavos: 6735 } }, 201);
  if (/\/pedidos\/ped_1\/pagar$/.test(u)) return R({ id: "ped_1", situacao: "confirmado", versao: 3, valores: { total_centavos: 6735 } }, 202);
  if (u.includes("/checkout/preferences")) return R({ init_point: "https://mp.example/pay/1", id: "pref1" }, 201);
  if (u.includes("/v1/payments/search")) return R({ results: [{ status: "approved", external_reference: lastId, transaction_amount: lastTotal / 100 }] });
  if (u.includes("/v1/payments/777")) return R({ status: "approved", external_reference: lastId, transaction_amount: lastTotal / 100 });
  throw new Error("unexpected fetch " + u);
};
let lastId = "", lastTotal = 0;
const env = { _db: DB, ADMIN_TOKEN: "adm", OWNER_EMAIL: "owner@x.com", GUBO_API_KEY: "gubo_test_x", GUBO_WEBHOOK_SECRET: "whsec_t", MP_ACCESS_TOKEN: "TEST-x", ASSETS: null };
const mk = (path, method = "GET", body = null, extra = {}) => { const raw = body ? JSON.stringify(body) : ""; const u = new URL("https://alphadogstyles.com" + path);
  return { req: new Request(u, { method, headers: extra.headers || {} }), env: extra.env || env, path: u.pathname, m: method, body: body || {}, raw, u, ctx: { waitUntil: p => p } }; };
const call = async (path, method, body, extra) => { const r = await BR.handleBR(H, mk(path, method, body, extra)); return { s: r.status, j: await r.json() }; };

const ship = { name: "Ana Souza", doc: "529.982.247-25", cep: "01310-100", logradouro: "Av. Paulista", numero: "1000", bairro: "Bela Vista", cidade: "São Paulo", uf: "SP", phone: "11999998888" };
const items = [{ sku: "CAV-LINE-CLASSIC-F-DK-PRET-M", qty: 1 }];

// quote
let r = await call("/api/br/quote", "POST", { cep: "01310-100", items }); assert.equal(r.s, 200); assert.equal(r.j.opcoes.length, 2); assert.equal(r.j.subtotal, 10990);
// bad CPF rejected before anything is created
r = await call("/api/br/orders", "POST", { email: "a@b.com", items, ship: { ...ship, doc: "111.111.111-11" } }); assert.equal(r.s, 400); assert.equal(tables.orders.size, 0);
// no payment provider and not dev mode -> refused (no dangling orders)
r = await call("/api/br/orders", "POST", { email: "a@b.com", items, ship }, { env: { ...env, MP_ACCESS_TOKEN: undefined } }); assert.equal(r.s, 503); assert.equal(r.j.code, "payments_not_configured");
// real flow
r = await call("/api/br/orders", "POST", { email: "a@b.com", items, ship, servico: "jadlog" }); assert.equal(r.s, 200, JSON.stringify(r.j)); assert.equal(r.j.url, "https://mp.example/pay/1");
lastId = r.j.id; lastTotal = r.j.total; assert.equal(lastTotal, 10990 + 1776); assert.equal(tables.orders.get(lastId).status, "awaiting_payment");
const mpBody = calls.find(c => c.u.includes("/checkout/preferences")).body; assert.equal(mpBody.external_reference, lastId); assert.equal(mpBody.items.at(-1).unit_price, 17.76); assert.equal(mpBody.items[0].unit_price, 109.9);
// payment webhook -> paid -> Gubo order created and paid from wallet
r = await call("/api/br/pay/webhook/mercadopago?data.id=777&type=payment", "POST", { type: "payment", data: { id: "777" } }); assert.equal(r.s, 200);
await new Promise(r => setTimeout(r, 20));
let o = tables.orders.get(lastId); assert.equal(o.status, "br_gubo_confirmed"); assert.equal(o.printify_id, "gubo:ped_1");
const gc = calls.find(c => c.u.endsWith("/pedidos/por-variante")); assert.equal(gc.body.referencia, lastId); assert.equal(gc.body.destinatario.documento, "52998224725"); assert.equal(gc.body.entrega.servico, "jadlog"); assert.equal(gc.h["idempotency-key"], "br-create-" + lastId);
assert.equal(calls.find(c => /pagar$/.test(c.u)).body.valor_esperado_centavos, 6735);
assert.ok(mails.some(m => /Pagamento confirmado/.test(m.subject) && m.from.includes("pedidos@")), "customer paid email from pedidos@");
// duplicate webhook is harmless
const n = calls.length; await call("/api/br/pay/webhook/mercadopago?data.id=777&type=payment", "POST", { type: "payment", data: { id: "777" } }); assert.equal(calls.filter(c => c.u.endsWith("/pedidos/por-variante")).length, 1);
// Gubo webhook: signature, dedupe, version
const evt = (tipo, situacao, versao, extra = {}) => JSON.stringify({ id: "evt_" + tipo + versao, tipo, dados: { pedido: { id: "ped_1", referencia: lastId, situacao, versao, ...extra } } });
const sign = (raw, secret = "whsec_t") => { const t = Math.floor(Date.now() / 1000); return `t=${t},v1=${crypto.createHmac("sha256", secret).update(t + "." + raw).digest("hex")}`; };
let raw = evt("pedido.enviado", "enviado", 5, { envio: { rastreio: "AB123456789BR", transportadora: "Jadlog" } });
let bad = await BR.handleBR(H, { ...mk("/api/br/gubo/webhook", "POST", null, { headers: { "gubo-assinatura": sign(raw, "wrong") } }), raw }); assert.equal(bad.status, 400);
let good = await BR.handleBR(H, { ...mk("/api/br/gubo/webhook", "POST", null, { headers: { "gubo-assinatura": sign(raw) } }), raw }); assert.equal(good.status, 200);
o = tables.orders.get(lastId); assert.equal(o.status, "br_shipped"); assert.equal(o.tracking, "AB123456789BR"); assert.ok(mails.some(m => /foi enviado/.test(m.subject)));
raw = evt("pedido.em_producao", "em_producao", 4);  // older version arriving late must not move the order backwards
await BR.handleBR(H, { ...mk("/api/br/gubo/webhook", "POST", null, { headers: { "gubo-assinatura": sign(raw) } }), raw }); assert.equal(tables.orders.get(lastId).status, "br_shipped");
// guest tracking requires matching e-mail
r = await call(`/api/br/orders/${lastId}?email=other@x.com`, "GET"); assert.equal(r.s, 404); r = await call(`/api/br/orders/${lastId}?email=A@B.com`, "GET"); assert.equal(r.s, 200); assert.equal(r.j.status, "br_shipped");
// internal endpoints need the admin token
r = await call("/api/internal/br/sweep", "POST", {}, { headers: {} }); assert.equal(r.s, 403);

// ---------- geoGate with a stub ASSETS binding
const seen = []; const assets = { fetch: async rq => { seen.push(new URL(rq.url).pathname); return new Response("<html>" + new URL(rq.url).pathname + "</html>", { headers: { "content-type": "text/html", etag: "W/x" } }); } };
const g = async (path, { cc = "US", cookie, ua = "Mozilla/5.0 iPhone" } = {}) => { const rq = new Request("https://alphadogstyles.com" + path, { headers: { "user-agent": ua, ...(cookie ? { cookie } : {}) } }); Object.defineProperty(rq, "cf", { value: { country: cc } }); return BR.geoGate(rq, { ASSETS: assets }, new URL(rq.url).pathname); };
let x = await g("/", { cc: "BR" }); assert.equal(await x.text(), "<html>/br/</html>"); assert.equal(x.headers.get("content-language"), "pt-BR"); assert.match(x.headers.get("vary"), /Cookie/); assert.match(x.headers.get("link"), /hreflang="pt-BR"/);
x = await g("/", { cc: "US" }); assert.equal(await x.text(), "<html>/</html>");
x = await g("/", { cc: "BR", ua: "Googlebot/2.1" }); assert.equal(await x.text(), "<html>/</html>");
x = await g("/?region=us", { cc: "BR" }); assert.equal(x.status, 302); assert.match(x.headers.get("set-cookie"), /ad_region=us/);
x = await g("/", { cc: "BR", cookie: "ad_region=us" }); assert.equal(await x.text(), "<html>/</html>");
assert.equal(await g("/api/br/config"), null); assert.equal(await g("/css/style.css"), null);   // only the entry pages are gated

// ---------- wallet without balance: order is held and retried, never lost
globalThis.fetch = async (url, init = {}) => { const u = String(url), R = (o, s = 200) => new Response(JSON.stringify(o), { status: s });
  if (u.endsWith("/pedidos/por-variante")) return R({ id: "ped_2", situacao: "aguardando_pagamento", versao: 1, valores: { itens_centavos: 5453, desconto_centavos: 0, frete_centavos: 1776, total_centavos: 7229 } }, 201);
  if (/pagar$/.test(u)) return R({ erro: { codigo: "saldo_insuficiente", mensagem: "x" } }, 402); throw new Error(u); };
tables.orders.set("BR-W", { id: "BR-W", email: "w@x.com", total: 12766, status: "br_paid", printify_id: null, tracking: null, data: JSON.stringify({ lines: [{ sku: "CAV-LINE-CLASSIC-F-DK-PRET-M", qty: 1 }], subtotal: 10990, shipping: 1776, frete: { servico: "jadlog" }, ship }) });
await BR.fulfilBR(H, env, "BR-W"); assert.equal(tables.orders.get("BR-W").status, "br_wallet_low"); assert.ok(mails.some(m => /Carteira Gubo/.test(m.subject)));
console.log("worker tests OK (" + calls.length + " mocked network calls)");

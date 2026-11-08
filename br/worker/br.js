// AlphaDog Styles - Brazilian (pt-BR) arm. One self-contained module plugged into store/worker/index.js (see br/patches).
// Nothing here runs until the patch is applied and the secrets exist. No payment keys, no Gubo key, no fake values are embedded.
//   geoGate()    : same-URL region routing (country BR -> pt-BR storefront, cookie override, bots never vary)
//   handleBR()   : /api/br/*  (quote, orders, confirm, custom, Mercado Pago webhook, Gubo webhook) + /api/internal/br/*
//   brMailbox()  : maps inbound suporte@ / customiza@ / pedidos@ to support_inbox mailboxes
// Env (all optional until the owner provides them): GUBO_API_KEY, GUBO_API_BASE, GUBO_WEBHOOK_SECRET,
//   MP_ACCESS_TOKEN, MP_WEBHOOK_SECRET, BR_DEV_MODE ("1" = staging: orders are created without a payment provider), BR_MAILBOX_DOMAIN.
import CAT from "../../br/data/catalog_br.json";
import CFG from "../../br/config/br_config.json";

const hex = b => [...new Uint8Array(b)].map(x => x.toString(16).padStart(2, "0")).join("");
const J = (o, s = 200, h = {}) => new Response(JSON.stringify(o), { status: s, headers: { "content-type": "application/json", "cache-control": "no-store", ...h } });
const err = (m, s = 400, extra = {}) => J({ error: m, ...extra }, s);
const esc = x => String(x).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
const now = () => Date.now();
const brl = c => "R$ " + (c / 100).toFixed(2).replace(".", ",").replace(/\B(?=(\d{3})+(?!\d))/g, ".");
const DOM = env => env.BR_MAILBOX_DOMAIN || CFG.domain;
const FROM = env => ({ suporte: `AlphaDog Suporte <suporte@${DOM(env)}>`, customiza: `AlphaDog Personalizados <customiza@${DOM(env)}>`, pedidos: `AlphaDog Pedidos <pedidos@${DOM(env)}>` });
export const BR_STATUS = ["reserved", "awaiting_payment", "br_paid", "br_wallet_low", "br_gubo_confirmed", "br_in_production", "br_shipped", "br_delivered", "needs_attention", "cancelled"];

/* ------------------------------------------------------------------ region routing */
export function decideRegion({ country, cookie, qs, bot, path }) {
  if (path === "/br" || path === "/br/") return { serve: "br", setCookie: null };
  if (qs === "us" || qs === "br") return { redirect: path, setCookie: qs };       // manual override always wins
  if (bot) return { serve: "us" };                                                 // crawlers always get the same page for the same URL
  if (cookie === "us" || cookie === "br") return { serve: cookie };
  return { serve: String(country || "").toUpperCase() === "BR" ? "br" : "us" };
}
const BOT_RE = /bot|crawl|spider|slurp|facebookexternalhit|preview|lighthouse|pingdom|headless/i;
export async function geoGate(req, env, path) {
  if (!(path === "/" || path === "/index.html" || path === "/br" || path === "/br/")) return null;
  const u = new URL(req.url), ck = Object.fromEntries((req.headers.get("cookie") || "").split(/;\s*/).map(x => x.split("=")));
  const d = decideRegion({ country: req.cf && req.cf.country || req.headers.get("cf-ipcountry"), cookie: ck[CFG.regions.cookie], qs: u.searchParams.get("region"),
    bot: !!(req.cf && req.cf.botManagement && req.cf.botManagement.verifiedBot) || BOT_RE.test(req.headers.get("user-agent") || ""), path });
  const cookie = v => `${CFG.regions.cookie}=${v}; Path=/; Max-Age=31536000; SameSite=Lax; Secure`;
  if (d.redirect) return new Response(null, { status: 302, headers: { location: d.redirect, "set-cookie": cookie(d.setCookie), "cache-control": "no-store", vary: "Cookie" } });
  const target = d.serve === "br" ? "/br/" : "/";
  const r = await env.ASSETS.fetch(new Request(new URL(target, u.origin), { method: "GET", redirect: "follow" }));   // fresh request: never forward the visitor's conditional headers (a 304 for the other region would be wrong)
  const h = new Headers(r.headers); h.set("vary", "Cookie, CF-IPCountry"); h.set("cache-control", "private, no-cache"); h.set("content-language", d.serve === "br" ? "pt-BR" : "en-US");
  h.append("link", '<https://' + DOM(env) + '/br/>; rel="alternate"; hreflang="pt-BR"'); h.append("link", '<https://' + DOM(env) + '/>; rel="alternate"; hreflang="en-US"'); h.append("link", '<https://' + DOM(env) + '/>; rel="alternate"; hreflang="x-default"');
  return new Response(r.body, { status: r.status, headers: h });
}

/* ------------------------------------------------------------------ validation helpers */
export function cpfOk(v) {
  const s = String(v || "").replace(/\D/g, ""); if (s.length !== 11 || /^(\d)\1+$/.test(s)) return false;
  for (const n of [9, 10]) { let sum = 0; for (let i = 0; i < n; i++) sum += +s[i] * (n + 1 - i); const d = (sum * 10) % 11 % 10; if (d !== +s[n]) return false; }
  return true;
}
export function cnpjOk(v) {
  const s = String(v || "").replace(/\D/g, ""); if (s.length !== 14 || /^(\d)\1+$/.test(s)) return false;
  for (const n of [12, 13]) { let sum = 0, w = n - 7; for (let i = 0; i < n; i++) { sum += +s[i] * w--; if (w < 2) w = 9; } const d = sum % 11 < 2 ? 0 : 11 - sum % 11; if (d !== +s[n]) return false; }
  return true;
}
const UFS = "AC AL AP AM BA CE DF ES GO MA MT MS MG PA PB PR PE PI RJ RN RS RO RR SC SP SE TO".split(" ");
const okEmail = e => typeof e === "string" && e.length < 255 && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(e);
const digits = v => String(v || "").replace(/\D/g, "");

/* ------------------------------------------------------------------ catalog / pricing */
export function priceCentavos(size) { return CFG.pricing.retail_centavos + (CFG.pricing.size_surcharge_centavos[size] || 0); }
// sku = <product>-<colour>-<size>   (Gubo sku_padrao). Returns the validated line or null.
export function resolveSku(sku, cat = CAT) {
  const s = String(sku || "").trim().toUpperCase();
  const p = cat.products.find(x => x.visible && s.startsWith(x.code + "-")); if (!p) return null;
  const [color, size] = s.slice(p.code.length + 1).split("-");
  if (!color || !size || !p.colors[color] || !p.colors[color].includes(size)) return null;
  const br = cat.breeds.find(b => b.code === p.breed);
  return { sku: s, product: p.code, color, size, nome: `${br ? br.name : p.breed} - ${cat.labels.theme[p.theme]} ${cat.labels.style[p.style]} (${cat.labels.side[p.side]}) - ${cat.colors[color].name} / ${size}`, price: priceCentavos(size) };
}
export function priceItems(items, cat = CAT) {
  const out = [];
  for (const it of Array.isArray(items) ? items : []) {
    const r = resolveSku(it.sku, cat); const q = Math.max(1, Math.min(20, parseInt(it.qty) || 1)); if (!r) return null;
    out.push({ ...r, qty: q });
  }
  return out.length && out.length <= 30 ? out : null;
}
const subtotalOf = lines => lines.reduce((a, l) => a + l.price * l.qty, 0);

/* ------------------------------------------------------------------ custom dog design purchase (product created by hand in Gubo Studio) */
async function customLines(env, DB, body) {
  const c = await DB.prepare("SELECT id,data,status,quote FROM custom_requests WHERE id=? AND token=?").bind(String(body.custom.id || ""), String(body.custom.k || "")).first(); const cd = c && JSON.parse(c.data);
  if (!c || c.status !== "ready" || !cd.gubo_product || !cd.price_centavos) return { error: "Este design personalizado ainda não está pronto para compra" };
  const sku = String(cd.gubo_product).toUpperCase() + "-" + String(body.color || "").toUpperCase() + "-" + String(body.size || "").toUpperCase();
  try { const v = await gubo(env, "GET", "/catalogo/variantes?sku=" + encodeURIComponent(sku)); const ok = (v.body.dados || [])[0]; if (!ok || !ok.disponivel) return { error: "Cor ou tamanho indisponível" }; } catch (e) { return { error: "Não foi possível validar o produto agora", status: 503 }; }
  return { custom: c.id, lines: [{ sku, product: cd.gubo_product, color: body.color, size: body.size, nome: "Design personalizado " + c.id, price: cd.price_centavos, qty: Math.max(1, Math.min(5, parseInt(body.qty) || 1)) }] };
}

/* ------------------------------------------------------------------ Gubo client */
export async function gubo(env, method, path, body, headers = {}) {
  if (!env.GUBO_API_KEY) { const e = new Error("Gubo API key not configured"); e.code = "gubo_not_configured"; throw e; }
  const r = await fetch((env.GUBO_API_BASE || CFG.gubo.base_url) + path, { method, headers: { authorization: "Bearer " + env.GUBO_API_KEY, "content-type": "application/json", ...headers }, body: body ? JSON.stringify(body) : undefined });
  let j = null; try { j = await r.json(); } catch { }
  if (!r.ok && ![409].includes(r.status)) { const e = new Error((j && j.erro && j.erro.mensagem) || "Gubo error " + r.status); e.status = r.status; e.gubo = j && j.erro; throw e; }
  return { status: r.status, body: j };
}
const guboItems = lines => lines.map(l => ({ sku: l.sku, quantidade: l.qty }));
async function quote(env, kvGet, kvSet, cep, lines) {
  const key = "brq:" + digits(cep) + ":" + lines.map(l => l.sku + "x" + l.qty).sort().join(",");
  const hit = await kvGet(key); if (hit && hit.exp > now()) return hit.v;
  let r = await gubo(env, "POST", "/fretes/cotacoes", { cep: digits(cep), itens: guboItems(lines), entrega: { preferencia: CFG.shipping.preference } });
  if (r.status === 202 && r.body && r.body.id) r = await gubo(env, "GET", "/fretes/cotacoes/" + r.body.id, null, { prefer: "wait=10" });
  const b = r.body; if (!b || b.situacao !== "pronta" || !(b.opcoes || []).length) { const e = new Error("Não foi possível calcular o frete para este CEP."); e.status = 422; throw e; }
  const v = { id: b.id, valida_ate: b.valida_ate, opcoes: b.opcoes.map(o => ({ servico: o.servico, nome: o.nome, transportadora: o.transportadora, preco_centavos: o.preco_centavos, prazo_dias_uteis: o.prazo_total_dias_uteis, previsao: o.previsao_entrega })), escolha: b.escolha && b.escolha.servico };
  await kvSet(key, { v, exp: now() + 10 * 60000 }); return v;
}

/* ------------------------------------------------------------------ payments (adapter; Mercado Pago placeholder) */
export const payReady = env => !!env.MP_ACCESS_TOKEN;
async function mp(env, method, path, body) {
  const r = await fetch("https://api.mercadopago.com" + path, { method, headers: { authorization: "Bearer " + env.MP_ACCESS_TOKEN, "content-type": "application/json" }, body: body ? JSON.stringify(body) : undefined });
  const j = await r.json().catch(() => ({})); if (!r.ok) throw new Error(j.message || "Mercado Pago " + r.status); return j;
}
// TODO-verify against the live Mercado Pago docs before go-live (field names are from memory of Checkout Pro; no network test was possible).
async function mpCreate(env, o, origin) {
  const items = o.lines.map(l => ({ id: l.sku, title: "AlphaDog " + l.nome, quantity: l.qty, unit_price: l.price / 100, currency_id: "BRL" }));
  if (o.shipping) items.push({ id: "FRETE", title: "Frete", quantity: 1, unit_price: o.shipping / 100, currency_id: "BRL" });
  const pref = await mp(env, "POST", "/checkout/preferences", { items, payer: { email: o.email, name: o.name }, external_reference: o.id, statement_descriptor: "ALPHADOG STYLES",
    notification_url: origin + "/api/br/pay/webhook/mercadopago", back_urls: { success: origin + "/#/pedido/" + o.id + "?pago=1", pending: origin + "/#/pedido/" + o.id, failure: origin + "/#/carrinho" }, auto_return: "approved", metadata: { order_id: o.id } });
  return { provider: "mercadopago", url: pref.init_point, ref: pref.id };
}
async function mpApproved(env, orderId, total) {
  const s = await mp(env, "GET", "/v1/payments/search?external_reference=" + encodeURIComponent(orderId) + "&sort=date_created&criteria=desc");
  const p = (s.results || []).find(x => x.status === "approved" && x.external_reference === orderId);
  return !!p && Math.round(p.transaction_amount * 100) === total;
}
async function mpSigOk(req, env, dataId) {
  if (!env.MP_WEBHOOK_SECRET) return true;   // authoritative check is the API lookup; signature is an extra layer (TODO-verify manifest format in MP sandbox)
  const sig = req.headers.get("x-signature") || "", p = Object.fromEntries(sig.split(",").map(x => x.trim().split("=")));
  if (!p.ts || !p.v1) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(env.MP_WEBHOOK_SECRET), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = hex(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(`id:${dataId};request-id:${req.headers.get("x-request-id") || ""};ts:${p.ts};`)));
  return mac === p.v1;
}

/* ------------------------------------------------------------------ emails (pt-BR) */
const T = {
  reserved: (id, tot) => [`Pedido ${id} recebido`, `<p>Obrigado pelo seu pedido <b>${id}</b> (${brl(tot)}). Assim que o pagamento for confirmado, enviamos para produção.</p>`],
  paid: (id, tot) => [`Pagamento confirmado - pedido ${id}`, `<p>Obrigado! Recebemos o pagamento do pedido <b>${id}</b> (${brl(tot)}). Sua peça é feita sob encomenda: a produção leva cerca de ${CFG.gubo.production_days} dias úteis, mais o prazo de entrega. Avisamos por e-mail quando for enviada.</p>`],
  shipped: (id, trk, carrier) => [`Seu pedido ${id} foi enviado`, `<p>Seu pedido da AlphaDog Styles está a caminho${carrier ? " pela " + esc(carrier) : ""}.</p>${trk ? `<p>Código de rastreio: <b>${esc(trk)}</b></p>` : ""}`],
  delivered: id => [`Pedido ${id} entregue`, `<p>Seu pedido foi entregue. Se algo não estiver certo, responda este e-mail ou escreva para suporte@${CFG.domain}.</p>`],
  custom: id => [`Recebemos seu pedido de design personalizado (${id})`, `<p>Obrigado! Recebemos as fotos do seu cachorro. Nosso artista vai analisar e enviar uma prévia e um orçamento por e-mail, normalmente em 2 a 4 dias úteis.</p>`],
  customQuote: (id, q) => [`Seu design personalizado ${id} está pronto para análise`, `<p>Temos novidades sobre o seu pedido ${id}${q ? ` - valor do design: <b>${brl(q)}</b>` : ""}. Abra o link do seu pedido para ver a prévia.</p>`],
};
const sendTo = async (h, env, to, [subj, html], box = "suporte") => h.mail(env, to, subj, html, `${box}@${DOM(env)}`, FROM(env)[box]);
const ownerMail = (h, env, subject, html) => env.OWNER_EMAIL ? h.mail(env, env.OWNER_EMAIL, subject, html, undefined, FROM(env).pedidos) : false;

/* ------------------------------------------------------------------ order state */
async function getOrder(DB, id) { const o = await DB.prepare("SELECT id,email,data,total,status,printify_id,tracking FROM orders WHERE id=?").bind(id).first(); return o ? { ...o, d: JSON.parse(o.data || "{}") } : null; }
async function setOrder(DB, o, patch) {
  const d = { ...o.d, ...(patch.d || {}) }, st = patch.status || o.status;
  await DB.prepare("UPDATE orders SET status=?,printify_id=?,tracking=?,data=?,updated=? WHERE id=?").bind(st, patch.gubo ? "gubo:" + patch.gubo : o.printify_id, patch.tracking || o.tracking, JSON.stringify(d), now(), o.id).run();
  Object.assign(o, { status: st, d, printify_id: patch.gubo ? "gubo:" + patch.gubo : o.printify_id, tracking: patch.tracking || o.tracking });
}
async function markPaidBR(h, env, ctx, id) {
  const DB = env._db, r = await DB.prepare("UPDATE orders SET status='br_paid',updated=? WHERE id=? AND status IN ('reserved','awaiting_payment')").bind(now(), id).run();
  if (r.meta && r.meta.changes === 0) return false;
  const o = await getOrder(DB, id); if (!o) return false;
  await sendTo(h, env, o.email, T.paid(id, o.total), "pedidos");
  await ownerMail(h, env, `Novo pedido BR ${id} (${brl(o.total)})`, `<p>Pedido pago <b>${id}</b> de ${esc(o.email)}. Enviando para a Gubo automaticamente.</p>`);
  if (env.GUBO_API_KEY) { const p = fulfilBR(h, env, id).catch(() => { }); ctx && ctx.waitUntil ? ctx.waitUntil(p) : await p; }
  return true;
}

/* ------------------------------------------------------------------ Gubo fulfilment (idempotent; also called by the retry sweep) */
export async function fulfilBR(h, env, id) {
  const DB = env._db, o = await getOrder(DB, id); if (!o || !["br_paid", "br_wallet_low"].includes(o.status)) return { skipped: o && o.status };
  const d = o.d, s = d.ship;
  let r = await gubo(env, "POST", "/pedidos/por-variante", {
    referencia: id, itens: guboItems(d.lines),
    destinatario: { nome: s.name, documento: digits(s.doc), email: o.email, ...(s.phone ? { telefone: digits(s.phone) } : {}), endereco: { cep: digits(s.cep), logradouro: s.logradouro, numero: s.numero, ...(s.complemento ? { complemento: s.complemento } : {}), bairro: s.bairro, cidade: s.cidade, uf: s.uf } },
    entrega: { servico: d.frete.servico, se_indisponivel: "mais_barata" }, observacao: "AlphaDog Styles " + id, metadados: { id_loja: id } },
    { "idempotency-key": "br-create-" + id, prefer: "wait=10" });
  let g = r.body;
  if (r.status === 409 && g && g.erro && g.erro.codigo === "referencia_duplicada") g = (await gubo(env, "GET", "/pedidos/" + g.erro.detalhes.pedido_id)).body;
  if (!g || !g.id) throw new Error("Gubo did not return an order id");
  if (["pendente", "recusado", "cancelado"].includes(g.situacao)) {
    await setOrder(DB, o, { status: "needs_attention", gubo: g.id, d: { gubo_note: g.pendencias || g.motivo_recusa || g.situacao } });
    await ownerMail(h, env, `[Atenção] Pedido BR ${id} parado na Gubo (${g.situacao})`, `<p>${esc(JSON.stringify(g.pendencias || g.motivo_recusa || ""))}</p>`); return { gubo: g.id, situacao: g.situacao };
  }
  if (g.situacao === "recebido") g = (await gubo(env, "GET", "/pedidos/" + g.id, null, { prefer: "wait=10" })).body;
  if (g.situacao === "aguardando_pagamento") {
    const v = g.valores || {}, overF = (v.frete_centavos || 0) - (d.shipping || 0), maxCost = Math.round(d.subtotal * 0.7);
    if (overF > (CFG.gubo.max_freight_overrun_centavos ?? 500) || (v.itens_centavos || 0) - (v.desconto_centavos || 0) > maxCost) {
      await setOrder(DB, o, { status: "needs_attention", gubo: g.id, d: { gubo_note: "cost guard", gubo_valores: v } });
      await ownerMail(h, env, `[Atenção] Pedido BR ${id}: custo Gubo acima do esperado`, `<p>Gubo ${brl(v.total_centavos)} vs cobrado ${brl(o.total)}. Pedido NÃO pago na Gubo.</p>`); return { guard: true };
    }
    try {
      const p = await gubo(env, "POST", `/pedidos/${g.id}/pagar`, { valor_esperado_centavos: v.total_centavos }, { "idempotency-key": "br-pay-" + id, prefer: "wait=10" }); g = (p.body && p.body.pedido) || g;
    } catch (e) {
      if (e.status === 402) { await setOrder(DB, o, { status: "br_wallet_low", gubo: g.id }); await ownerMail(h, env, "[Ação] Carteira Gubo sem saldo", `<p>O pedido ${id} aguarda saldo. Recarregue a carteira no Studio (Pix/cartão); o sistema tenta de novo sozinho.</p>`); return { wallet: "low" }; }
      throw e;
    }
  }
  await setOrder(DB, o, { status: "br_gubo_confirmed", gubo: g.id, d: { gubo_total_centavos: (g.valores || {}).total_centavos, gubo_versao: g.versao || 0 } });
  return { gubo: g.id, situacao: g.situacao };
}
const GUBO_MAP = { confirmado: "br_gubo_confirmed", em_producao: "br_in_production", enviado: "br_shipped", entregue: "br_delivered", cancelado: "needs_attention", recusado: "needs_attention", pendente: "needs_attention" };
async function applyGuboOrder(h, env, p) {
  const DB = env._db, o = await getOrder(DB, p.referencia); if (!o) return false;
  if ((o.d.gubo_versao || 0) >= (p.versao || 0)) return true;
  const st = GUBO_MAP[p.situacao]; if (!st) return true;                     // unknown/early states = "em andamento"
  const trk = p.envio && (p.envio.url_rastreio || p.envio.rastreio);
  const was = o.status; await setOrder(DB, o, { status: st, gubo: p.id, tracking: trk || null, d: { gubo_versao: p.versao || 0, gubo_note: st === "needs_attention" ? (p.pendencias || p.motivo_recusa || p.situacao) : o.d.gubo_note } });
  if (st === "br_shipped" && was !== st) await sendTo(h, env, o.email, T.shipped(o.id, p.envio && p.envio.rastreio, p.envio && p.envio.transportadora), "pedidos");
  if (st === "br_delivered" && was !== st) await sendTo(h, env, o.email, T.delivered(o.id), "pedidos");
  if (st === "needs_attention" && was !== st) await ownerMail(h, env, `[Atenção] Pedido BR ${o.id}: Gubo ${p.situacao}`, `<pre>${esc(JSON.stringify(p.pendencias || p.motivo_recusa || "", null, 1))}</pre>`);
  return true;
}
async function guboSigOk(raw, header, secret) {
  const parts = (header || "").split(",").map(x => x.trim().split("=")), t = (parts.find(x => x[0] === "t") || [])[1], v1 = parts.filter(x => x[0] === "v1").map(x => x[1]);
  if (!t || !v1.length || !secret || Math.abs(Date.now() / 1000 - Number(t)) > 300) return false;
  const key = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  const mac = hex(await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(t + "." + raw)));
  return v1.some(x => x.length === mac.length && [...x].reduce((a, c, i) => a | (c.charCodeAt(0) ^ mac.charCodeAt(i)), 0) === 0);
}

/* ------------------------------------------------------------------ inbound mail mapping */
export function brMailbox(to) {
  const a = String(to || "").toLowerCase();
  if (a.startsWith("suporte@")) return "br_suporte";
  if (a.startsWith("customiza@")) return "br_custom";
  if (a.startsWith("pedidos@")) return "br_pedidos";
  return null;
}

/* ------------------------------------------------------------------ routes */
// h = helpers from index.js: { mail, kvGet, kvSet, rnd, auth, okEmail }
export async function handleBR(h, ctx) {
  const { req, env, path, m, body, raw, u } = ctx; const DB = env._db;
  if (!path.startsWith("/api/br/") && !path.startsWith("/api/internal/br/")) return null;

  if (path === "/api/br/config" && m === "GET")
    return J({ currency: "BRL", payments: payReady(env) || env.BR_DEV_MODE === "1", dev: env.BR_DEV_MODE === "1", shipping: CFG.shipping.mode, free_over_centavos: CFG.shipping.free_over_centavos, retail_centavos: CFG.pricing.retail_centavos, mailboxes: CFG.mailboxes, seller: CFG.seller });

  if (path === "/api/br/quote" && m === "POST") {
    let lines = priceItems(body.items);
    if (!lines && body.custom) { const cl = await customLines(env, DB, body); if (cl.error) return err(cl.error, cl.status || 400); lines = cl.lines; }
    if (!lines) return err("Carrinho inválido");
    if (digits(body.cep).length !== 8) return err("Informe um CEP válido");
    try {
      const q = await quote(env, h.kvGet.bind(null, DB), h.kvSet.bind(null, DB), body.cep, lines), sub = subtotalOf(lines);
      const free = CFG.shipping.free_over_centavos != null && sub >= CFG.shipping.free_over_centavos;
      return J({ ...q, subtotal: sub, free_shipping: free });
    } catch (e) { return err(e.code === "gubo_not_configured" ? "Cálculo de frete indisponível no momento" : e.message, e.status === 422 ? 422 : 503); }
  }

  if (path === "/api/br/orders" && m === "POST") {
    if ((await h.kvGet(DB, "checkout_paused")) === "1") return err("O checkout está pausado por alguns instantes. Tente novamente em breve.", 503);
    if (!payReady(env) && env.BR_DEV_MODE !== "1") return err("O pagamento ainda não está disponível. Volte em breve!", 503, { code: "payments_not_configured" });
    let lines = priceItems(body.items), custom = null;
    if (!lines && body.custom) { const cl = await customLines(env, DB, body); if (cl.error) return err(cl.error, cl.status || 400); lines = cl.lines; custom = cl.custom; }
    if (!lines) return err("Carrinho inválido");
    const e = String(body.email || "").trim().toLowerCase(); if (!okEmail(e)) return err("Informe um e-mail válido");
    const s = body.ship || {}, doc = digits(s.doc), cep = digits(s.cep);
    if (!(cpfOk(doc) || cnpjOk(doc))) return err("CPF inválido");
    if (cep.length !== 8) return err("CEP inválido");
    if (!UFS.includes(String(s.uf || "").toUpperCase())) return err("Estado (UF) inválido");
    for (const k of ["name", "logradouro", "numero", "bairro", "cidade"]) if (!s[k] || String(s[k]).length > 120) return err("Complete o endereço de entrega");
    if (String(s.name).trim().length < 3) return err("Informe o nome completo do destinatário");
    if (s.phone && !/^\d{10,13}$/.test(digits(s.phone))) return err("Telefone inválido (use DDD)");
    let q; try { q = await quote(env, h.kvGet.bind(null, DB), h.kvSet.bind(null, DB), cep, lines); } catch (x) { return err(x.code === "gubo_not_configured" && env.BR_DEV_MODE === "1" ? "DEV: frete sem Gubo" : (x.message || "Frete indisponível"), 503); }
    const opt = q.opcoes.find(o => o.servico === body.servico) || q.opcoes.find(o => o.servico === q.escolha) || q.opcoes[0];
    const sub = subtotalOf(lines), free = CFG.shipping.free_over_centavos != null && sub >= CFG.shipping.free_over_centavos, ship = free ? 0 : opt.preco_centavos, total = sub + ship;
    const id = "BR-" + h.rnd(4).toUpperCase();
    const data = { region: "BR", lang: "pt", currency: "BRL", lines, subtotal: sub, shipping: ship, frete: { servico: opt.servico, nome: opt.nome, prazo_dias_uteis: opt.prazo_dias_uteis, previsao: opt.previsao, cotacao: q.id }, custom,
      ship: { name: String(s.name).trim(), doc, phone: digits(s.phone), cep, logradouro: s.logradouro, numero: s.numero, complemento: s.complemento || "", bairro: s.bairro, cidade: s.cidade, uf: String(s.uf).toUpperCase() } };
    await DB.prepare("INSERT INTO orders(id,email,data,total,status,created,updated) VALUES(?,?,?,?,?,?,?)").bind(id, e, JSON.stringify(data), total, "reserved", now(), now()).run();
    if (payReady(env)) {
      try {
        const pay = await mpCreate(env, { id, email: e, name: data.ship.name, lines, shipping: ship }, u.origin);
        await setOrder(DB, await getOrder(DB, id), { status: "awaiting_payment", d: { pay: { provider: pay.provider, ref: pay.ref } } });
        return J({ id, total, url: pay.url });
      } catch (x) { await DB.prepare("UPDATE orders SET status='cancelled',updated=? WHERE id=?").bind(now(), id).run(); return err("Não foi possível iniciar o pagamento: " + x.message, 502); }
    }
    await sendTo(h, env, e, T.reserved(id, total), "pedidos");     // BR_DEV_MODE staging: no provider, order stays 'reserved'
    return J({ id, total, dev: true });
  }

  if (path === "/api/br/orders/confirm" && m === "POST" && payReady(env)) {
    const o = await getOrder(DB, String(body.id || "")); if (!o) return err("Pedido não encontrado", 404);
    if (o.status === "awaiting_payment" && await mpApproved(env, o.id, o.total)) await markPaidBR(h, env, ctx.ctx, o.id);
    return J({ status: (await getOrder(DB, o.id)).status });
  }

  let mm;
  if ((mm = path.match(/^\/api\/br\/orders\/(BR-[\w]+)$/)) && m === "GET") {         // guest tracking: order id + e-mail
    const o = await getOrder(DB, mm[1]); const e = String(u.searchParams.get("email") || "").toLowerCase();
    if (!o || o.email !== e) return err("Pedido não encontrado", 404);
    return J({ id: o.id, status: o.status, total: o.total, itens: o.d.lines.map(l => ({ nome: l.nome, qty: l.qty })), frete: o.d.frete, rastreio: o.tracking });
  }

  if (path === "/api/br/pay/webhook/mercadopago" && m === "POST") {
    if (!payReady(env)) return J({ ok: true });
    let ev = {}; try { ev = JSON.parse(raw || "{}"); } catch { }
    const dataId = u.searchParams.get("data.id") || (ev.data && ev.data.id) || "";
    if (!(await mpSigOk(req, env, dataId))) return err("bad signature", 400);
    if ((ev.type || u.searchParams.get("type")) === "payment" && dataId) {
      try { const p = await mp(env, "GET", "/v1/payments/" + dataId), o = p.external_reference && await getOrder(DB, p.external_reference);
        if (o && p.status === "approved" && Math.round(p.transaction_amount * 100) === o.total) await markPaidBR(h, env, ctx.ctx, o.id); } catch (e) { return err("retry", 500); }
    }
    return J({ ok: true });
  }

  if (path === "/api/br/gubo/webhook" && m === "POST") {
    if (!(await guboSigOk(raw, req.headers.get("gubo-assinatura"), env.GUBO_WEBHOOK_SECRET))) return err("assinatura inválida", 400);
    let ev; try { ev = JSON.parse(raw); } catch { return err("bad json", 400); }
    if (await h.kvGet(DB, "gevt:" + ev.id)) return J({ ok: true });
    const p = ev.dados && ev.dados.pedido; if (p && p.referencia) await applyGuboOrder(h, env, p);
    await h.kvSet(DB, "gevt:" + ev.id, 1); return J({ ok: true });
  }

  if (path === "/api/br/custom" && m === "POST") {
    const e = String(body.email || "").trim().toLowerCase(); if (!okEmail(e)) return err("Informe um e-mail válido");
    const ph = Array.isArray(body.photos) ? body.photos : []; if (ph.length < 5) return err("Envie pelo menos 5 fotos do seu cachorro"); if (ph.length > 12) return err("Envie no máximo 12 fotos");
    for (const x of ph) if (!/^image\/(jpeg|png|webp)$/.test(x.mime || "") || typeof x.b64 !== "string" || x.b64.length > 2800000) return err("Uma das fotos não pôde ser usada. Use fotos JPG ou PNG.");
    const cl = v => String(v || "").slice(0, 1500), dog = body.dog || {};
    const data = { region: "BR", dog: { name: cl(dog.name), breed: cl(dog.breed), colors: cl(dog.colors), markings: cl(dog.markings), ears: cl(dog.ears), tail: cl(dog.tail), details: cl(dog.details) }, style: { theme: cl(body.style && body.style.theme), style: cl(body.style && body.style.style) }, products: ["camiseta"], qty: cl(body.qty), notes: cl(body.notes) };
    const id = "CU-" + h.rnd(3).toUpperCase(), tok = h.rnd(12);
    await DB.prepare("INSERT INTO custom_requests(id,token,email,name,lang,data,status,created,updated) VALUES(?,?,?,?,?,?,?,?,?)").bind(id, tok, e, cl(body.name), "pt", JSON.stringify(data), "new", now(), now()).run();
    let i = 0; for (const x of ph) await DB.prepare("INSERT INTO custom_photos(req_id,idx,mime,b64,created) VALUES(?,?,?,?,?)").bind(id, i++, x.mime, x.b64, now()).run();
    await sendTo(h, env, e, [T.custom(id)[0], T.custom(id)[1] + `<p><a href="${(env.SITE_URL || u.origin)}/#/personalizado/${id}?k=${tok}">Ver seu pedido</a></p>`], "customiza");
    const cto = env.FORWARD_BR_CUSTOM || env.OWNER_EMAIL; if (cto) await h.mail(env, cto, `Novo pedido de design personalizado BR ${id}`, `<p><b>${esc(e)}</b> (${ph.length} fotos)</p><pre style="white-space:pre-wrap">${esc(JSON.stringify(data, null, 1))}</pre>`, e, FROM(env).customiza);
    return J({ id, k: tok });
  }
  if ((mm = path.match(/^\/api\/br\/custom\/(CU-[\w]+)$/)) && m === "GET") {
    const r = await DB.prepare("SELECT id,status,quote,note,data FROM custom_requests WHERE id=? AND token=?").bind(mm[1], u.searchParams.get("k") || "").first(); if (!r) return err("Não encontrado", 404);
    const d = JSON.parse(r.data); return J({ id: r.id, status: r.status, quote: r.quote, note: r.note, ready: r.status === "ready" ? { price_centavos: d.price_centavos, product: d.gubo_product } : null, dog: { name: d.dog.name } });
  }

  /* ---- internal (admin token already checked by index.js before this point is reached for /api/internal/*) ---- */
  if (path.startsWith("/api/internal/br/")) {
    if (!env.ADMIN_TOKEN || req.headers.get("x-admin-token") !== env.ADMIN_TOKEN) return err("Forbidden", 403);
    if (path === "/api/internal/br/sweep" && m === "POST") {                     // retry br_paid / br_wallet_low, reconcile awaiting_payment
      const out = { fulfilled: [], reconciled: [], errors: [] };
      for (const st of ["br_paid", "br_wallet_low"]) for (const r of (await DB.prepare("SELECT id FROM orders WHERE status=? ORDER BY created LIMIT 20").bind(st).all()).results) {
        try { out.fulfilled.push({ id: r.id, ...(await fulfilBR(h, env, r.id)) }); } catch (e) { out.errors.push({ id: r.id, error: String(e.message).slice(0, 200) }); }
      }
      if (payReady(env)) for (const r of (await DB.prepare("SELECT id,total FROM orders WHERE status=? ORDER BY created LIMIT 30").bind("awaiting_payment").all()).results) {
        try { if (await mpApproved(env, r.id, r.total)) { await markPaidBR(h, env, ctx.ctx, r.id); out.reconciled.push(r.id); } } catch (e) { out.errors.push({ id: r.id, error: String(e.message).slice(0, 200) }); }
      }
      if (env.GUBO_API_KEY) {                                                        // polling fallback for lost webhooks (docs: ?atualizado_desde=)
        const since = (await h.kvGet(DB, "br_gubo_since")) || new Date(now() - 3 * 864e5).toISOString();
        try { const g = await gubo(env, "GET", "/pedidos?limite=100&atualizado_desde=" + encodeURIComponent(since)); let max = since;
          for (const p of (g.body.dados || [])) { if (p.referencia && /^BR-/.test(p.referencia)) await applyGuboOrder(h, env, p); if (p.atualizado_em > max) max = p.atualizado_em; }
          await h.kvSet(DB, "br_gubo_since", max); } catch (e) { out.errors.push({ gubo_poll: String(e.message).slice(0, 200) }); }
      }
      return J(out);
    }
    if ((mm = path.match(/^\/api\/internal\/br\/fulfil\/(BR-[\w]+)$/)) && m === "POST") { try { return J(await fulfilBR(h, env, mm[1])); } catch (e) { return err(String(e.message), 502); } }
    if ((mm = path.match(/^\/api\/internal\/br\/custom\/(CU-[\w]+)$/)) && m === "POST") {   // owner/assistant: quote, mark ready with the Gubo product created in Studio
      const r = await DB.prepare("SELECT email,data,quote,status FROM custom_requests WHERE id=?").bind(mm[1]).first(); if (!r) return err("No such request", 404);
      const d = JSON.parse(r.data); if (body.gubo_product) d.gubo_product = String(body.gubo_product).toUpperCase(); if (body.price_centavos) d.price_centavos = parseInt(body.price_centavos);
      const q = body.quote_centavos != null ? parseInt(body.quote_centavos) : r.quote, st = body.status || r.status;
      await DB.prepare("UPDATE custom_requests SET status=?,quote=?,note=COALESCE(?::text,note),data=?,updated=? WHERE id=?").bind(st, q, body.note || null, JSON.stringify(d), now(), mm[1]).run();
      if (body.notify) await sendTo(h, env, r.email, T.customQuote(mm[1], q), "customiza");
      return J({ ok: true });
    }
    return err("Not found", 404);
  }
  return err("Not found", 404);
}

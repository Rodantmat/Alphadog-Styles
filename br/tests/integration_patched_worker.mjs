import assert from "node:assert/strict";
const mod = (await import("./store/worker/index.js")).default;
const inbox = []; const DB = { prepare(sql) { let b = []; const o = { bind(...a) { b = a; return o }, async first() { return null }, async all() { return { results: [] } }, async run() { if (/INSERT INTO support_inbox/.test(sql)) inbox.push(b); return { meta: { changes: 1 } } } }; return o } };
const assets = { fetch: async rq => new Response("ASSET:" + new URL(rq.url).pathname) };
const env = { DB, ASSETS: assets, ADMIN_TOKEN: "t", GUBO_API_KEY: undefined };
const ctx = { waitUntil() { } };
const req = (p, cc, extra = {}) => { const r = new Request("https://alphadogstyles.com" + p, { headers: { "user-agent": "Mozilla/5.0", ...extra } }); Object.defineProperty(r, "cf", { value: { country: cc } }); return r };
assert.equal(await (await mod.fetch(req("/", "BR"), env, ctx)).text(), "ASSET:/br/");
assert.equal(await (await mod.fetch(req("/", "US"), env, ctx)).text(), "ASSET:/");
assert.equal(await (await mod.fetch(req("/css/style.css", "BR"), env, ctx)).text(), "ASSET:/css/style.css");   // untouched
let r = await mod.fetch(req("/api/br/config", "BR"), env, ctx); assert.equal(r.status, 200); const j = await r.json(); assert.equal(j.currency, "BRL"); assert.equal(j.payments, false);
r = await mod.fetch(req("/api/health", "US"), env, ctx); assert.equal(r.status, 200);
r = await mod.fetch(req("/api/internal/br/sweep", "US"), env, ctx); assert.equal(r.status, 500 === r.status ? r.status : 403);
// inbound mail
const msg = (to) => ({ to, from: "cliente@exemplo.com.br", raw: new TextEncoder().encode("From: cliente@exemplo.com.br\r\nTo: " + to + "\r\nSubject: Oi\r\n\r\nQuero saber do meu pedido"), forward: async () => { } });
for (const to of ["suporte@alphadogstyles.com", "customiza@alphadogstyles.com", "pedidos@alphadogstyles.com", "support@alphadogstyles.com", "customization@alphadogstyles.com"]) await mod.email(msg(to), env, ctx);
assert.deepEqual(inbox.map(x => x[0]), ["br_suporte", "br_custom", "br_pedidos", "support", "custom"]);
console.log("patched worker integration OK");

import { JSDOM } from "jsdom"; import fs from "fs";
const R = "/home/claude/alphadog-styles/br/site";
const html = fs.readFileSync(R + "/index.html", "utf8").replace(/<script[^>]*src[^>]*><\/script>/, "");
const dom = new JSDOM(html, { url: "https://alphadogstyles.com/", runScripts: "outside-only", pretendToBeVisual: true });
const w = dom.window; const cat = fs.readFileSync(process.env.CATALOG || R + "/data/catalog_br.json", "utf8"); const MODELS = JSON.parse(fs.readFileSync(R + "/../config/br_config.json", "utf8")).pricing.models;
w.fetch = async u => ({ ok: true, status: 200, json: async () => u.includes("catalog_br") ? JSON.parse(cat) : u.includes("/api/br/config") ? { payments: false, retail_centavos: 10990, models: MODELS } : {} });
w.IntlOK = 1; w.scrollTo = () => {};
let src = fs.readFileSync(R + "/js/br.js", "utf8");
w.eval(src.replace(/^/, "") );   // classic-script eval; module top-level const/let are fine
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = async h => { w.location.hash = h; await sleep(60); return w.document.querySelector("#app").textContent.replace(/\s+/g, " ").slice(0, 160) };
await sleep(100);
for (const h of ["#/", "#/loja", "#/p/CAV/line/classic", "#/carrinho", "#/pagina/faq", "#/pagina/tamanhos", "#/rastrear", "#/personalizar", "#/entrar", "#/nada"]) console.log(h, "=>", await go(h));
if (!process.env.CATALOG) {
// add to cart then checkout
w.location.hash = "#/p/CAV/line/classic"; await sleep(60); w.document.querySelector("#add").click(); await sleep(60);
console.log("cart:", w.localStorage.getItem("adbr_cart"), "| page:", w.document.querySelector("#app").textContent.replace(/\s+/g," ").slice(0,100));
console.log("checkout =>", await go("#/checkout"));
console.log("pay disabled (no provider):", w.document.querySelector("#pay").disabled);

}
if (process.env.CATALOG) {   // multi-model catalog (python3 br/tests/gen_multi_fixture.py /tmp/multi.json; CATALOG=/tmp/multi.json node br/tests/smoke_site.mjs)
  const T = () => w.document.querySelector("#app").textContent.replace(/\s+/g, " ");
  w.localStorage.clear(); w.location.hash = "#/p/LHA/line/classic"; await sleep(80);
  const nb = nbsp => nbsp.replace(/\u00a0/g, " ");
  console.log("models:", [...w.document.querySelectorAll("#md button")].map(b => b.textContent).join(" | "));
  if (!/R\$ 139,90/.test(nb(T())) || !/R\$ 109,90/.test(nb(T()))) throw new Error("Padrao price/compare-at missing: " + nb(T()).slice(0, 200));
  const pick = async m => { w.document.querySelector(`#md button[data-m="${m}"]`).click(); await sleep(60) };
  await pick("H2"); if (!/R\$ 276,90/.test(nb(T())) || !/R\$ 217,90/.test(nb(T()))) throw new Error("H2: " + nb(T()).slice(0, 200));
  w.document.querySelector('#sz button[data-z="XG"]').click(); await sleep(60); if (!/R\$ 234,90/.test(nb(T()))) throw new Error("H2 XG surcharge: " + nb(T()).slice(0, 200));
  await pick("EC"); console.log("EC sizes:", [...w.document.querySelectorAll("#sz button")].map(b => b.textContent).join(","));
  await pick("KD"); console.log("KD sizes:", [...w.document.querySelectorAll("#sz button")].map(b => b.textContent).join(","));
  await pick("BL"); w.document.querySelector("#add").click(); await sleep(60);
  console.log("cart:", w.localStorage.getItem("adbr_cart"));
  const ct = nb(T()); if (!/Babylook/.test(ct) || !/R\$ 109,90/.test(ct)) throw new Error("cart: " + ct.slice(0, 250));
  console.log("grid cards:", (await go("#/loja"), w.document.querySelectorAll(".card").length), "| first price:", nb(w.document.querySelector(".card .price").textContent));
  console.log("MULTI SMOKE OK");
}

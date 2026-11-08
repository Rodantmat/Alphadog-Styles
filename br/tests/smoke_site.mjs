import { JSDOM } from "jsdom"; import fs from "fs";
const R = "/home/claude/alphadog-styles/br/site";
const html = fs.readFileSync(R + "/index.html", "utf8").replace(/<script[^>]*src[^>]*><\/script>/, "");
const dom = new JSDOM(html, { url: "https://alphadogstyles.com/", runScripts: "outside-only", pretendToBeVisual: true });
const w = dom.window; const cat = fs.readFileSync(R + "/data/catalog_br.json", "utf8");
w.fetch = async u => ({ ok: true, status: 200, json: async () => u.includes("catalog_br") ? JSON.parse(cat) : u.includes("/api/br/config") ? { payments: false, retail_centavos: 10990 } : {} });
w.IntlOK = 1; w.scrollTo = () => {};
let src = fs.readFileSync(R + "/js/br.js", "utf8");
w.eval(src.replace(/^/, "") );   // classic-script eval; module top-level const/let are fine
const sleep = ms => new Promise(r => setTimeout(r, ms));
const go = async h => { w.location.hash = h; await sleep(60); return w.document.querySelector("#app").textContent.replace(/\s+/g, " ").slice(0, 160) };
await sleep(100);
for (const h of ["#/", "#/loja", "#/p/CAV/line/classic", "#/carrinho", "#/pagina/faq", "#/pagina/tamanhos", "#/rastrear", "#/personalizar", "#/entrar", "#/nada"]) console.log(h, "=>", await go(h));
// add to cart then checkout
w.location.hash = "#/p/CAV/line/classic"; await sleep(60); w.document.querySelector("#add").click(); await sleep(60);
console.log("cart:", w.localStorage.getItem("adbr_cart"), "| page:", w.document.querySelector("#app").textContent.replace(/\s+/g," ").slice(0,100));
console.log("checkout =>", await go("#/checkout"));
console.log("pay disabled (no provider):", w.document.querySelector("#pay").disabled);

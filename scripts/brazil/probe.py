import sys, json, statistics as st
sys.path.insert(0, "scripts/brazil")
from common import *
task = sys.argv[1]
QUERIES = ["camiseta shih tzu","camiseta vira-lata caramelo","camiseta mae de pet","camiseta golden retriever","camiseta personalizada cachorro","moletom cachorro","camiseta pug","camiseta yorkshire","camiseta labrador","bone cachorro"]

if task == "ml_api":
    log = []
    for url in ["https://api.mercadolibre.com/sites/MLB/search?q=camiseta%20shih%20tzu&limit=50",
                "https://api.mercadolibre.com/sites/MLB/categories",
                "https://api.mercadolibre.com/categories/MLB1430",
                "https://api.mercadolibre.com/sites/MLB/listing_prices?price=60&category_id=MLB31447",
                "https://api.mercadolibre.com/sites/MLB/domain_discovery/search?q=camiseta%20shih%20tzu"]:
        r = get(url)
        log.append({"url": url, "status": r.status_code if r is not None else None, "body": (r.text[:3000] if r is not None else "")})
        print(url, r.status_code if r is not None else None, (r.text[:200] if r is not None else ""))
    save("ml/api_probe.json", log)
    # try full search on all queries if works
    if True:
        for q in QUERIES:
            r = get("https://api.mercadolibre.com/sites/MLB/search", params={"q": q, "limit": 50})
            if r is not None and r.status_code == 200:
                save(f"ml/search_{q.replace(' ','_')}.json", r.text)

PW_HELPER = None
def pw_run(fn):
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(user_agent=UA, locale="pt-BR", viewport={"width":1366,"height":900})
        page = ctx.new_page()
        try:
            fn(page)
        finally:
            b.close()

def grab(page, url, name, wait=2500, links=False):
    try:
        resp = page.goto(url, wait_until="domcontentloaded", timeout=40000)
        page.wait_for_timeout(wait)
        txt = page.inner_text("body")
        save(name, f"URL: {url}\nSTATUS: {resp.status if resp else None}\nTITLE: {page.title()}\n\n{txt}")
        if links:
            hrefs = page.eval_on_selector_all("a[href]", "els=>els.map(e=>[e.innerText.trim().slice(0,100),e.href])")
            save(name + ".links.json", hrefs)
        return txt
    except Exception as e:
        print("PWERR", url, e)
        save(name, f"URL: {url}\nERROR: {e}")
        return ""

if task == "ml_pw":
    def run(page):
        import urllib.parse
        for q in QUERIES:
            slug = q.replace(" ", "-")
            url = f"https://lista.mercadolivre.com.br/{slug}"
            try:
                resp = page.goto(url, wait_until="domcontentloaded", timeout=40000)
                page.wait_for_timeout(2500)
                for _ in range(4):
                    page.mouse.wheel(0, 2500); page.wait_for_timeout(500)
                cards = page.eval_on_selector_all("li.ui-search-layout__item, div.ui-search-result, div.poly-card", """els=>els.map(e=>({text:e.innerText, href:(e.querySelector('a')||{}).href}))""")
                save(f"ml/list_{slug}.json", {"url": url, "status": resp.status if resp else None, "title": page.title(), "n": len(cards), "cards": cards})
                if not cards:
                    save(f"ml/list_{slug}.body.txt", page.inner_text("body")[:5000])
            except Exception as e:
                print("PWERR", q, e)
    pw_run(run)

if task == "ml_items":
    # a few item pages: take first N links from each saved listing
    import glob
    def run(page):
        for f in glob.glob("docs/brazil_data/ml/list_*.json"):
            d = json.load(open(f))
            if not isinstance(d, dict): continue
            for c in d.get("cards", [])[:3]:
                if c.get("href"):
                    slug = f.split("list_")[1][:-5]
                    n = re.sub(r"\W+", "_", c["href"])[-40:]
                    txt = grab(page, c["href"], f"ml/item_{slug}_{n}.txt", wait=1500)
    pw_run(run)

if task == "ml_help":
    URLS = {
     "custos": "https://www.mercadolivre.com.br/ajuda/Custos-para-vender_1044",
     "tarifas": "https://vendedores.mercadolivre.com.br/custos/",
     "tarifas2": "https://www.mercadolivre.com.br/ajuda/Tarifas-e-custos_1044",
     "envio": "https://www.mercadolivre.com.br/ajuda/Como-funciona-o-envio_3375",
     "nota_fiscal": "https://www.mercadolivre.com.br/ajuda/nota-fiscal_1187",
     "pf": "https://www.mercadolivre.com.br/ajuda/Posso-vender-sem-CNPJ_1038",
     "devolucoes": "https://www.mercadolivre.com.br/ajuda/devolucoes_1201",
     "dev_shipments": "https://developers.mercadolivre.com.br/pt_br/envios",
     "dev_invoices": "https://developers.mercadolivre.com.br/pt_br/notas-fiscais",
     "dev_limits": "https://developers.mercadolivre.com.br/pt_br/limites-de-chamadas",
     "dev_saleterms": "https://developers.mercadolivre.com.br/pt_br/condicoes-de-venda",
     "dev_start": "https://developers.mercadolivre.com.br/pt_br/api-docs-pt-br",
     "seller_home": "https://vendedores.mercadolivre.com.br/",
    }
    def run(page):
        for k, u in URLS.items():
            grab(page, u, f"ml_help/{k}.txt", wait=3000, links=True)
        # discover links to cost pages from seller home
        try:
            hrefs = json.load(open("docs/brazil_data/ml_help/seller_home.txt.links.json"))
            keep = [h for t, h in hrefs if re.search(r"custo|tarifa|envio|nota|cnpj|devol|reputa|ajuda", h + t, re.I)][:25]
            save("ml_help/discovered_links.json", keep)
            for i, h in enumerate(keep[:12]):
                grab(page, h, f"ml_help/disc_{i}.txt", wait=2500)
        except Exception as e:
            print("disc err", e)
    pw_run(run)
    # API fee data (public)
    out = {}
    for cat in ["MLB31447", "MLB1430", "MLB109027"]:
        for lt in ["gold_special", "gold_pro", "free"]:
            r = get(f"https://api.mercadolibre.com/sites/MLB/listing_prices?price=60&category_id={cat}&listing_type_id={lt}")
            out[f"{cat}_{lt}"] = {"status": r.status_code if r is not None else None, "body": r.text[:1500] if r is not None else ""}
    for u in ["https://api.mercadolibre.com/sites/MLB/listing_types", "https://api.mercadolibre.com/categories/MLB31447", "https://api.mercadolibre.com/sites/MLB"]:
        r = get(u); out[u] = {"status": r.status_code if r is not None else None, "body": r.text[:4000] if r is not None else ""}
    save("ml_help/api_fees.json", out)

if task == "dimona":
    URLS = {
     "api_docs": "https://api.camisadimona.com.br/",
     "api_docs2": "https://api.camisadimona.com.br/docs",
     "api_swagger": "https://api.camisadimona.com.br/swagger",
     "home": "https://www.camisadimona.com.br/",
     "dropshipping": "https://www.camisadimona.com.br/dropshipping",
     "dropshipping2": "https://www.camisadimona.com.br/dropshipping/",
     "suporte": "https://suporte.camisadimona.com.br/",
     "suporte_pt": "https://suporte.camisadimona.com.br/pt-BR",
     "precos": "https://www.camisadimona.com.br/precos",
     "frete": "https://www.camisadimona.com.br/frete",
     "integracoes": "https://www.camisadimona.com.br/integracoes",
    }
    def run(page):
        for k, u in URLS.items():
            grab(page, u, f"dimona/{k}.txt", wait=4000, links=True)
        found = set()
        for k in URLS:
            try:
                for t, h in json.load(open(f"docs/brazil_data/dimona/{k}.txt.links.json")):
                    if "dimona" in h and re.search(r"artigo|article|docs|api|frete|prazo|devol|troca|nota|pagament|integra|dropship|preco|tabela|arte|arquivo|marketplace|mercado|cancel", h + t, re.I):
                        found.add(h)
            except Exception: pass
        found = sorted(found)[:40]
        save("dimona/discovered_links.json", found)
        for i, h in enumerate(found):
            grab(page, h, f"dimona/disc_{i:02d}.txt", wait=2500)
    pw_run(run)
    for u in ["https://api.camisadimona.com.br/", "https://api.camisadimona.com.br/openapi.json", "https://api.camisadimona.com.br/swagger.json", "https://api.camisadimona.com.br/v1/docs"]:
        r = get(u)
        save("dimona/curl_" + re.sub(r"\W+", "_", u)[-40:] + ".txt", f"{u}\n{r.status_code if r is not None else None}\n{r.text[:6000] if r is not None else ''}")

if task == "shipping":
    URLS = {
     "melhorenvio_home": "https://melhorenvio.com.br/",
     "melhorenvio_docs": "https://docs.menv.io/",
     "melhorenvio_api": "https://docs.melhorenvio.com.br/",
     "melhorenvio_calc": "https://melhorenvio.com.br/calculadora-de-frete",
     "melhorenvio_prices": "https://melhorenvio.com.br/planos",
     "correios_tabela": "https://www.correios.com.br/enviar/precisa-de-ajuda/tabelas-de-precos-e-prazos",
     "montink_home": "https://montink.com.br/",
     "montink_precos": "https://montink.com.br/precos",
     "montink_dropshipping": "https://montink.com.br/dropshipping",
     "dropsimples": "https://www.dropsimples.com.br/",
     "ra_dimona": "https://www.reclameaqui.com.br/empresa/camisa-dimona/",
     "ra_montink": "https://www.reclameaqui.com.br/empresa/montink/",
     "ra_dropsimples": "https://www.reclameaqui.com.br/empresa/dropsimples/",
    }
    def run(page):
        for k, u in URLS.items():
            grab(page, u, f"shipping/{k}.txt", wait=4000, links=True)
        # Melhor Envio public calculator POST attempt via requests
    pw_run(run)
    for body in [{"from":{"postal_code":"01310100"},"to":{"postal_code":"20040020"},"products":[{"id":"1","width":20,"height":3,"length":25,"weight":0.3,"insurance_value":60,"quantity":1}]},
                 {"from":{"postal_code":"01310100"},"to":{"postal_code":"69005040"},"products":[{"id":"1","width":20,"height":3,"length":25,"weight":0.3,"insurance_value":60,"quantity":1}]}]:
        try:
            r = requests.post("https://melhorenvio.com.br/api/v2/me/shipment/calculate", json=body, headers={"User-Agent": UA, "Accept":"application/json"}, timeout=25)
            save("shipping/me_calc_%s.json" % body["to"]["postal_code"], f"{r.status_code}\n{r.text[:3000]}")
        except Exception as e:
            print("ERR", e)

if task == "shopee":
    URLS = {
     "shopee_search": "https://shopee.com.br/search?keyword=camiseta%20shih%20tzu",
     "shopee_api": "https://shopee.com.br/api/v4/search/search_items?by=relevancy&keyword=camiseta%20shih%20tzu&limit=20&newest=0&order=desc&page_type=search&version=2",
     "amazon_search": "https://www.amazon.com.br/s?k=camiseta+shih+tzu",
     "amazon_search2": "https://www.amazon.com.br/s?k=camiseta+vira-lata+caramelo",
     "amazon_search3": "https://www.amazon.com.br/s?k=camiseta+mae+de+pet",
    }
    def run(page):
        for k, u in URLS.items():
            grab(page, u, f"shopee/{k}.txt", wait=5000)
    pw_run(run)

if task == "dimona2":
    # Zendesk Help Center public API (official) + Postman published docs JSON
    allart = []
    url = "https://suporte.camisadimona.com.br/api/v2/help_center/pt-br/articles.json?per_page=100"
    pages = 0
    while url and pages < 5:
        r = get(url)
        if r is None or r.status_code != 200:
            save("dimona/zd_error.txt", f"{url}\n{r.status_code if r is not None else None}\n{r.text[:500] if r is not None else ''}")
            break
        j = r.json(); allart += j.get("articles", []); url = j.get("next_page"); pages += 1
    print("articles", len(allart))
    out = []
    for a in allart:
        out.append(f"# [{a['id']}] {a['title']}\nURL: {a['html_url']}\nsection: {a.get('section_id')} updated: {a.get('updated_at')}\n\n{text_of_html(a.get('body') or '')}\n\n{'='*60}\n")
    save("dimona/zendesk_articles.txt", "\n".join(out))
    for ep in ["sections", "categories"]:
        r = get(f"https://suporte.camisadimona.com.br/api/v2/help_center/pt-br/{ep}.json?per_page=100")
        if r is not None and r.status_code == 200: save(f"dimona/zd_{ep}.json", r.text)
    for u in ["https://documenter.gw.postman.com/api/collections/111729/2sB2qdgLJQ?segregateAuth=true&versionTag=latest",
              "https://api.camisadimona.com.br/view/metadata/2sB2qdgLJQ",
              "https://documenter.gw.postman.com/view/metadata/2sB2qdgLJQ"]:
        r = get(u)
        save("dimona/postman_" + re.sub(r"\W+", "_", u)[-30:] + ".json", r.text if r is not None else "ERR")
        print(u, r.status_code if r is not None else None, len(r.text) if r is not None else 0)

if task == "amazon_parse":
    pass

if task == "dimona3":
    from bs4 import BeautifulSoup
    ids = [14214044760468, 14819247754004, 14214172355348, 14207402191124, 20278295040532, 14214507814164, 14823773115028]
    links = {}
    for i in ids:
        r = get(f"https://suporte.camisadimona.com.br/api/v2/help_center/pt-br/articles/{i}.json")
        if r is None or r.status_code != 200: continue
        a = r.json()["article"]
        s = BeautifulSoup(a["body"], "lxml")
        links[i] = [[x.get_text(strip=True), x["href"]] for x in s.find_all("a", href=True)]
    save("dimona/article_links.json", links)
    seen = set()
    os.makedirs(OUT + "/dimona/catalog", exist_ok=True)
    for i, ls in links.items():
        for t, h in ls:
            if h in seen or not h.startswith("http"): continue
            if not re.search(r"drive\.google|docs\.google|\.xlsx|\.pdf|\.csv|dimona|zdassets|zendesk", h): continue
            seen.add(h)
            u = h
            m = re.search(r"drive\.google\.com/file/d/([^/]+)", h)
            if m: u = f"https://drive.google.com/uc?export=download&id={m.group(1)}"
            m = re.search(r"docs\.google\.com/spreadsheets/d/([^/]+)", h)
            if m: u = f"https://docs.google.com/spreadsheets/d/{m.group(1)}/export?format=csv"
            try:
                r = requests.get(u, headers={"User-Agent": UA}, timeout=30, allow_redirects=True)
                ct = r.headers.get("content-type", "")
                print(h, "->", r.status_code, ct, len(r.content))
                if r.status_code == 200 and len(r.content) < 6_000_000 and "html" not in ct:
                    fn = re.sub(r"\W+", "_", h)[-60:]
                    ext = ".csv" if "csv" in ct else (".pdf" if "pdf" in ct else (".xlsx" if "sheet" in ct or "excel" in ct else ".bin"))
                    open(f"{OUT}/dimona/catalog/{fn}{ext}", "wb").write(r.content)
                    if ext == ".pdf":
                        import subprocess
                        subprocess.run(["pdftotext", "-layout", f"{OUT}/dimona/catalog/{fn}{ext}", f"{OUT}/dimona/catalog/{fn}.txt"])
                elif r.status_code == 200 and "html" in ct:
                    save("dimona/catalog/" + re.sub(r"\W+", "_", h)[-60:] + ".html.txt", text_of_html(r.text)[:20000])
            except Exception as e:
                print("ERR", h, e)

if task == "alt":
    # Alternatives research: fetch public pages with plain requests first, playwright fallback. Only public pages, no login.
    URLS = {
     "montink_home": "https://montink.com.br/",
     "montink_drop": "https://montink.com.br/dropshipping",
     "montink_integ": "https://montink.com.br/integracoes",
     "montink_precos": "https://montink.com.br/precos",
     "montink_api": "https://montink.com.br/api",
     "montink_dev": "https://developers.montink.com.br/",
     "montink_ajuda": "https://ajuda.montink.com.br/",
     "montink_help": "https://suporte.montink.com.br/",
     "montink_faq": "https://montink.com.br/faq",
     "gelato_br": "https://www.gelato.com/print-on-demand/brazil",
     "gelato_hook": "https://developers.gelato.com/docs/webhooks",
     "gelato_orders": "https://developers.gelato.com/docs/orders/order_details/",
     "gelato_dev": "https://developers.gelato.com/",
     "gelato_pricing": "https://www.gelato.com/pricing",
     "gelato_shipping": "https://support.gelato.com/en/articles/8996576-how-do-i-configure-notifications-webhooks",
     "printful_v2": "https://developers.printful.com/docs/v2-beta/",
     "printful_br": "https://www.printful.com/br",
     "printify_br": "https://help.printify.com/hc/en-us/articles/4483619306513-Which-countries-does-Printify-ship-to",
     "umapenca": "https://www.umapenca.com.br/",
     "umapenca_api": "https://www.umapenca.com.br/api",
     "reservaink": "https://www.reservaink.com.br/",
     "hayamax": "https://www.hayamax.com.br/",
     "dslite": "https://www.dslite.com.br/",
     "printi": "https://www.printi.com.br/",
     "camiseteria": "https://www.camiseteria.com.br/",
     "estampaja": "https://www.estampaja.com.br/",
     "ml_mcp_docs": "https://developers.mercadolivre.com.br/pt_br/server-mcp",
     "ml_mcp_docs2": "https://developers.mercadolivre.com.br/server-mcp",
     "ml_mcp_repo_readme": "https://raw.githubusercontent.com/mercadolibre/mercadolibre-mcp-server/main/README.md",
     "newerton_readme": "https://raw.githubusercontent.com/newerton/mcp-mercado-livre/main/README.md",
     "docker_ml_mcp": "https://hub.docker.com/mcp/server/mercado-libre/overview",
     "smithery_ml": "https://smithery.ai/server/lumile/mercadolibre-mcp",
    }
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch()
        ctx = b.new_context(user_agent=UA, locale="pt-BR", viewport={"width":1366,"height":900})
        for k, u in URLS.items():
            try:
                r = get(u)
                if r is not None and r.status_code == 200 and "raw.githubusercontent" in u:
                    save(f"alt/{k}.txt", f"URL: {u}\nSTATUS: 200\n\n{r.text}"); continue
                page = ctx.new_page()
                resp = page.goto(u, wait_until="domcontentloaded", timeout=40000)
                page.wait_for_timeout(4000)
                txt = page.inner_text("body")
                hrefs = page.eval_on_selector_all("a[href]", "els=>els.map(e=>[e.innerText.trim().slice(0,80),e.href])")
                save(f"alt/{k}.txt", f"URL: {u}\nSTATUS: {resp.status if resp else None}\nREQ_STATUS: {r.status_code if r is not None else None}\nTITLE: {page.title()}\n\n{txt[:30000]}\n\nLINKS:\n" + "\n".join(f"{a} | {h}" for a, h in hrefs[:200]))
                page.close()
            except Exception as e:
                save(f"alt/{k}.txt", f"URL: {u}\nERROR: {e}")
        b.close()

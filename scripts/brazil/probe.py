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
        log.append({"url": url, "status": r.status_code if r else None, "body": (r.text[:3000] if r else "")})
        print(url, r.status_code if r else None, (r.text[:200] if r else ""))
    save("ml/api_probe.json", log)
    # try full search on all queries if works
    if log[0]["status"] == 200:
        for q in QUERIES:
            r = get("https://api.mercadolibre.com/sites/MLB/search", params={"q": q, "limit": 50})
            if r is not None and r.status_code == 200:
                save(f"ml/search_{q.replace(' ','_')}.json", r.text)

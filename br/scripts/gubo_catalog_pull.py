"""Read-only pull of the Gubo catalog (needs GUBO_API_KEY with catalogo:ler). Writes produtos.json, variantes.json, cores.json into the output dir.
Docs: GET /catalogo/produtos, /catalogo/variantes (limite, cursor), /dominios/cores. Sync once a day, never per order."""
import os, sys, json, time, requests
base = os.environ.get("GUBO_API_BASE", "https://api.gubo.com.br/v1"); key = os.environ["GUBO_API_KEY"]; out = sys.argv[1]; os.makedirs(out, exist_ok=True)
S = requests.Session(); S.headers["Authorization"] = "Bearer " + key
def pages(path, **params):
    cur = None
    while True:
        p = {"limite": 100, **params, **({"cursor": cur} if cur else {})}
        r = S.get(base + path, params=p, timeout=60)
        if r.status_code == 429: time.sleep(int(r.headers.get("Retry-After", "5"))); continue
        r.raise_for_status(); j = r.json(); yield from j.get("dados", [])
        if not j.get("tem_mais"): return
        cur = j.get("proximo_cursor")
for name, path, kw in (("produtos", "/catalogo/produtos", {"situacao": "todos"}), ("variantes", "/catalogo/variantes", {}), ("cores", "/dominios/cores", {})):
    rows = list(pages(path, **kw)); json.dump(rows, open(f"{out}/{name}.json", "w"), ensure_ascii=False); print(name, len(rows))

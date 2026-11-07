import os, json, requests
KEY = os.environ["GUBO_API_KEY"]
OUT = "docs/brazil_data/gubo"; os.makedirs(OUT, exist_ok=True)
BASES = ["https://api.gubo.com.br/v1",
         "https://kx75xapy8azwdvdnd4brts7y098e5qvg.buildprintusercontent.com/gubo-api/latest/live/v1"]
H = {"Authorization": "Bearer " + KEY}
def save(n, o):
    open(f"{OUT}/{n}.json", "w").write(json.dumps(o, ensure_ascii=False, indent=1)[:60000])
def call(base, m, p, **kw):
    try:
        r = requests.request(m, base + p, headers=H, timeout=60, **kw)
        try: b = r.json()
        except Exception: b = r.text[:800]
        return r.status_code, dict(r.headers), b
    except Exception as e:
        return 0, {}, str(e)[:300]
base = None
for b in BASES:
    s, h, body = call(b, "GET", "/conexao")
    print(b[:45], s, h.get("Gubo-Modo"))
    if s == 200: base = b; save("conexao", body); break
    save("conexao_err_" + str(BASES.index(b)), [s, body])
if not base: raise SystemExit("no base worked")
for n, p in [("servicos", "/fretes/servicos"), ("carteira", "/carteira"),
             ("produtos", "/catalogo/produtos?situacao=todos&limite=50"),
             ("variantes", "/catalogo/variantes?limite=100")]:
    s, h, body = call(base, "GET", p); print(n, s); save(n, [s, body])
s, h, v = call(base, "GET", "/catalogo/variantes?disponivel=true&limite=20")
items = []
try: items = [{"sku": v["dados"][0]["sku"], "quantidade": 1}]
except Exception: pass
print("items", items)
if items:
    for nome, cep in [("sp", "01310100"), ("rio", "20061001"), ("manaus", "69005010"), ("porto_alegre", "90010000")]:
        s, h, body = call(base, "POST", "/fretes/cotacoes", json={"cep": cep, "itens": items}); print(nome, s); save("cotacao_" + nome, [s, body])

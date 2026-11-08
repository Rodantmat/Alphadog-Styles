import os, json, time, uuid, requests
KEY = os.environ["GUBO_API_KEY"]; B = "https://api.gubo.com.br/v1"
OUT = "docs/brazil_data/gubo"; os.makedirs(OUT, exist_ok=True)
H = {"Authorization": "Bearer " + KEY}
def save(n, o): open(f"{OUT}/{n}.json", "w").write(json.dumps(o, ensure_ascii=False, indent=1)[:60000])
def call(m, p, idem=False, **kw):
    h = dict(H)
    if idem: h["Idempotency-Key"] = str(uuid.uuid4())
    r = requests.request(m, B + p, headers=h, timeout=90, **kw)
    try: b = r.json()
    except Exception: b = r.text[:800]
    return r.status_code, b
ref = "TESTE-" + str(int(time.time()))
dest = {"nome": "Cliente Teste", "documento": "12345678909", "email": "teste@example.com",
        "endereco": {"cep": "01310-100", "logradouro": "Av. Paulista", "numero": "1000", "complemento": "ap 12",
                     "bairro": "Bela Vista", "cidade": "São Paulo", "uf": "SP"}}
body = {"referencia": ref, "itens": [{"sku": "CAV01-PRET-M", "quantidade": 1}], "destinatario": dest,
        "entrega": {"preferencia": "mais_barata"}, "valor_venda_centavos": 8990,
        "metadados": {"canal": "teste"}}
s, o = call("POST", "/pedidos/por-variante", idem=True, json=body, headers={"Prefer": "wait=10"}); print("create", s); save("pedido_create", [s, o])
pid = o.get("id") if isinstance(o, dict) else None
if not pid: raise SystemExit("no order id")
time.sleep(3)
s, o = call("GET", f"/pedidos/{pid}"); print("get", s); save("pedido_get", [s, o])
s, o = call("POST", f"/pedidos/{pid}/pagar", idem=True, json={}); print("pagar", s); save("pedido_pagar", [s, o])
time.sleep(3)
for para in ["em_producao", "enviado", "entregue"]:
    s, o = call("POST", f"/teste/pedidos/{pid}/avancar", idem=True, json={"para": para}); print(para, s); save("pedido_avancar_" + para, [s, o]); time.sleep(2)
s, o = call("GET", f"/pedidos/{pid}"); print("final", s); save("pedido_final", [s, o])
s, o = call("GET", "/carteira"); save("carteira_apos", [s, o])

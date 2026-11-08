"""usage: gen_multi_fixture.py OUT.json   - builds a PUBLIC catalog for the 3 new breeds x 12 designs x 2 tones x all 11 models with every variant marked available
(synthetic Gubo dump, cost = the model's card cost). For tests only."""
import importlib.util, json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
def mod(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(here, "..", "scripts", n + ".py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
bb, bm, bp = mod("build_br_catalog"), mod("br_matrix"), mod("br_pricing")
CN = {"PRET": "Preto", "MAR": "Marrom", "VMG": "Verde Musgo", "AZM": "Azul Marinho", "BRAN": "Branco", "OFWH": "Offwhite"}
produtos, variantes = [], []
for r in bm.matrix(bm.breeds()):
    produtos.append({"codigo": r["code"], "nome": r["name"], "imagem_url": "https://example.invalid/" + r["code"] + ".png", "modelo": {"codigo": "X"}})
    for c in r["colors"]:
        for s in r["sizes"]:
            sku = f"{r['code']}-{c}-{s}"
            variantes.append({"produto": r["code"], "sku": sku, "sku_padrao": sku, "cor": {"codigo": c, "nome": CN[c]}, "tamanho": s, "disponivel": True,
                              "preco_unitario_centavos": bp.row(r["model"])["cost_card_centavos"] - 150})
cat = bb.build(produtos, variantes)
for p in cat["products"]:
    p.pop("cost_centavos", None)
json.dump(cat, open(sys.argv[1], "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print("products", len(cat["products"]), "warnings", len(cat["warnings"]), cat["warnings"][:3])

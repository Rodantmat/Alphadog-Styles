"""Run: python3 -I br/tests/test_catalog.py   (no network). Uses the REAL Gubo dump (1 product) plus a synthetic fixture in the owner's SKU pattern."""
import json, os, sys, importlib.util
here = os.path.dirname(__file__)
spec = importlib.util.spec_from_file_location("b", os.path.join(here, "..", "scripts", "build_br_catalog.py")); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)

# 1. real dump
cat = b.build(b.load(os.path.join(here, "fixtures/produtos_cav_real.json")), b.load(os.path.join(here, "fixtures/variantes_cav_real.json")))
p = cat["products"][0]
assert p["code"] == "CAV-LINE-CLASSIC-F-DK" and p["breed"] == "CAV" and p["theme"] == "line" and p["style"] == "classic" and p["side"] == "front" and p["tone"] == "dark"
assert cat["breeds"][0]["name"] == "Cavalier King Charles", cat["breeds"]
assert set(p["colors"]) == {"PRET", "MAR", "VMG", "AZM"}, p["colors"]          # BRAN/OFWH are cor_nao_liberada on a dark product
assert p["sizes"] == ["P", "M", "G", "GG", "XG", "XGG"] and p["visible"]
assert p["cost_centavos"]["M"] == 5453 and p["cost_centavos"]["XG"] == 6295

# 2. owner pattern (synthetic)
prods = [{"codigo": "SHI-LN-CL-F-LT", "nome": "Camiseta Shih Tzu Linha Classico Frente Clara", "modelo": {"codigo": "CAMP"}},
         {"codigo": "SHI-GE-OC-B-DK", "nome": "Camiseta Shih Tzu Geometrico Oculos Costas Escura", "modelo": {"codigo": "CAMP"}},
         {"codigo": "WEIRD", "nome": "x"}]
vars_ = [{"produto": "SHI-LN-CL-F-LT", "sku": "SHI-LN-CL-F-LT-BRAN-M", "sku_padrao": "SHI-LN-CL-F-LT-BRAN-M", "cor": {"codigo": "BRAN", "nome": "Branco"}, "tamanho": "M", "disponivel": True, "preco_unitario_centavos": 5453},
         {"produto": "SHI-GE-OC-B-DK", "sku": "SHI-GE-OC-B-DK-PRET-G", "sku_padrao": "SHI-GE-OC-B-DK-PRET-G", "cor": {"codigo": "PRET", "nome": "Preto"}, "tamanho": "G", "disponivel": False, "preco_unitario_centavos": 5453}]
c2 = b.build(prods, vars_)
assert len(c2["products"]) == 2 and any("WEIRD" in w for w in c2["warnings"])
s = {x["code"]: x for x in c2["products"]}
assert s["SHI-LN-CL-F-LT"]["style"] == "classic" and s["SHI-GE-OC-B-DK"]["style"] == "cool" and s["SHI-GE-OC-B-DK"]["theme"] == "geo" and not s["SHI-GE-OC-B-DK"]["visible"]
assert c2["breeds"][0]["name"] == "Shih Tzu", c2["breeds"]
print("catalog tests OK")

# 3. all models: 6th SKU segment (Padrao keeps the 5-segment code)
prods = [{"codigo": "LHA-LN-CL-F-LT", "nome": "Camiseta Lhasa Apso Linha Classico Frente Clara"},
         {"codigo": "LHA-LN-CL-F-LT-BL", "nome": "Babylook Lhasa Apso Linha Classico Frente Clara"},
         {"codigo": "VLT-GE-CO-B-DK-H2", "nome": "Moletom com capuz (2 cabos) Vira-lata (SRD) Geometrico Coracao Costas Escura"},
         {"codigo": "MPN-GE-OC-B-DK-ZZ", "nome": "x"}]
vars_ = [{"produto": c["codigo"], "sku": c["codigo"] + "-PRET-M", "sku_padrao": c["codigo"] + "-PRET-M", "cor": {"codigo": "PRET", "nome": "Preto"}, "tamanho": "M", "disponivel": True, "preco_unitario_centavos": 20000 if c["codigo"].endswith("H2") else 5453} for c in prods]
c3 = b.build(prods, vars_)
m = {x["code"]: x["model"] for x in c3["products"]}
assert m == {"LHA-LN-CL-F-LT": "PD", "LHA-LN-CL-F-LT-BL": "BL", "VLT-GE-CO-B-DK-H2": "H2"}, m
assert [x["name"] for x in c3["breeds"]] == ["Lhasa Apso", "Vira-lata (SRD)"], c3["breeds"]
assert any("PRICE BELOW FLOOR" in w for w in c3["warnings"]) and any("ZZ" in w for w in c3["warnings"])   # H2 given a Gubo cost of R$200 -> below the 15% floor; ZZ has no price
print("model catalog tests OK")

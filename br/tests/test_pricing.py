"""Run: python3 -I br/tests/test_pricing.py   (no network). Proves the BRL table follows the stated method and the owner's floors."""
import importlib.util, json, math, os
here = os.path.dirname(os.path.abspath(__file__))
def mod(n):
    sp = importlib.util.spec_from_file_location(n, os.path.join(here, "..", "scripts", n + ".py")); m = importlib.util.module_from_spec(sp); sp.loader.exec_module(m); return m
bp, bb, bm = mod("br_pricing"), mod("build_br_catalog"), mod("br_matrix")
cfg = json.load(open(os.path.join(here, "..", "config", "br_config.json"), encoding="utf-8"))
T = bp.table()

# 1. committed config == generated table (nobody hand-edited prices)
assert cfg["pricing"]["models"] == bp.models_config(), "run: python3 -I br/scripts/br_pricing.py --write"
# 2. the owner's anchor is reproduced by the method (US multiple + owner discount ratio), not typed in
assert T["PD"]["compare_at_centavos"] == 13990 and T["PD"]["price_centavos"] == 10990 == cfg["pricing"]["retail_centavos"]
# 3. every price ends in ,90; compare-at too; compare-at > price; discount ratio 15..25%
for c, r in T.items():
    assert r["price_centavos"] % 100 == 90 and r["compare_at_centavos"] % 100 == 90, c
    assert r["compare_at_centavos"] > r["price_centavos"] and 15 <= r["off_pct"] <= 25, (c, r["off_pct"])
    # 4. owner floor: price >= 1.15 x (cost + label) at the CARD price, and still after the card fee; also if Gubo bills the print as MEGA
    assert r["price_centavos"] >= math.ceil(1.15 * r["cost_card_centavos"] / (1 - bp.FEE_CARD)), c
    assert r["floor_ok_if_mega"], c
    # XG/XGG surcharge keeps the ,90 ending
    assert (r["price_centavos"] + r["size_surcharge_centavos"]) % 100 == 90, c
# 5. proportionality: uncapped models sit at the same multiple of cost as the US store (within rounding to ,90)
for c, r in T.items():
    if r["capped"]: continue
    k = bp.K_HOOD if r["class"] == "hood" else bp.K_TEE
    assert abs(r["compare_at_centavos"] / r["cost_card_centavos"] - k) < 0.05, (c, r["compare_at_centavos"] / r["cost_card_centavos"], k)
# 6. models ordered sanely: hoodies > oversized > tech > padrao = babylook > cropped > kids
p = {c: r["price_centavos"] for c, r in T.items()}
assert p["H3"] > p["H2"] > p["HS"] > p["OV"] > p["TM"] > p["PD"] == p["BL"] > p["CR"] > p["KD"]
# 7. builder floor guard fires on a price below floor and is silent on the real one
prod = {"model": "PD", "side": "front"}
assert bb.price_for(cfg["pricing"]["models"], prod, "M") == 10990 and bb.price_for(cfg["pricing"]["models"], prod, "XG") == 10990 + 800
assert bb.price_for(cfg["pricing"]["models"], {"model": "ZZ"}, "M") is None
low = json.loads(json.dumps(cfg["pricing"]["models"])); low["PD"]["price_front_centavos"] = 6000
produtos = [{"codigo": "SHI-LN-CL-F-LT", "nome": "Camiseta Shih Tzu Linha Classico Frente Clara", "modelo": {"codigo": "CAMP"}}]
vars_ = [{"produto": "SHI-LN-CL-F-LT", "sku": "SHI-LN-CL-F-LT-BRAN-M", "sku_padrao": "SHI-LN-CL-F-LT-BRAN-M", "cor": {"codigo": "BRAN", "nome": "Branco"}, "tamanho": "M", "disponivel": True, "preco_unitario_centavos": 5453}]
assert not [w for w in bb.build(produtos, vars_, models=cfg["pricing"]["models"])["warnings"] if "FLOOR" in w]
assert [w for w in bb.build(produtos, vars_, models=low)["warnings"] if "FLOOR" in w]

# 8. planned matrix: 19 breeds x 12 designs x 2 tones x 11 models, every code parses back and is unique
syn = [{"code": f"B{i:02d}", "name": f"Raca {i}"} for i in range(16)] + json.load(open(os.path.join(here, "..", "config", "br_breeds.json")))["new"]
assert len(syn) == 19 and {b["code"] for b in syn} >= {"LHA", "MPN", "VLT"}
rows = list(bm.matrix(syn))
assert len(rows) == 19 * 12 * 2 * 11 == 5016 and len({r["code"] for r in rows}) == 5016
for r in rows:
    meta = bb.parse_code(r["code"]); assert meta and meta["model"] == r["model"] and meta["breed"] == r["breed"], r["code"]
    assert (r["model"] == "PD") == (len(r["code"].split("-")) == 5)          # Padrao keeps the original 5-segment SKU
assert bm.count(rows)["variants"] > 0
assert bb.parse_code("SHI-LN-CL-F-LT") ["model"] == "PD" and bb.parse_code("SHI-LN-CL-F-LT-BL")["model"] == "BL" and bb.parse_code("SHI-LN-CL-F-LT-ZZ") is None
print("pricing tests OK:", {c: f"{r['price_centavos']/100:.2f}" for c, r in T.items()})

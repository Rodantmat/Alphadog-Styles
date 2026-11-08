#!/usr/bin/env python3
"""Build the Brazilian storefront catalog from a Gubo catalog dump (GET /catalogo/produtos + /catalogo/variantes).

The Gubo API is read-only for products (they are created in the Studio), so this script never guesses breeds or SKUs:
everything comes from the dump. It tolerates the two SKU spellings seen so far:
  owner pattern : {BREED}-{LN|GE}-{CL|OC|CO}-{F|B}-{DK|LT}        e.g. SHI-LN-CL-F-LT
  probe pattern : {BREED}-{LINE|GEO}-{CLASSIC|COOL|HEART}-{F|B}-{DK|LT}  e.g. CAV-LINE-CLASSIC-F-DK
  other models  : the same code + a 6th MODEL segment (PD = Camiseta Padrao has NO segment, so existing SKUs are unchanged):
                  OV oversized, TM tech modal, BL babylook, CR cropped, KD infantil, H2/H3 moletom capuz 2/3 cabos, HS moletom sem capuz, EC ecobag, PT pet
                  e.g. SHI-LN-CL-F-LT-BL  -> variant SKU SHI-LN-CL-F-LT-BL-BRAN-M
Variant SKU = <product>-<colour>-<size> (Gubo docs: sku_padrao).

usage: build_br_catalog.py --produtos P.json --variantes V.json [--cores C.json] [--out br/site/data/catalog_br.json]
Dumps may be raw API bodies, {"dados":[...]} or the [status, body] pairs saved by scripts/brazil/gubo_probe.py.
Exit code 2 if nothing parseable was found.
"""
import argparse, json, os, re, sys, unicodedata, datetime

THEME = {"LN": "line", "LINE": "line", "GE": "geo", "GEO": "geo", "GEOM": "geo", "GEOMETRIC": "geo"}
STYLE = {"CL": "classic", "CLASSIC": "classic", "OC": "cool", "COOL": "cool", "CO": "heart", "HEART": "heart"}
SIDE = {"F": "front", "B": "back"}
TONE = {"DK": "dark", "LT": "light"}
MODEL = {"OV": "Camiseta Oversized", "TM": "Camiseta Tech Modal", "BL": "Babylook", "CR": "Cropped", "KD": "Camiseta Infantil",
         "H2": "Moletom com capuz (2 cabos)", "H3": "Moletom com capuz (3 cabos)", "HS": "Moletom sem capuz", "EC": "Ecobag", "PT": "Camiseta Pet"}
MODEL_NAME = {"PD": "Camiseta Padrão", **MODEL}                                   # PD is implicit (5-segment code)
THEME_PT = {"line": "Linha contínua", "geo": "Geométrico"}
STYLE_PT = {"classic": "Clássico", "cool": "Óculos escuros", "heart": "Coração"}
SIDE_PT = {"front": "Frente", "back": "Costas"}
# Cosmetic swatches only. Hex values other than Preto (taken from the Gubo docs example) are approximations -> TODO-verify via /dominios/cores
COLOR_FALLBACK = {
    "PRET": ("Preto", "#1A1A1A", "dark"), "MAR": ("Marrom", "#5B4636", "dark"), "VMG": ("Verde Musgo", "#4B5320", "dark"),
    "AZM": ("Azul Marinho", "#1F2A44", "dark"), "BRAN": ("Branco", "#FFFFFF", "light"), "OFWH": ("Offwhite", "#F2EDE1", "light"),
}
NAME_PREFIX = re.compile(r"^\s*(?:(?:(?:Camiseta|Camisa|Moletom|Padr[aã]o|Babylook|Baby\s?look|Cropped|Oversized|Tech\s+Modal|Infantil|Ecobag|Pet|Canguru|Com|Sem|Capuz|[23]|Cabos?)\b|[()])\s*)+", re.I)
BREED_CUT = re.compile(r"\s+(Linha|Geom[eé]tric[oa]?|Geometria|Cl[aá]ssic[oa]?|Classic|Cool|Heart|Cora[cç][aã]o|[OÓ]culos|Frente|Costas)\b", re.I)


def unwrap(x):
    """Return a list of records from any of the dump shapes."""
    if isinstance(x, list) and len(x) == 2 and isinstance(x[0], int) and isinstance(x[1], (dict, list)):
        x = x[1]
    if isinstance(x, dict):
        for k in ("dados", "data", "items"):
            if k in x and isinstance(x[k], list):
                return x[k]
        return [x]
    return x if isinstance(x, list) else []


def load(path):
    if not path:
        return []
    with open(path, encoding="utf-8") as f:
        raw = json.load(f)
    if isinstance(raw, list) and raw and isinstance(raw[0], list):   # list of pages [[200, body], ...]
        out = []
        for pg in raw:
            out += unwrap(pg)
        return out
    return unwrap(raw)


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "_", s).strip("_")


def parse_code(code):
    p = str(code).upper().split("-")
    if len(p) not in (5, 6):
        return None
    b, th, st, sd, tn = p[:5]
    mdl = p[5] if len(p) == 6 else "PD"
    if mdl != "PD" and mdl not in MODEL:
        return None
    if th in THEME and st in STYLE and sd in SIDE and tn in TONE:
        return {"breed": b, "theme": THEME[th], "style": STYLE[st], "side": SIDE[sd], "tone": TONE[tn], "model": mdl}
    return None


def breed_name(nome, code_breed):
    n = NAME_PREFIX.sub("", nome or "")
    m = BREED_CUT.search(n)
    n = (n[:m.start()] if m else n).strip()
    return n or code_breed


def price_for(models, p, size):
    """Mirror of worker priceCentavos(size, p). None if the model has no price."""
    m = (models or {}).get(p.get("model") or "PD")
    if not m:
        return None
    base = m["price_back_centavos"] if p.get("side") == "back" else m["price_front_centavos"]
    return base + (m.get("size_surcharge_centavos", 0) if size in m.get("surcharge_sizes", []) else 0)


def load_models():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "br_config.json"), encoding="utf-8") as f:
            return json.load(f)["pricing"].get("models")
    except (OSError, KeyError, ValueError):
        return None


LABEL_CENTAVOS = 150     # custom brand label (Gubo price page); the owner requires it on every piece
FLOOR = 1.15             # owner rule: price >= (cost + label) + 15%


def build(produtos, variantes, cores=None, models="config"):
    models = load_models() if models == "config" else models
    warnings = []
    colors = {k: {"name": v[0], "hex": v[1], "tone": v[2], "approx": k != "PRET"} for k, v in COLOR_FALLBACK.items()}
    for c in cores or []:
        if c.get("codigo"):
            old = colors.get(c["codigo"], {})
            colors[c["codigo"]] = {"name": c.get("nome", old.get("name", c["codigo"])), "hex": c.get("hex", old.get("hex", "#888888")),
                                   "tone": old.get("tone", "dark"), "approx": "hex" not in c}
    byprod = {}
    for v in variantes:
        byprod.setdefault(v["produto"], []).append(v)
    breeds, prods = {}, []
    for p in produtos:
        code = p["codigo"]
        meta = parse_code(code)
        if not meta:
            warnings.append(f"skip product {code}: code does not match the breed/theme/style/side/tone pattern")
            continue
        bname = breed_name(p.get("nome"), meta["breed"])
        breeds.setdefault(meta["breed"], {"code": meta["breed"], "slug": slug(bname), "name": bname})
        vs = byprod.get(code, [])
        avail = [v for v in vs if v.get("disponivel")]
        if not avail:
            warnings.append(f"product {code} has no available variant (not released in Studio yet?) - kept but hidden")
        cols, sizes, costs = {}, [], {}
        for v in avail:
            cols.setdefault(v["cor"]["codigo"], []).append(v["tamanho"])
            costs[v["tamanho"]] = v.get("preco_unitario_centavos")
            if v["cor"]["codigo"] not in colors:
                colors[v["cor"]["codigo"]] = {"name": v["cor"]["nome"], "hex": "#888888", "tone": meta["tone"], "approx": True}
                warnings.append(f"colour {v['cor']['codigo']} has no known hex")
            if v["sku"] != v.get("sku_padrao") and v.get("sku_padrao"):
                warnings.append(f"{v['sku_padrao']} is linked to store SKU {v['sku']} - storefront uses sku_padrao (both accepted by Gubo)")
        for t in sorted({t for ts in cols.values() for t in ts}, key=lambda s: ["P", "M", "G", "GG", "XG", "XGG"].index(s) if s in ["P", "M", "G", "GG", "XG", "XGG"] else (100 + int(s) if s.isdigit() else 99)):
            sizes.append(t)
        if models:
            for t, c in costs.items():
                pr = price_for(models, meta, t)
                if pr is None:
                    warnings.append(f"product {code}: model {meta['model']} has no configured price - the worker will refuse to sell it")
                elif c and pr < FLOOR * (c + LABEL_CENTAVOS):
                    warnings.append(f"PRICE BELOW FLOOR: {code} size {t} price {pr} < 1.15 x (Gubo cost {c} + label {LABEL_CENTAVOS})")
        prods.append({"code": code, **meta, "name": p.get("nome"), "image": p.get("imagem_url"), "gubo_model": (p.get("modelo") or {}).get("codigo"),
                      "colors": {k: sorted(set(v)) for k, v in cols.items()}, "sizes": sizes, "cost_centavos": costs, "visible": bool(avail)})
    prods.sort(key=lambda x: x["code"])
    return {
        "generated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": "gubo_api_dump",
        "currency": "BRL",
        "labels": {"theme": THEME_PT, "style": STYLE_PT, "side": SIDE_PT, "model": MODEL_NAME},
        "colors": colors,
        "breeds": sorted(breeds.values(), key=lambda b: b["name"]),
        "products": prods,
        "warnings": warnings,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--produtos", required=True)
    ap.add_argument("--variantes", required=True)
    ap.add_argument("--cores")
    ap.add_argument("--out", default="br/site/data/catalog_br.json")
    ap.add_argument("--public", action="store_true", help="strip Gubo cost from the output (use for the storefront copy)")
    a = ap.parse_args()
    cat = build(load(a.produtos), load(a.variantes), load(a.cores))
    if not cat["products"]:
        print("no parseable products", file=sys.stderr); sys.exit(2)
    if a.public:
        for p in cat["products"]:
            p.pop("cost_centavos", None)
    with open(a.out, "w", encoding="utf-8") as f:
        json.dump(cat, f, ensure_ascii=False, separators=(",", ":"))
    vis = [p for p in cat["products"] if p["visible"]]
    print(f"products {len(cat['products'])} (visible {len(vis)}), breeds {len(cat['breeds'])}, colours {len(cat['colors'])}, warnings {len(cat['warnings'])}")
    for w in cat["warnings"][:20]:
        print("  warn:", w)


if __name__ == "__main__":
    main()

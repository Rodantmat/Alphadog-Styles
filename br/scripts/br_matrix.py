#!/usr/bin/env python3
"""The PLANNED Brazilian catalog matrix: breeds x 12 designs x 2 tones x models, with SKU codes and Gubo Studio product names.
Used (a) as the checklist of products to create in Gubo Studio (the API cannot create products), (b) by tests to prove every code round-trips
through build_br_catalog.parse_code and the worker's SKU resolver, (c) to count variants.  Nothing here is sold: the live catalog is whatever
the Gubo sync finds with disponivel=true.

SKU:  {BREED}-{LN|GE}-{CL|OC|CO}-{F|B}-{DK|LT}[-{MODEL}]-{COLOR}-{SIZE}      MODEL absent = Camiseta Padrao (PD), so existing SKUs never change.
usage: br_matrix.py [--breeds FILE] [--csv out.csv] [--models PD,BL]      prints counts
"""
import csv, importlib.util, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("bb", os.path.join(HERE, "build_br_catalog.py")); bb = importlib.util.module_from_spec(spec); spec.loader.exec_module(bb)
spec = importlib.util.spec_from_file_location("bp", os.path.join(HERE, "br_pricing.py")); bp = importlib.util.module_from_spec(spec); spec.loader.exec_module(bp)

THEMES = [("LN", "Linha"), ("GE", "Geometrico")]
STYLES = [("CL", "Classico"), ("OC", "Oculos"), ("CO", "Coracao")]
SIDES = [("F", "Frente"), ("B", "Costas")]
TONES = [("DK", "Escura", ["PRET", "MAR", "VMG", "AZM"]), ("LT", "Clara", ["BRAN", "OFWH"])]   # colours: PRET verified, others from the Gubo probe (availability per model UNVERIFIED)


def breeds(path=None):
    d = json.load(open(path or os.path.join(HERE, "..", "config", "br_breeds.json"), encoding="utf-8"))
    return d["approved"] + d["new"]


def product_code(breed, th, st, sd, tn, model="PD"):
    c = f"{breed}-{th}-{st}-{sd}-{tn}"
    return c if model == "PD" else f"{c}-{model}"


def matrix(breed_list, models=None):
    for m in models or list(bp.MODELS):
        for b in breed_list:
            for th, thn in THEMES:
                for st, stn in STYLES:
                    for sd, sdn in SIDES:
                        for tn, tnn, cols in TONES:
                            code = product_code(b["code"], th, st, sd, tn, m)
                            yield {"code": code, "model": m, "breed": b["code"], "name": f"{'Camiseta' if m == 'PD' else bp.MODELS[m][0]} {b['name']} {thn} {stn} {sdn} {tnn}",
                                   "colors": cols, "sizes": bp.MODELS[m][4], "price_centavos": bp.row(m)["price_centavos"], "compare_at_centavos": bp.row(m)["compare_at_centavos"]}


def count(rows):
    rows = list(rows)
    return {"products": len(rows), "variants": sum(len(r["colors"]) * len(r["sizes"]) for r in rows)}


if __name__ == "__main__":
    a = sys.argv[1:]
    bl = breeds(a[a.index("--breeds") + 1] if "--breeds" in a else None)
    ms = a[a.index("--models") + 1].split(",") if "--models" in a else None
    rows = list(matrix(bl, ms))
    print(len(bl), "breeds ->", count(rows))
    if "--csv" in a:
        with open(a[a.index("--csv") + 1], "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f); w.writerow(["codigo", "modelo", "nome", "cores", "tamanhos", "preco_centavos", "de_centavos"])
            for r in rows:
                w.writerow([r["code"], r["model"], r["name"], " ".join(r["colors"]), " ".join(r["sizes"]), r["price_centavos"], r["compare_at_centavos"]])

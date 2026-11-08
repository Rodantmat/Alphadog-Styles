#!/usr/bin/env python3
"""Proportional BRL price table for the pt-BR store (single source: this file's INPUTS; output lands in br/config/br_config.json -> pricing.models).

Method (NOT a currency conversion):
  1. C   = Gubo cost of the model with the owner's brand label, at the CARD price (conservative; Pix is ~5% lower)
         = (garment + print tier + label) * CARD_FACTOR
  2. L   = compare-at ("de") price = C * K_US, rounded UP to the next ...90.   K_US = US retail / Printify cost of the same class
           tee-like K = 27.99/11.29 (Bella+Canvas 3001, one print side); hoodie-like K = 49.99/21.58 (Gildan 18500, one print side)
  3. P   = selling price = L * DISC, rounded to the nearest ...90.            DISC = 109.90/139.90 (owner's retail / crossed-out ratio)
  4. P is raised to the next ...90 if it is below FLOOR (>= 1.15 x cost incl. label AND after the card fee); accessories are capped (market sanity)
  5. XG/XGG surcharge = US 2XL surcharge share (200/2799 tee, 400/4999 hoodie) of P, rounded to whole reais.
usage: br_pricing.py            print the table
       br_pricing.py --write    update br/config/br_config.json (pricing.models) in place
"""
import json, math, os, sys

PIX = {  # Gubo "precos" page, 2026-11-07 (VERIFIED in docs/brazil_data/BR_PRODUCERS.md section 3.1), centavos, Pix price of the plain piece
    "PD": 3990, "OV": 5890, "TM": 5490, "BL": 3990, "CR": 2590, "KD": 2590, "H2": 9990, "H3": 12990, "HS": 7890, "EC": 2590, "PT": 2590}
PRINT_PIX = {"P": 590, "M": 890, "G": 1190, "X": 1690}   # small <=350cm2, medium <=700, large <=1050, mega <=1400 (VERIFIED, same page)
LABEL = 150                                              # custom printed label R$1,50 (VERIFIED, same page); owner requires the brand label
CARD_FACTOR = 5453 / 5180                                # observed 2026-11-07 probe: R$54,53 card vs R$51,80 Pix for tee + large print (VERIFIED for PD only; assumed equal for other models = UNVERIFIED)
K_TEE = 2799 / 1129                                      # US: Premium Tee $27.99 / Printify BC3001 cost $11.29 (store/data/catalog.json; out/fabric2.json)
K_HOOD = 4999 / 2158                                     # US: Heavy Hoodie $49.99 / Printify G18500 cost $21.58 (out/costs.json hoodie_pocket)
DISC = 10990 / 13990                                     # owner: retail R$109,90 vs crossed-out R$139,90
FLOOR = 1.15                                             # owner: price >= (cost + label) + 15%
FEE_CARD = 0.0498                                        # Mercado Pago card, instant (UNVERIFIED secondary source, br_config.json fees_note)
SUR_PCT = {"tee": 200 / 2799, "hood": 400 / 4999}        # US 2XL surcharge share
MODELS = {  # code: (name_pt, class, tier, cap_centavos or None, sizes (UNVERIFIED except PD), surcharge?)
    "PD": ("Camiseta Padrão", "tee", "G", None, ["P", "M", "G", "GG", "XG", "XGG"], True),
    "OV": ("Camiseta Oversized", "tee", "G", None, ["P", "M", "G", "GG", "XG"], True),
    "TM": ("Camiseta Tech Modal", "tee", "G", None, ["P", "M", "G", "GG", "XG"], True),
    "BL": ("Babylook", "tee", "G", None, ["P", "M", "G", "GG"], False),
    "CR": ("Cropped", "tee", "G", None, ["P", "M", "G"], False),
    "KD": ("Camiseta Infantil", "tee", "M", None, ["2", "4", "6", "8", "10", "12", "14"], False),
    "H2": ("Moletom com capuz (2 cabos)", "hood", "G", None, ["P", "M", "G", "GG", "XG"], True),
    "H3": ("Moletom com capuz (3 cabos)", "hood", "G", None, ["P", "M", "G", "GG", "XG"], True),
    "HS": ("Moletom sem capuz", "hood", "G", None, ["P", "M", "G", "GG", "XG"], True),
    "EC": ("Ecobag", "tee", "G", 5990, ["UN"], False),
    "PT": ("Camiseta Pet", "tee", "M", 5990, ["P", "M", "G"], False),
}
MODEL_DESC = {"PD": "Camiseta 100% algodão (fio penteado 30.1, 170 g)"}   # only claims verified for PD; others get just the model name


def ceil90(c):   # next price ending ...90 at or above c (centavos)
    return math.ceil((c - 90) / 100) * 100 + 90


def near90(c):
    return round((c - 90) / 100) * 100 + 90


def row(code, side_tier=None):
    name, cls, tier, cap, sizes, sur = MODELS[code]
    tier = side_tier or tier
    cost = round((PIX[code] + PRINT_PIX[tier] + LABEL) * CARD_FACTOR)
    k = K_HOOD if cls == "hood" else K_TEE
    floor_price = ceil90(math.ceil(FLOOR * cost / (1 - FEE_CARD)))
    cmp_ = ceil90(round(k * cost))
    price = max(near90(round(cmp_ * DISC)), floor_price)
    capped = False
    if cap and price > cap:
        price, capped = cap, True
        cmp_ = max(ceil90(round(price / DISC)), price)
    surcharge = round(SUR_PCT[cls] * price / 100) * 100 if sur else 0
    return {"code": code, "name": name, "class": cls, "tier": tier, "cost_card_centavos": cost, "compare_at_centavos": cmp_, "price_centavos": price,
            "floor_centavos": floor_price, "size_surcharge_centavos": surcharge, "capped": capped, "sizes": sizes,
            "net_over_cost_pct": round((price * (1 - FEE_CARD) - cost) / cost * 100, 1), "off_pct": round((1 - price / cmp_) * 100, 1)}


def table():
    out = {}
    for c in MODELS:
        r = row(c)
        worst = row(c, "X")                       # if Gubo bills the print as MEGA (art > 1050 cm2) the price must still clear the floor
        r["floor_ok_if_mega"] = r["price_centavos"] >= round(FLOOR * worst["cost_card_centavos"] / (1 - FEE_CARD) - 100)
        out[c] = r
    return out


def models_config():
    """Compact, public (no costs) block for br_config.json."""
    t = table()
    return {c: {"name": r["name"], "class": r["class"], "price_front_centavos": r["price_centavos"], "price_back_centavos": r["price_centavos"],
                "compare_at_centavos": r["compare_at_centavos"], "size_surcharge_centavos": r["size_surcharge_centavos"],
                "surcharge_sizes": ["XG", "XGG"], "sizes": r["sizes"], "desc": MODEL_DESC.get(c, r["name"])} for c, r in t.items()}


def brl(c):
    return f"R$ {c // 100},{c % 100:02d}"


if __name__ == "__main__":
    t = table()
    print(f"{'cod':3} {'modelo':30} {'custo*':>9} {'de':>9} {'por':>9} {'piso':>9} {'XG+':>5} {'liq/custo':>9} {'off':>5}")
    for c, r in t.items():
        print(f"{c:3} {r['name']:30} {brl(r['cost_card_centavos']):>9} {brl(r['compare_at_centavos']):>9} {brl(r['price_centavos']):>9} {brl(r['floor_centavos']):>9} {r['size_surcharge_centavos']//100:>5} {r['net_over_cost_pct']:>8}% {r['off_pct']:>4}%{' CAP' if r['capped'] else ''}{'' if r['floor_ok_if_mega'] else ' MEGA-FAIL'}")
    if "--write" in sys.argv:
        p = os.path.join(os.path.dirname(__file__), "..", "config", "br_config.json")
        cfg = json.load(open(p, encoding="utf-8")); cfg["pricing"]["models"] = models_config()
        cfg["pricing"]["models_note"] = "Generated by br/scripts/br_pricing.py (proportional method, see br/docs/pricing.md). Do not hand-edit; change the inputs there. Sizes of models other than PD are UNVERIFIED until the catalog sync reads Gubo."
        cfg["pricing"]["compare_at_note"] = "Display only (crossed-out price). The US store shows no compare-at price; this is the owner's BR marketing device (R$139,90 -> R$109,90)."
        json.dump(cfg, open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=2); open(p, "a").write("\n"); print("written")

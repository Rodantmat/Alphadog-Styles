"""Amazon US listings for AlphaDog Styles (Option 2: breed groups, ~36 parent listings, Size x Color variations).
READ-ONLY planning: writes store/data/amazon_feed.json. Nothing is sent to Amazon from here.

Rules (owner, Nov 2026):
 - prices = the approved table (store/data/catalog.json via market_plan.price) - never invented here
 - breed + design go inside the Color value ("Frenchie · Line Art · White"); only Size and Color vary
 - SKU = the same encoded SKU as eBay/TikTok (decode() in market_plan.py turns it back into a store order item -> Printify)
 - free shipping is built into the prices
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_plan as M
import market_text as T

ROOT = M.ROOT
SITE = "https://alphadogstyles.com/mk/"
PER_PRODUCT = 6            # breed groups per product -> 6 products x 6 = 36 listings
CHILD_CAP = int(os.environ.get("AMZ_CHILD_CAP", "800"))   # max children (breed x design x color x size) per parent; adjustable
M.CAP["amazon"] = CHILD_CAP

PTYPE = {"tee": "SHIRT", "hoodie": "SWEATSHIRT", "wtank": "SHIRT", "tank": "SHIRT", "polo": "SHIRT", "cap": "HAT"}
# Amazon standardized colour (20-value list) for each display colour name
STD = [("white", "White"), ("cream", "Off White"), ("natural", "Beige"), ("sand", "Beige"), ("stone", "Beige"), ("khaki", "Beige"), ("black", "Black"),
       ("navy", "Blue"), ("light blue", "Blue"), ("blue", "Blue"), ("tahiti", "Blue"), ("indigo", "Blue"), ("pink", "Pink"), ("maroon", "Red"), ("red", "Red"),
       ("forest", "Green"), ("military", "Green"), ("green", "Green"), ("spruce", "Green"), ("mint", "Green"), ("camo", "Green"), ("orange", "Orange"),
       ("peach", "Orange"), ("asphalt", "Grey"), ("charcoal", "Grey"), ("ash", "Grey"), ("heather", "Grey"), ("grey", "Grey"), ("gray", "Grey")]
def std_color(name):
    n = name.lower()
    for k, v in STD:
        if k in n: return v
    return "Multicolor"
CS = {"Soft Cream": "Cream", "Athletic Heather": "Heather", "Light Blue": "Lt Blue", "Soft Pink": "Pink", "Sport Grey": "Grey", "Light Pink": "Pink",
      "Heather Grey": "Grey", "Solid Tahiti Blue": "Blue", "Solid Mint": "Mint", "Solid Light Orange": "Peach", "Solid White": "White", "Solid Black": "Black",
      "Solid Midnight Navy": "Navy", "J. Navy": "Navy", "Dark Grey Heather": "Dark Grey", "Solid Military Green": "Military Green", "Solid Indigo": "Indigo"}
FABRIC_SHORT = {"tee": "Airlume combed and ring-spun cotton (heathers include polyester)", "hoodie": "50% cotton, 50% polyester",
                "tank": "Airlume combed and ring-spun cotton (heathers include polyester)", "wtank": "cotton/polyester blend",
                "polo": "cotton-blend pique", "cap": "cotton twill (foam/mesh trucker styles include polyester)"}
MATERIAL = {"tee": "Cotton", "hoodie": "Cotton Blend", "tank": "Cotton", "wtank": "Cotton Blend", "polo": "Cotton Blend", "cap": "Cotton"}
NOUN_SHORT = {"tee": "T-Shirt", "hoodie": "Hoodie", "wtank": "Women's Racerback Tank", "tank": "Tank Top", "polo": "Polo Shirt", "cap": "Hat"}

# per-listing image lookup built from the images already generated for eBay / Etsy / TikTok listings (same real Printify mockups)
IM = json.load(open(f"{ROOT}/store/data/market_images.json"))
def img_lookup():
    L = {}
    for lid, m in IM.items():
        pk = lid.split("-")[1]
        d = L.setdefault(pk, {"bd": {}, "bdc": {}, "hero": {}})
        d["bd"].update(m.get("bd", {})); d["bdc"].update(m.get("bdc", {}))
        for h in m.get("hero", []):
            p = h.split("/")
            if len(p) >= 2: d["hero"].setdefault(p[1], []).append(h)
    return L
IMG = img_lookup()
def child_image(pk, b, dc, cc):
    d = IMG.get(pk, {})
    return d.get("bdc", {}).get(f"{b}|{dc}|{cc}") or d.get("bd", {}).get(f"{b}|{dc}") or (d.get("hero", {}).get(b) or [None])[0]

def color_value(L, b, dc, cc, C, D):
    cname = C[cc]["name"]; cname = CS.get(cname, cname)
    dn = D[dc]["short"] if L["prod"] != "cap" else D[dc]["name"]
    parts = [M.short(b)] + [dn, cname]
    return " · ".join(parts)[:120]

def bullets(L, P):
    pk = L["prod"]; dn = ", ".join(sorted({d["name"] for d in P["designs"] if d["code"] in L["designs"]}))
    br = T.names(L["breeds"])
    b = [f"ORIGINAL DOG ART: minimalist {br} artwork by AlphaDog Styles - pick your breed and design in the Color menu",
         f"DESIGNS: {dn}"[:240],
         f"FABRIC AND FIT: {T.FABRIC[pk]}"[:240],
         "MADE TO ORDER IN THE USA: printed just for you, tracking included. Production 2-5 business days, then 3-7 business days in transit",
         "PERFECT GIFT for dog moms, dog dads and every dog lover. Finished with the AlphaDog Styles logo label" if pk != "cap" else
         "PERFECT GIFT for dog moms, dog dads and every dog lover. Durable print made to last"]
    return [x[:255] for x in b]

def build():
    plan = M.build()   # re-derive the base tables (products, designs, colors); amazon listings are built below
    out = []
    for pk, P in M.PRODUCTS.items():
        PP = plan["products"][pk]; D = {d["code"]: d for d in PP["designs"]}; C = {c["code"]: c for c in PP["colors"]}
        for i, br in enumerate(M.groups(PER_PRODUCT)):
            nD, nC = M.fill("amazon", pk, len(br)); fam = M.famname(br)
            L = {"id": f"amazon-{pk}-{i+1:02d}", "plat": "amazon", "prod": pk, "breeds": br, "family": fam,
                 "designs": [d[0] for d in P["designs"][:nD]], "colors": [c[0] for c in P["colors"][:nC]], "sizes": P["sizes"]}
            L["title"] = ("AlphaDog Styles " + M.title("tiktok", pk, br, fam))[:200]
            kids = []
            for b in br:
                for dc in L["designs"]:
                    for cc in L["colors"]:
                        cv = color_value(L, b, dc, cc, C, D)
                        for s in L["sizes"]:
                            kids.append({"sku": M.sku(pk, b, dc, cc, s), "color": cv, "color_std": std_color(C[cc]["color"]), "size": s,
                                         "price": M.price(C[cc]["prod"], s), "img": child_image(pk, b, dc, cc), "breed": b, "design": dc, "cc": cc})
            assert len({(k["color"], k["size"]) for k in kids}) == len(kids), L["id"]       # Amazon needs unique Color x Size
            assert len({k["sku"] for k in kids}) == len(kids), L["id"]
            heroes = []
            for b in br:
                heroes += (IMG.get(pk, {}).get("hero", {}).get(b) or [])[:2]
            out.append({"id": L["id"], "prod": pk, "ptype": PTYPE[pk], "title": L["title"], "parent_sku": f"AMZ-P-{pk}-{i+1:02d}",
                        "desc": T.description({**L, "plat": "etsy"}).replace("\n\n", "\n"), "bullets": bullets(L, PP),
                        "fabric": FABRIC_SHORT[pk], "material": MATERIAL[pk], "noun": NOUN_SHORT[pk],
                        "heroes": [SITE + h for h in heroes[:8]], "children": kids})
    return out

if __name__ == "__main__":
    f = build()
    json.dump(f, open(f"{ROOT}/store/data/amazon_feed.json", "w"), separators=(",", ":"))
    tot = sum(len(x["children"]) for x in f)
    print(len(f), "parent listings,", tot, "child SKUs; max/parent", max(len(x["children"]) for x in f), "(cap", CHILD_CAP, ")")
    from collections import Counter
    print("breeds covered:", len({b for x in f for k in x["children"] for b in [k["breed"]]}), "of", len(M.BR))
    print("children without image:", sum(1 for x in f for k in x["children"] if not k["img"]))
    print("price range per product:", {pk: (min(k["price"] for x in f if x["prod"] == pk for k in x["children"]), max(k["price"] for x in f if x["prod"] == pk for k in x["children"])) for pk in M.PRODUCTS})
    for x in f: print(f"  {x['id']:16} {x['ptype']:10} kids={len(x['children']):4} {x['title'][:90]}")
    print("longest color value:", max(len(k["color"]) for x in f for k in x["children"]))
    # every SKU must decode back to a store order item
    plan = json.load(open(f"{ROOT}/store/data/market_plan.json")); bad = 0
    for x in f:
        for k in x["children"]:
            it = M.decode(plan, k["sku"])
            if not it: bad += 1
    print("SKU decode failures:", bad)

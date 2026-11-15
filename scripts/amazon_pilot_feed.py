"""PILOT listing in the new Amazon structure: ONE parent = Tee x placement 'Emblem + Back' x style 'Line Art' (design 1).
Variation theme STYLE_NAME/COLOR_NAME/SIZE_NAME -> Style = Breed (all 33), Color, Size. Writes store/data/amazon_pilot.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_plan as M
ROOT = M.ROOT
PK = "tee"; DC = os.environ.get("LDC", "1")
LIST = {"1": dict(id="pilot-tee-1", out="amazon_pilot.json", gal="amazon_gallery.json", psku="AMZ-P-tee-d1", art="Line Art", artd="Minimalist continuous line art", pk="minimalist line art"),
        "4": dict(id="listing-tee-4", out="amazon_listing_tee4.json", gal="amazon_gallery_d4.json", psku="AMZ-P-tee-d4", art="Geometric Art", artd="Bold geometric faceted illustration", pk="geometric art"),
        "3": dict(id="listing-tee-3", out="amazon_listing_tee3.json", gal="amazon_gallery_d3.json", psku="AMZ-P-tee-d3", art="Line Art Heart", artd="Minimalist continuous line art with a heart", pk="line art with a heart"),
        "7": dict(id="listing-tee-7", out="amazon_listing_tee7.json", gal="amazon_gallery_d7.json", psku="AMZ-P-tee-d7", art="Geometric Sunglasses", artd="Bold geometric faceted illustration with cool sunglasses", pk="geometric art with sunglasses"),
        "8": dict(id="listing-tee-8", out="amazon_listing_tee8.json", gal="amazon_gallery_d8.json", psku="AMZ-P-tee-d8", art="Line Art Sunglasses", artd="Minimalist continuous line art with cool sunglasses", pk="line art with sunglasses"),
        "9": dict(id="listing-tee-9", out="amazon_listing_tee9.json", gal="amazon_gallery_d9.json", psku="AMZ-P-tee-d9", art="Geometric Heart", artd="Bold geometric faceted illustration with a heart", pk="geometric art with a heart")}[DC]
COLORS = ["WH", "BK", "NV", "AS", "LB", "HE", "PK", "CR", "NA", "MR"]
plan = M.build(); PP = plan["products"][PK]; C = {c["code"]: c for c in PP["colors"]}
EX = json.load(open(f"{ROOT}/store/data/amazon_extras.json")); GAL = json.load(open(f"{ROOT}/store/data/{LIST['gal']}"))
STD = {"WH": "White", "BK": "Black", "NV": "Blue", "AS": "Grey", "LB": "Blue", "HE": "Grey", "PK": "Pink", "CR": "Off White", "NA": "Beige", "MR": "Red"}
NAME = {"WH": "White", "BK": "Black", "NV": "Navy", "AS": "Ash", "LB": "Light Blue", "HE": "Athletic Heather", "PK": "Soft Pink", "CR": "Soft Cream", "NA": "Natural", "MR": "Maroon"}
kids = []; skipped = []
for b in M.BR:
    for cc in COLORS:
        e = GAL.get(f"{b}|{cc}") or {}
        if e.get("main") != "ok": skipped.append((b, cc, "no main")); continue
        base = f"amz/{PK}/{b}/{DC}{cc}"
        g = (GAL.get(f"{b}|{cc}") or {}).get("g", [])
        extra = [base + "_g%d.jpg" % (i + 1) for i, t in enumerate(g) if t == "ok"][:8]      # real Printify photos: back, people wearing it, hanger/folded, lifestyle (all 8 slots overwritten)
        for s in PP["sizes"]:
            kids.append({"sku": M.sku(PK, b, DC, cc, s), "style": M.BR[b], "breed": b, "color": NAME[cc], "color_std": STD[cc], "cc": cc, "size": s,
                         "price": M.price(C[cc]["prod"], s), "img": base + ".jpg", "others": extra,
                         "title": f"AlphaDog Styles Unisex T-Shirt for Adults - {M.BR[b]} {LIST['art']}, Front Emblem and Full Body Back, {NAME[cc]}"[:200]})
assert len({(k["style"], k["color"], k["size"]) for k in kids}) == len(kids)
assert len({k["sku"] for k in kids}) == len(kids)
plan_j = json.load(open(f"{ROOT}/store/data/market_plan.json")); bad = sum(1 for k in kids if not M.decode(plan_j, k["sku"]))
F = {"id": LIST["id"], "prod": PK, "ptype": "SHIRT", "theme": "STYLE_NAME/COLOR_NAME/SIZE_NAME", "parent_sku": LIST["psku"],
     "title": f"AlphaDog Styles Unisex T-Shirt for Adults - Dog Breed {LIST['art']}, Front Emblem and Full Body Back Print",
     "desc": f"Wear your best friend. {LIST['artd']} of your dog's breed on a soft unisex tee: a small emblem portrait on the front and the full body drawing across the back.\n\nHOW TO ORDER\n1. Style: pick your breed.\n2. Color: pick the shirt color.\n3. Size: pick your size.\n\nFABRIC AND FIT\nBella+Canvas 3001 unisex jersey tee, about 4.2 oz, 100% Airlume combed and ring-spun cotton (heather shades include some polyester). Soft, lightweight retail fit that runs true to size - size up for a relaxed fit.\n\nDETAILS\n- Printed in the USA, made to order just for you.\n- Finished with the AlphaDog Styles logo label.\n- Production 2-5 business days, then 3-7 business days in transit within the US. Tracking included.\n\nCARE\nMachine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print.",
     "bullets": [f"ORIGINAL DOG ART: {LIST['pk']} of your dog's breed by AlphaDog Styles - pick your breed in the Style menu",
                 f"DESIGN: {LIST['art']} with a small emblem portrait on the front and a full body drawing across the back",
                 "FABRIC AND FIT: Bella+Canvas 3001 unisex jersey tee, about 4.2 oz, 100% Airlume combed and ring-spun cotton (heather shades include some polyester). Soft, lightweight retail fit that runs true to size",
                 "MADE TO ORDER IN THE USA: printed just for you, tracking included. Production 2-5 business days, then 3-7 business days in transit",
                 "PERFECT GIFT for dog moms, dog dads and every dog lover. Finished with the AlphaDog Styles logo label"],
     "fabric": "Airlume combed and ring-spun cotton (heathers include polyester)", "material": "Cotton", "noun": "T-Shirt", "heroes": [], "children": kids}
json.dump([F], open(f"{ROOT}/store/data/{LIST['out']}", "w"), separators=(",", ":"))
print("children", len(kids), "breeds", len({k['breed'] for k in kids}), "colors", len({k['color'] for k in kids}), "skipped", skipped[:10], "decode failures", bad)
print("price range", min(k["price"] for k in kids), max(k["price"] for k in kids), "| images per child", sorted({1 + len(k["others"]) for k in kids}))

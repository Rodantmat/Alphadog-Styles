"""PILOT listing in the new Amazon structure: ONE parent = Tee x placement 'Emblem + Back' x style 'Line Art' (design 1).
Variation theme STYLE_NAME/COLOR_NAME/SIZE_NAME -> Style = Breed (all 33), Color, Size. Writes store/data/amazon_pilot.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_plan as M
ROOT = M.ROOT
PK, DC = "tee", "1"
COLORS = ["WH", "BK", "NV", "AS"]
plan = M.build(); PP = plan["products"][PK]; C = {c["code"]: c for c in PP["colors"]}
EX = json.load(open(f"{ROOT}/store/data/amazon_extras.json"))
STD = {"WH": "White", "BK": "Black", "NV": "Blue", "AS": "Grey"}
NAME = {"WH": "White", "BK": "Black", "NV": "Navy", "AS": "Ash"}
kids = []; skipped = []
for b in M.BR:
    for cc in COLORS:
        e = EX.get(f"{b}|{cc}") or {}
        if e.get("main") != "ok": skipped.append((b, cc, "no main")); continue
        base = f"amz/{PK}/{b}/{DC}{cc}"
        extra = [base + s + ".jpg" for s, k in (("_b", "_b"), ("_c", "_c")) if e.get(k) == "ok"]
        for s in PP["sizes"]:
            kids.append({"sku": M.sku(PK, b, DC, cc, s), "style": M.BR[b], "breed": b, "color": NAME[cc], "color_std": STD[cc], "cc": cc, "size": s,
                         "price": M.price(C[cc]["prod"], s), "img": base + ".jpg", "others": extra,
                         "title": f"AlphaDog Styles Unisex T-Shirt for Adults - {M.BR[b]} Line Art, Front Emblem and Full Body Back, {NAME[cc]}"[:200]})
assert len({(k["style"], k["color"], k["size"]) for k in kids}) == len(kids)
assert len({k["sku"] for k in kids}) == len(kids)
plan_j = json.load(open(f"{ROOT}/store/data/market_plan.json")); bad = sum(1 for k in kids if not M.decode(plan_j, k["sku"]))
F = {"id": "pilot-tee-1", "prod": PK, "ptype": "SHIRT", "theme": "STYLE_NAME/COLOR_NAME/SIZE_NAME", "parent_sku": "AMZ-P-tee-d1",
     "title": "AlphaDog Styles Unisex T-Shirt for Adults - Dog Breed Line Art, Front Emblem and Full Body Back Print",
     "desc": "Wear your best friend. Minimalist continuous line art of your dog's breed on a soft unisex tee: a small emblem portrait on the front and the full body drawing across the back.\n\nHOW TO ORDER\n1. Style: pick your breed.\n2. Color: pick the shirt color.\n3. Size: pick your size.\n\nFABRIC AND FIT\nBella+Canvas 3001 unisex jersey tee, about 4.2 oz, 100% Airlume combed and ring-spun cotton (heather shades include some polyester). Soft, lightweight retail fit that runs true to size - size up for a relaxed fit.\n\nDETAILS\n- Printed in the USA, made to order just for you.\n- Finished with the AlphaDog Styles logo label.\n- Ships within 10 days of your order. Tracking included.\n\nCARE\nMachine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print.",
     "bullets": ["ORIGINAL DOG BREED ART: minimalist continuous line art - small emblem portrait on the front, full body drawing across the back",
                 "PICK YOUR BREED: 33 breeds in the Style menu, in 4 colors and sizes S to 2XL",
                 "SOFT UNISEX FIT: Bella+Canvas 3001, 100% Airlume combed and ring-spun cotton (heather shades include some polyester)",
                 "MADE TO ORDER IN THE USA: printed just for you, tracking included. Ships within 10 days of your order",
                 "PERFECT GIFT for dog moms, dog dads and every dog lover. Finished with the AlphaDog Styles logo label"],
     "fabric": "Airlume combed and ring-spun cotton (heathers include polyester)", "material": "Cotton", "noun": "T-Shirt", "heroes": [], "children": kids}
json.dump([F], open(f"{ROOT}/store/data/amazon_pilot.json", "w"), separators=(",", ":"))
print("children", len(kids), "breeds", len({k['breed'] for k in kids}), "colors", len({k['color'] for k in kids}), "skipped", skipped[:10], "decode failures", bad)
print("price range", min(k["price"] for k in kids), max(k["price"] for k in kids), "| images per child", sorted({1 + len(k["others"]) for k in kids}))

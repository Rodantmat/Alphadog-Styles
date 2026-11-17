"""Amazon listing feed for the NON-tee shirts (polo, tank, wtank) in the same structure as the tee listings:
ONE parent = product x design (art style + its placement); variation theme STYLE_NAME/COLOR_NAME/SIZE_NAME -> Style = Breed (all 33), Color, Size.
Only colours with REAL Printify mockups are listed. env: PK (polo|tank|wtank), LDC (design code). Writes store/data/amazon_listing_<pk><dc>.json."""
import json, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import market_plan as M
ROOT = M.ROOT
PK = os.environ["PK"]; DC = os.environ.get("LDC", "1")
assert PK in ("polo", "tank", "wtank", "hoodie", "cap"), PK
COLORS = {"polo": ["WH", "HE"], "tank": ["WH", "HE"], "wtank": ["WH", "HG", "TB", "MI", "LO"],
          "hoodie": ["WH", "GR", "SA", "LB", "PK", "AS"], "cap": ["DW", "DS", "DK", "DB", "DP", "FW", "FP", "FB", "MW"]}[PK]
STD = {"WH": "White", "HE": "Grey", "HG": "Grey", "TB": "Blue", "MI": "Green", "LO": "Orange"}
NAME = None
if PK == "hoodie":
    STD = {"WH": "White", "GR": "Grey", "SA": "Beige", "LB": "Blue", "PK": "Pink", "AS": "Grey"}
    NAME = {"WH": "White", "GR": "Sport Grey", "SA": "Sand", "LB": "Light Blue", "PK": "Light Pink", "AS": "Ash"}
if PK == "cap":
    STD = {"DW": "White", "DS": "Beige", "DK": "Beige", "DB": "Blue", "DP": "Pink", "FW": "White", "FP": "Pink", "FB": "Blue", "MW": "White"}
    NAME = {"DW": "Dad Hat White", "DS": "Dad Hat Stone", "DK": "Dad Hat Khaki", "DB": "Dad Hat Light Blue", "DP": "Dad Hat Pink",
            "FW": "Foam Trucker White", "FP": "Foam Trucker Pink Trim", "FB": "Foam Trucker Blue Trim", "MW": "Mesh Trucker White"}
NAME = NAME or {"WH": "White", "HE": "Athletic Heather", "HG": "Heather Grey", "TB": "Tahiti Blue", "MI": "Mint", "LO": "Light Orange"}
ART = {"line_classic": ("Line Art", "Minimalist continuous line art", "minimalist line art"),
       "geo_classic": ("Geometric Art", "Bold geometric faceted illustration", "geometric art"),
       "line_heart": ("Line Art Heart", "Minimalist continuous line art with a heart", "line art with a heart"),
       "geo_cool": ("Geometric Sunglasses", "Bold geometric faceted illustration with cool sunglasses", "geometric art with sunglasses"),
       "line_cool": ("Line Art Sunglasses", "Minimalist continuous line art with cool sunglasses", "line art with sunglasses"),
       "geo_heart": ("Geometric Heart", "Bold geometric faceted illustration with a heart", "geometric art with a heart")}
PROD = {"polo": dict(who="Unisex", noun="Polo Shirt", on="a breathable pique polo", fabric="cotton-blend pique", material="Cotton Blend",
                     fit="FABRIC AND FIT: JERZEES 443M pique polo, breathable cotton-blend pique, ribbed collar and three-button placket. Classic fit that runs true to size"),
        "tank": dict(who="Unisex", noun="Tank Top", on="a soft unisex jersey tank", fabric="Airlume combed and ring-spun cotton (heathers include polyester)", material="Cotton",
                     fit="FABRIC AND FIT: Bella+Canvas 3480 unisex jersey tank, about 4.2 oz, 100% Airlume combed and ring-spun cotton (heathers include polyester). Soft, light and breathable retail fit"),
        "hoodie": dict(who="Unisex", noun="Hoodie", on="a soft heavy-blend hoodie", fabric="50% cotton, 50% polyester", material="Cotton Blend",
                       fit="FABRIC AND FIT: Gildan 18500 heavy blend hoodie, about 8 oz, 50% cotton / 50% polyester, double-lined hood, pouch pocket and matching drawcord. Classic roomy fit - size down if you like it snug"),
        "cap": dict(who="Unisex", noun="Hat", on="a hat", fabric="cotton twill (foam/mesh trucker styles include polyester)", material="Cotton",
                    fit="HAT STYLES: Dad Hat (Yupoong 6245CM, soft unstructured cotton twill, low profile, adjustable strap), Foam Trucker (OTTO, retro foam front with mesh back, snapback) or Mesh Trucker (Yupoong 6006, 5-panel with mesh back, snapback). One size fits most"),
        "wtank": dict(who="Women's", noun="Racerback Tank", on="a soft women's racerback tank", fabric="cotton/polyester blend", material="Cotton Blend",
                      fit="FABRIC AND FIT: Next Level 1533 women's ideal racerback tank, about 3.9 oz cotton/polyester blend, slim racerback cut that sits close to the body - size up for a looser fit")}[PK]
plan = M.build(); PP = plan["products"][PK]; C = {c["code"]: c for c in PP["colors"]}; D = {d["code"]: d for d in PP["designs"]}[DC]
art, artd, pkw = ART[D["art"]]
if D["back"]:   place, pdesc = "Front Emblem and Full Body Back", "a small emblem portrait on the front and the full body drawing across the back"
elif D["front"] == "head_l": place, pdesc = "Large Front Portrait", "a large portrait printed across the front"
else:           place, pdesc = "Chest Emblem", "a small emblem portrait on the chest"
if PK == "cap": place, pdesc = "Front Emblem", "a portrait printed on the front of the hat"
GAL = json.load(open(f"{ROOT}/store/data/amazon_gallery_{PK}_d{DC}.json"))
head = f"AlphaDog Styles {PROD['who']} {PROD['noun']}" + (" for Adults" if PROD["who"] == "Unisex" else "")
kids = []; skipped = []
for b in M.BR:
    for cc in COLORS:
        e = GAL.get(f"{b}|{cc}") or {}
        if e.get("main") != "ok": skipped.append((b, cc, "no main")); continue
        base = f"amz/{PK}/{b}/{DC}{cc}"
        extra = [base + "_g%d.jpg" % (i + 1) for i, t in enumerate(e.get("g", [])) if t == "ok"][:8]      # real Printify photos only
        for s in PP["sizes"]:
            kids.append({"sku": M.sku(PK, b, DC, cc, s), "style": M.BR[b], "breed": b, "color": NAME[cc], "color_std": STD[cc], "cc": cc, "size": s,
                         "price": M.price(C[cc]["prod"], s), "img": base + ".jpg", "others": extra,
                         "title": f"{head} - {M.BR[b]} {art}, {place}, {NAME[cc]}"[:200]})
assert len({(k["style"], k["color"], k["size"]) for k in kids}) == len(kids)
assert len({k["sku"] for k in kids}) == len(kids)
plan_j = json.load(open(f"{ROOT}/store/data/market_plan.json")); bad = sum(1 for k in kids if not M.decode(plan_j, k["sku"]))
F = {"id": f"listing-{PK}-{DC}", "prod": PK, "ptype": {"hoodie": "SWEATSHIRT", "cap": "HAT"}.get(PK, "SHIRT"), "theme": os.environ.get("AMZ_THEME") or ("STYLE_NAME/COLOR_NAME" if PK == "cap" else "STYLE_NAME/COLOR_NAME/SIZE_NAME"), "parent_sku": f"AMZ-P-{PK}-d{DC}",
     "title": f"{head} - Dog Breed {art}, {place} Print" if PK != "cap" else f"{head} - Dog Breed {art}, Dad Hat and Trucker Cap",
     "desc": f"Wear your best friend. {artd} of your dog's breed on {PROD['on']}: {pdesc}.\n\nHOW TO ORDER\n1. Style: pick your breed.\n2. Color: pick the color.\n3. Size: pick your size.\n\n"
             f"{PROD['fit']}.\n\nDETAILS\n- Printed in the USA, made to order just for you.\n- Finished with the AlphaDog Styles logo label.\n- Production 2-5 business days, then 3-7 business days in transit within the US. Tracking included.\n\n"
             "CARE\nMachine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print.",
     "bullets": [f"ORIGINAL DOG ART: {pkw} of your dog's breed by AlphaDog Styles - pick your breed in the Style menu",
                 f"DESIGN: {art} with {pdesc}",
                 PROD["fit"],
                 "MADE TO ORDER IN THE USA: printed just for you, tracking included. Production 2-5 business days, then 3-7 business days in transit",
                 "PERFECT GIFT for dog moms, dog dads and every dog lover. Finished with the AlphaDog Styles logo label"],
     "fabric": PROD["fabric"], "material": PROD["material"], "noun": PROD["noun"] if PK != "wtank" else "Women's Racerback Tank", "heroes": [], "children": kids}
if PK == "cap":
    F["desc"] = F["desc"].replace("2. Color: pick the color.\n3. Size: pick your size.", "2. Color: pick the hat style and color.\n3. Add to cart.").replace("Finished with the AlphaDog Styles logo label", "Durable print made to last").replace("Machine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print.", "Spot clean with a damp cloth. Do not machine wash or tumble dry.")
    F["bullets"][4] = "PERFECT GIFT for dog moms, dog dads and every dog lover. Durable print made to last"
    for k in kids: k["title"] = k["title"].replace(", Front Emblem, ", ", ")
json.dump([F], open(f"{ROOT}/store/data/amazon_listing_{PK}{DC}.json", "w"), separators=(",", ":"))
print(F["id"], "| parent", F["parent_sku"], "|", F["title"])
print("children", len(kids), "breeds", len({k['breed'] for k in kids}), "colors", len({k['color'] for k in kids}), "skipped", skipped[:10], "decode failures", bad)
print("price range", min(k["price"] for k in kids), max(k["price"] for k in kids), "| images per child", sorted({1 + len(k["others"]) for k in kids}))
print("sample child:", kids[0]["sku"], "|", kids[0]["title"])

"""Shared listing text for the consolidated marketplace listings (Etsy / eBay / TikTok). No off-site links (all three forbid them)."""
import json,os
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plan=json.load(open(f"{ROOT}/store/data/market_plan.json")); cat=json.load(open(f"{ROOT}/store/data/catalog.json"))
BR={b["slug"]:b["name"] for b in cat["breeds"]}
FABRIC={"tee":"Bella+Canvas 3001 unisex jersey tee, about 4.2 oz, 100% Airlume combed and ring-spun cotton (heather shades include some polyester). Soft, lightweight retail fit that runs true to size - size up for a relaxed fit.",
 "hoodie":"Gildan 18500 heavy blend hoodie, about 8 oz, 50% cotton / 50% polyester, double-lined hood, pouch pocket and matching drawcord. Classic roomy fit - size down if you like it snug.",
 "tank":"Bella+Canvas 3480 unisex jersey tank, about 4.2 oz, 100% Airlume combed and ring-spun cotton (heathers include polyester). Soft, light and breathable retail fit.",
 "wtank":"Next Level 1533 women's ideal racerback tank, about 3.9 oz cotton/polyester blend, slim racerback cut that sits close to the body - size up for a looser fit.",
 "polo":"JERZEES 443M piqué polo, breathable cotton-blend piqué, ribbed collar and three-button placket. The dog is printed on the chest.",
 "cap":"Choose your hat: Dad Hat (Yupoong 6245CM, soft unstructured cotton twill, low profile, adjustable strap), Foam Trucker (OTTO, retro foam front with mesh back, snapback) or Mesh Trucker (Yupoong 6006, 5-panel with mesh back, snapback). One size fits most."}
DESIGN_HELP={"Line Art · Emblem + Back":"small continuous-line head on the chest + full-body line art across the back",
 "Geometric Sunglasses · Big Front":"large geometric portrait with aviator sunglasses on the front",
 "Line Art Heart · Emblem + Back":"line-art head framed in a heart on the chest + full-body line art on the back",
 "Geometric · Emblem + Back":"small geometric head on the chest + full-body geometric art on the back",
 "Line Art Sunglasses · Big Front":"large continuous-line portrait with sunglasses on the front",
 "Geometric Heart · Big Front":"large geometric portrait framed in a heart on the front"}
def names(br): return ", ".join(BR[b] for b in br[:-1])+(" or " if len(br)>1 else "")+BR[br[-1]]
def description(L):
    P=plan["products"][L["prod"]]; D={d["code"]:d for d in P["designs"]}; C={c["code"]:c for c in P["colors"]}
    pk=L["prod"]; noun={"tee":"tee","hoodie":"hoodie","wtank":"racerback tank","tank":"tank top","polo":"polo","cap":"hat"}[pk]
    lines=[f"Wear your best friend. Minimalist {names(L['breeds'])} art on a soft {noun} - the gift every dog mom and dog dad actually wears.","",
           "HOW TO ORDER"]
    if pk=="cap": lines+=["1. Style: pick your breed and design.","2. Hat: pick the hat style and color.","3. Add to cart."]
    else: lines+=["1. Style: pick your breed and design.","2. Color: pick the shirt color.","3. Size: pick your size (see the fit notes below)."]
    lines+=["","DESIGNS"]
    for dc in L["designs"]:
        d=D[dc]; lines.append(f"- {d['name']}: {DESIGN_HELP.get(d['name'],d['name'].lower())}")
    lines+=["",("HATS AND COLORS: " if pk=="cap" else "COLORS: ")+", ".join(C[c]["name"] for c in L["colors"])]
    if pk!="cap": lines.append("SIZES: "+", ".join(L["sizes"]))
    lines+=["","FABRIC AND FIT",FABRIC[pk],"","DETAILS",
            "- Printed in the USA, made to order just for you.",
            "- Finished with the AlphaDog Styles logo label." if pk not in("cap",) else "- Durable print made to last.",
            "- Production 2-5 business days, then 3-7 business days in transit within the US. Tracking included.","",
            "CARE","Machine wash cold, inside out, with similar colors. Tumble dry low. Do not iron or dry clean the print." if pk!="cap" else "Spot clean with a damp cloth. Do not machine wash or tumble dry.","",
            "Don't see your dog's breed, or want one that looks exactly like your dog? Send us a message - we create custom designs from your photos."]
    return "\n".join(lines)
def style_value(b,d,short=False):
    """variation value for the Style (breed + design) option"""
    from market_plan import short as sname
    return f"{sname(b) if short else BR[b]} · {d['short'] if short else d['name']}"

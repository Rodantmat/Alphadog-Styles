"""Turn the shop's existing Etsy listings into the consolidated listings of store/data/market_plan.json (plat=etsy).
Editing keeps each listing's fee, reviews, favorites and shipping/processing setup. Steps per listing:
title/description/tags/taxonomy -> inventory (Style x Color x Size, our SKUs) -> new photos (old ones removed) -> photos linked to Style values.
ARG: "dry" (plan only) | "one" (first listing only) | "all" | a plan listing id. State in out/market_etsy_state.json (resumable)."""
import os,json,re,time
import etsy_api as E, market_text as T
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
plan=T.plan; imgs=json.load(open(f"{ROOT}/store/data/market_images.json"))
STATE=f"{ROOT}/out/market_etsy_state.json"; st=json.load(open(STATE)) if os.path.exists(STATE) else {"map":{},"done":{}}
TAX_WORDS={"tee":["t-shirts"],"hoodie":["hoodies","sweatshirts"],"wtank":["tank tops"],"tank":["tank tops"],"polo":["polo"],"cap":["baseball","trucker","hats"]}
def save(): os.makedirs(os.path.dirname(STATE),exist_ok=True); json.dump(st,open(STATE,"w"),indent=1)
TAXPATH={"tee":["Gender-Neutral Adult Clothing > Tops & Tees > T-shirts"],"hoodie":["Gender-Neutral Adult Clothing > Hoodies & Sweatshirts > Hoodies"],
 "tank":["Gender-Neutral Adult Clothing > Tops & Tees > Tanks"],"wtank":["Women's Clothing > Tops & Tees > Tank","Women's Clothing > Tops & Tees > Tanks"],
 "polo":["Gender-Neutral Adult Clothing > Tops & Tees > Polos"],"cap":["Hats & Caps > Baseball","Hats & Caps > Trucker","Hats & Head Coverings > Hats & Caps"]}
def taxonomy(pk):
    pr=json.load(open(f"{ROOT}/out/market_etsy_probe.json"))["taxonomy"]
    for want in TAXPATH[pk]:
        hit=[(i,s) for i,s in pr if want in s]
        if hit: return sorted(hit,key=lambda x:len(x[1]))[0][0] if not want.endswith("Hats & Caps") else hit[0][0]
    return None
def kind_of(title):
    t=title.lower()
    if "hoodie" in t or "sweatshirt" in t: return "hoodie"
    if "tank" in t: return "tank"
    if "hat" in t or "cap" in t: return "cap"
    return "tee"
def assign(existing):
    """plan listing id -> existing listing id. Same product + same first breed first, then same product, then anything."""
    if st["map"]: return st["map"]
    P=[l for l in plan["listings"] if l["plat"]=="etsy"]; free={x["listing_id"]:x for x in existing}; m={}
    def breed_in(title,b): return T.BR[b].lower() in title.lower()
    for rule in (lambda l,x: kind_of(x["title"])==l["prod"] and breed_in(x["title"],l["breeds"][0]),
                 lambda l,x: kind_of(x["title"])==l["prod"] and any(breed_in(x["title"],b) for b in l["breeds"]),
                 lambda l,x: kind_of(x["title"])==l["prod"],
                 lambda l,x: any(breed_in(x["title"],b) for b in l["breeds"]),
                 lambda l,x: True):
        for l in P:
            if l["id"] in m: continue
            hit=next((i for i,x in free.items() if rule(l,x)),None)
            if hit: m[l["id"]]=hit; free.pop(hit)
    st["map"]=m; save(); return m
def style_val(b,d):
    v=f"{T.BR[b]} - {d['name']}"
    if len(v)>45: v=f"{T.BR[b]} - {d['short']}"
    if len(v)>45:
        from market_plan import short
        v=f"{short(b)} - {d['short']}"
    return v[:45]
def inventory(L,readiness):
    P=plan["products"][L["prod"]]; D={d["code"]:d for d in P["designs"]}; C={c["code"]:c for c in P["colors"]}
    from market_plan import sku,price
    prods=[]; cap=L["prod"]=="cap"
    for b in L["breeds"]:
        for dc in L["designs"]:
            for cc in L["colors"]:
                for s in L["sizes"]:
                    pv=[{"property_id":513,"property_name":"Style","values":[style_val(b,D[dc])],"value_ids":[]},
                        {"property_id":514,"property_name":"Hat" if cap else "Color","values":[C[cc]["name"]],"value_ids":[]}]
                    if not cap: pv.append({"property_id":516,"property_name":"Size","values":[s],"value_ids":[]})
                    pr=price(C[cc]["prod"],s)
                    off={"price":pr,"quantity":999,"is_enabled":True}
                    if readiness: off["readiness_state_id"]=readiness
                    prods.append({"sku":sku(L["prod"],b,dc,cc,s),"property_values":pv,"offerings":[off]})
    allp=[513,514] if cap else [513,514,516]
    return {"products":prods,"price_on_property":([513,514] if cap else [513,514,516]),"quantity_on_property":[],"sku_on_property":allp,
            "readiness_state_on_property":[]},(2 if cap else 3)
def sync_one(L,lid,full):
    sid=E.shop_id(); log={}
    # 1) listing text + category
    upd={"title":L["title"],"description":T.description(L),"tags":",".join(L["tags"]),"should_auto_renew":"true",
         "shipping_profile_id":319337860724 if L["prod"]=="hoodie" else 318773465927}
    if kind_of(full["title"])!=L["prod"] or L["prod"] in("wtank","polo"):
        tx=taxonomy(L["prod"])
        if tx: upd["taxonomy_id"]=tx
    r=E.call("PATCH",f"/shops/{sid}/listings/{lid}",form=upd); log["update"]=r.get("_err") or "ok"
    if r.get("_err"): log["update_msg"]=r["msg"]; return log
    # 2) inventory
    cur=E.call("GET",f"/listings/{lid}/inventory"); rd=None
    try: rd=cur["products"][0]["offerings"][0].get("readiness_state_id")
    except Exception: pass
    body,nv=inventory(L,rd)
    r=E.call("PUT",f"/listings/{lid}/inventory",body=body,q={"max_variations_supported":nv}) if nv==3 else E.call("PUT",f"/listings/{lid}/inventory",body=body)
    log["inventory"]=r.get("_err") or len(r.get("products",[]))
    if r.get("_err"): log["inventory_msg"]=r["msg"]; return log
    inv=r
    # 3) photos: upload new (max 10), then remove the old Printify mockups
    m=imgs[L["id"]]; files=(m["hero"][:8]+[m["lineup"]])[:10]
    old=E.call("GET",f"/listings/{lid}/images").get("results",[])
    new_ids={}
    for rank,f in enumerate(files,1):
        data=open(f"{ROOT}/store/mk/{f}","rb").read()
        r=E.call("POST",f"/shops/{sid}/listings/{lid}/images",form={"rank":rank,"overwrite":"true"},files={"image":(os.path.basename(f),data,"image/jpeg")})
        if r.get("listing_image_id"): new_ids[f]=r["listing_image_id"]
        else: log.setdefault("img_err",[]).append(str(r)[:200])
    if len(new_ids)>=3:
        for o in old:
            if o["listing_image_id"] not in new_ids.values(): E.call("DELETE",f"/shops/{sid}/listings/{lid}/images/{o['listing_image_id']}")
    log["images"]=len(new_ids)
    # 4) link photos to Style values where we have that exact breed+design photo
    P=plan["products"][L["prod"]]; D={d["code"]:d for d in P["designs"]}
    vid={}
    for p in inv.get("products",[]):
        for pv in p["property_values"]:
            if pv["property_id"]==513 and pv.get("value_ids"): vid[pv["values"][0]]=pv["value_ids"][0]
    vi=[]
    for key,f in m["bd"].items():
        b,dc=key.split("|"); v=style_val(b,D[dc])
        if f in new_ids and v in vid: vi.append({"property_id":513,"value_id":vid[v],"image_id":new_ids[f]})
    if vi:
        r=E.call("POST",f"/shops/{sid}/listings/{lid}/variation-images",body={"variation_images":vi}); log["var_images"]=r.get("_err") or len(vi)
        if r.get("_err"): log["var_images_msg"]=r["msg"][:300]
    return log
def main(arg="dry"):
    ex=E.listings("active"); print("active Etsy listings:",len(ex))
    m=assign(ex); P={l["id"]:l for l in plan["listings"] if l["plat"]=="etsy"}
    byid={x["listing_id"]:x for x in ex}
    print("assigned",len(m),"of",len(P))
    for pid,lid in m.items(): print(f"  {pid:16} -> {lid} | {byid.get(lid,{}).get('title','?')[:70]}")
    if arg=="dry": return
    todo=[p for p in m if p not in st["done"]]
    if arg=="one": todo=todo[:1]
    elif arg not in("all",): todo=[arg] if arg in m else []
    for pid in todo:
        lid=m[pid]; full=byid.get(lid) or E.call("GET",f"/listings/{lid}")
        t0=time.time(); log=sync_one(P[pid],lid,full); print(pid,lid,json.dumps(log),f"{time.time()-t0:.0f}s",flush=True)
        if log.get("update")=="ok" and isinstance(log.get("inventory"),int) and log.get("images",0)>=3: st["done"][pid]={"listing":lid,"t":int(time.time()),**log}
        else: st.setdefault("failed",{})[pid]=log
        save()
    print("DONE",len(st["done"]),"of",len(m))

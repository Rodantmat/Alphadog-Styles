"""Read-only look at the Etsy shop before converting listings: listings, one inventory, images, taxonomy ids, readiness states, shipping profiles."""
import json,os
import etsy_api as E
out={}
sid=E.shop_id(); out["shop_id"]=sid
L=E.listings("active"); out["n_active"]=len(L)
out["listings"]=[{k:l.get(k) for k in("listing_id","title","taxonomy_id","shipping_profile_id","return_policy_id","production_partner_ids","processing_min","processing_max","readiness_state_id","has_variations","state","num_favorers","views","tags","who_made","when_made","is_supply","shop_section_id","price","skus","listing_type")} for l in L]
if L:
    lid=L[0]["listing_id"]
    inv=E.call("GET",f"/listings/{lid}/inventory"); out["inv_sample_keys"]=list(inv.keys()) if isinstance(inv,dict) else inv
    if inv.get("products"): out["inv_sample_product"]=inv["products"][0]; out["inv_n"]=len(inv["products"]); out["inv_on"]={k:inv.get(k) for k in("price_on_property","quantity_on_property","sku_on_property","readiness_state_on_property")}
    out["images_sample"]=E.call("GET",f"/listings/{lid}/images")
    full=E.call("GET",f"/listings/{lid}"); out["listing_full_sample"]={k:v for k,v in full.items() if k!="description"}; out["desc_sample"]=full.get("description","")[:3000]
out["shipping_profiles"]=E.call("GET",f"/shops/{sid}/shipping-profiles")
out["readiness"]=E.call("GET",f"/shops/{sid}/readiness-state-definitions")
out["sections"]=E.call("GET",f"/shops/{sid}/sections")
tax=E.call("GET","/seller-taxonomy/nodes")
def walk(n,path,acc):
    p=path+[n["name"]]; s=" > ".join(p)
    if any(w in s.lower() for w in ("t-shirt","hoodie","sweatshirt","tank","polo","hat","cap")) and ("clothing" in s.lower() or "accessories" in s.lower()): acc.append((n["id"],s))
    for c in n.get("children",[]): walk(c,p,acc)
acc=[]
for n in tax.get("results",[]): walk(n,[],acc)
out["taxonomy"]=acc
os.makedirs("out",exist_ok=True); json.dump(out,open("out/market_etsy_probe.json","w"),indent=1)
print("active",len(L),"shop",sid); print(json.dumps(out.get("inv_on")),out.get("inv_n")); print("\n".join(f"{i} {s}" for i,s in acc[:60]))

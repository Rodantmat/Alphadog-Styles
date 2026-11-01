"""Research: tank tops (unisex + women's), caps, polos on Printify - providers, colors, sizes, print areas, US shipping."""
import os,json,urllib.request,time
T=os.environ["PRINTIFY_TOKEN"]
def g(p):
    for a in range(5):
        try:
            r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}); return json.load(urllib.request.urlopen(r,timeout=60))
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(20); continue
            raise
bps=g("/v1/catalog/blueprints.json")
pp={p["id"]:p for p in g("/v1/catalog/print_providers.json")}
def kind(t):
    t=t.lower()
    if any(x in t for x in ["kid","youth","toddler","baby","dog","pet"]): return None
    if "polo" in t: return "polo"
    if "tank" in t: return "tank"
    if any(x in t for x in ["cap","hat","trucker","snapback","beanie"]) and "beanie" not in t and "bucket" not in t: return "cap"
    return None
out={"cands":[]}
for b in bps:
    k=kind(b["title"])
    if not k: continue
    d={"id":b["id"],"kind":k,"title":b["title"],"brand":b.get("brand"),"model":b.get("model"),"providers":[]}
    try: provs=g(f"/v1/catalog/blueprints/{b['id']}/print_providers.json")
    except Exception as e: d["err"]=str(e); out["cands"].append(d); continue
    for p in provs:
        loc=(pp.get(p["id"],{}).get("location") or {})
        if loc.get("country") not in ("US",None): continue
        e={"id":p["id"],"title":p["title"],"loc":loc.get("region")}
        try:
            vs=g(f"/v1/catalog/blueprints/{b['id']}/print_providers/{p['id']}/variants.json")["variants"]
            e["n"]=len(vs); e["colors"]=sorted({v["options"].get("color","") for v in vs}); e["sizes"]=sorted({v["options"].get("size","") for v in vs})
            e["areas"]={ph["position"]:[ph.get("width"),ph.get("height")] for ph in (vs[0].get("placeholders") or [])}
            e["v0"]={k2:v2 for k2,v2 in vs[0].items() if k2 not in("placeholders",)}
        except Exception as ex: e["verr"]=str(ex)[:100]
        try:
            sh=g(f"/v1/catalog/blueprints/{b['id']}/print_providers/{p['id']}/shipping.json")
            us=[pr for pr in sh["profiles"] if "US" in pr["countries"]]
            e["ship_us"]=[(pr["first_item"]["cost"],pr["additional_items"]["cost"]) for pr in us][:2]
        except Exception as ex: e["sherr"]=str(ex)[:80]
        d["providers"].append(e)
    out["cands"].append(d)
json.dump(out,open("out/expand.json","w"),indent=1); print("cands",len(out["cands"]))

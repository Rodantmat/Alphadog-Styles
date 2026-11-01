# Read-only: which Printify print providers produce in Brazil, what they make,
# and what shipping to Brazil costs from the providers our live products use.
import os,json,urllib.request
T=os.environ["PRINTIFY_TOKEN"]
def g(p):
    r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"})
    return json.load(urllib.request.urlopen(r))
out={}
provs=g("/v1/catalog/print_providers.json")
out["provider_countries"]=sorted({(p.get("location") or {}).get("country","?") for p in provs})
br=[p for p in provs if (p.get("location") or {}).get("country") in ("BR","Brazil")]
out["brazil_providers"]=[]
for p in br:
    d=g(f"/v1/catalog/print_providers/{p['id']}.json")
    out["brazil_providers"].append({"id":p["id"],"title":p["title"],"location":p.get("location"),
        "blueprints":[{"id":b["id"],"title":b["title"],"brand":b.get("brand"),"model":b.get("model")} for b in d.get("blueprints",[])]})
# providers used by our live products, and their shipping to BR
used=set()
for shop in (29544854,29545924):
    try:
        ps=g(f"/v1/shops/{shop}/products.json?limit=50")["data"]
        for p in ps: used.add((p["blueprint_id"],p["print_provider_id"]))
    except Exception as e: out[f"shop_{shop}_err"]=str(e)
out["used"]=sorted(used)
out["ship_to_BR"]={}
for bp,pp in sorted(used):
    try:
        s=g(f"/v1/catalog/blueprints/{bp}/print_providers/{pp}/shipping.json")
        rows=[]
        for prof in s.get("profiles",[]):
            if any(c in ("BR","REST_OF_THE_WORLD") for c in prof.get("countries",[])):
                rows.append({"countries":[c for c in prof["countries"] if c in("BR","REST_OF_THE_WORLD")],
                             "first":prof["first_item"],"additional":prof["additional_items"]})
        out["ship_to_BR"][f"{bp}/{pp}"]={"handling":s.get("handling_time"),"rows":rows[:3]}
    except Exception as e: out["ship_to_BR"][f"{bp}/{pp}"]=str(e)
json.dump(out,open("out/printify_brazil.json","w"),indent=1)
print(json.dumps({"countries":out["provider_countries"],"br":[(p["id"],p["title"],len(p["blueprints"])) for p in out["brazil_providers"]]}))

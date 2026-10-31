import os,json,urllib.request
T=os.environ["PRINTIFY_TOKEN"]
def g(p):
    r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}); return json.load(urllib.request.urlopen(r))
out={}
# shipping for current blueprints
for bp in (145,77):
    try: out[f"ship_{bp}_99"]=g(f"/v1/catalog/blueprints/{bp}/print_providers/99/shipping.json")
    except Exception as e: out[f"ship_{bp}_99"]=str(e)
bps=g("/v1/catalog/blueprints.json")
keys=["bella","comfort colors","next level","gildan","independent","cotton heritage","lane seven","champion","sol","hoodie","sweatshirt"]
cand=[b for b in bps if any(k in b["title"].lower() for k in ["bella+canvas","bella + canvas","comfort colors","next level","independent trading","cotton heritage","lane seven"]) and any(w in b["title"].lower() for w in ["tee","t-shirt","hoodie","sweatshirt","fleece"])]
out["candidates"]=[]
for b in cand[:40]:
    try:
        pps=g(f"/v1/catalog/blueprints/{b['id']}/print_providers.json")
        d={"id":b["id"],"title":b["title"],"providers":[]}
        for p in pps[:6]:
            e={"id":p["id"],"title":p["title"]}
            try:
                vs=g(f"/v1/catalog/blueprints/{b['id']}/print_providers/{p['id']}/variants.json")["variants"]
                e["nvar"]=len(vs)
            except Exception as ex: e["err"]=str(ex)
            try:
                sh=g(f"/v1/catalog/blueprints/{b['id']}/print_providers/{p['id']}/shipping.json")
                e["ship"]={"profiles":[ {"v":len(pr["variant_ids"]),"first":pr["first_item"],"add":pr["additional_items"],"countries":[c for c in pr["countries"] if c in("US","BR","CO","REST_OF_THE_WORLD")]} for pr in sh["profiles"][:6]]}
            except Exception as ex: e["sherr"]=str(ex)
            d["providers"].append(e)
        out["candidates"].append(d)
    except Exception as ex: out["candidates"].append({"id":b["id"],"err":str(ex)})
json.dump(out,open("out/catalog.json","w"),indent=1)
print("ok")

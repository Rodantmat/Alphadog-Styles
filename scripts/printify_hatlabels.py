import os,json,urllib.request,time,re
T=os.environ["PRINTIFY_TOKEN"].strip()
def g(p):
    for a in range(4):
        try:
            r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"alphadog"})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception as e:
            time.sleep(5*(a+1))
    return None
bps=g("/v1/catalog/blueprints.json")
hats=[b for b in bps if re.search(r"\b(hat|cap|snapback|trucker|beanie|bucket)\b",b["title"],re.I)]
print("hat blueprints:",len(hats))
out=[]
for b in hats:
    pps=g(f"/v1/catalog/blueprints/{b['id']}/print_providers.json") or []
    for p in pps:
        vs=(g(f"/v1/catalog/blueprints/{b['id']}/print_providers/{p['id']}/variants.json") or {}).get("variants",[])
        pos=sorted({ph["position"] for v in vs for ph in v.get("placeholders",[])})
        out.append((b["id"],b["title"],b.get("brand"),b.get("model"),p["id"],p["title"],pos))
        time.sleep(0.2)
allpos=sorted({x for o in out for x in o[6]})
print("ALL POSITIONS:",allpos)
for o in out:
    if any(not re.fullmatch(r"front(_dtf)?|front_embroidery|back|left|right|(back|left|right|front)_hat_embroidery|front_print|back_print",x) for x in o[6]):
        print("NOTABLE",o)
json.dump(out,open("out/hat_positions.json","w"),indent=0)

import os, json, re, urllib.request, time
T=os.environ["PRINTIFY_TOKEN"]
def get(p):
    for _ in range(3):
        try:
            r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"alphadog"})
            return json.load(urllib.request.urlopen(r,timeout=60))
        except Exception as e:
            err=str(e); time.sleep(2)
    return {"error":err}
bps=get("/v1/catalog/blueprints.json")
print("total blueprints",len(bps))
pat=re.compile(r"Heavy Cotton Tee|Jersey Tank|Tank|Hooded Sweatshirt|Hoodie|Dad Hat|Baseball Cap|Trucker|Softstyle|Premium Hat|Snapback",re.I)
sel=[b for b in bps if pat.search(b["title"])]
print("matches",len(sel))
for b in sel: print(b["id"],"|",b["brand"],"|",b["title"])
want=[b for b in sel if re.search(r"Heavy Cotton Tee$|Unisex Heavy Cotton Tee|Unisex Jersey Tank|Unisex Heavy Blend.*Hooded Sweatshirt|Classic Dad Hat|Dad Hat|Trucker",b["title"],re.I)][:10]
print("\n=== DETAIL ===")
for b in want:
    print("\n##",b["id"],b["brand"],b["title"])
    prov=get(f"/v1/catalog/blueprints/{b['id']}/print_providers.json")
    if isinstance(prov,dict): print(prov); continue
    for p in prov[:8]:
        v=get(f"/v1/catalog/blueprints/{b['id']}/print_providers/{p['id']}/variants.json")
        if "error" in v: print(" prov",p["id"],p["title"],v); continue
        vs=v["variants"]
        cols=sorted({x["options"].get("color") for x in vs if x.get("options")})
        sizes=[]
        for x in vs:
            s=x["options"].get("size")
            if s and s not in sizes: sizes.append(s)
        ph={}
        for x in vs:
            for q in x.get("placeholders",[]): ph[q["position"]]=(q["width"],q["height"])
        loc=p.get("location",{})
        print(" prov",p["id"],p["title"],"|",loc.get("country") if isinstance(loc,dict) else loc,"| variants",len(vs),"| colors",len(cols),"| sizes",sizes,"| placeholders",ph)
        if p is prov[0]: print("   colors:",cols)
        time.sleep(0.7)

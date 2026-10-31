import os, json, urllib.request, sys
T=os.environ["PRINTIFY_TOKEN"]
def get(p):
    r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"alphadog"})
    return json.load(urllib.request.urlopen(r,timeout=60))
out={}
for bp,prov in [(145,99),(77,99)]:
    b=get(f"/v1/catalog/blueprints/{bp}.json")
    v=get(f"/v1/catalog/blueprints/{bp}/print_providers/{prov}/variants.json")
    vs=v["variants"]
    out[str(bp)]={"title":b["title"],"brand":b["brand"],"model":b["model"],"description":b["description"][:300],
      "variants":[{"id":x["id"],"title":x["title"],"options":x["options"],"placeholders":x["placeholders"],"is_available":x.get("is_available")} for x in vs]}
    cols=sorted({x["options"]["color"] for x in vs}); sizes=[]
    for x in vs:
        if x["options"]["size"] not in sizes: sizes.append(x["options"]["size"])
    print(bp,b["title"],"| variants",len(vs),"| colors",len(cols),"| sizes",sizes)
    print(" colors:",cols)
    print(" placeholders:",vs[0]["placeholders"])
    try:
        sh=get(f"/v1/catalog/blueprints/{bp}/print_providers/{prov}/shipping.json")
        print(" shipping:",json.dumps(sh)[:600])
    except Exception as e: print(" shipping err",e)
os.makedirs("out",exist_ok=True)
json.dump(out,open("out/printify_variants.json","w"))

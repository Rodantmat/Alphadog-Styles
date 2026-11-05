import os,json,urllib.request,time
T=os.environ["PRINTIFY_TOKEN"]
def g(p):
    for a in range(6):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=90))
        except Exception as e: time.sleep(10*(a+1))
out={}
for name,bp in {"tee":12,"hoodie":77,"tank":39,"wtank":18,"polo":1402,"cap_dad":1447,"cap_foam":1735,"cap_mesh":1734}.items():
    vs=g(f"/v1/catalog/blueprints/{bp}/print_providers/99/variants.json")["variants"]
    cols={}
    for v in vs: cols.setdefault(v["options"].get("color"),[]).append(v["options"].get("size"))
    out[name]={c:sorted(set(s)) for c,s in cols.items()}
    print(name,len(cols),list(cols))
json.dump(out,open("out/colors_all.json","w"),indent=1)

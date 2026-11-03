import os,json,urllib.request
T=os.environ["PRINTIFY_TOKEN"].strip()
def g(p):
    r=urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"alphadog"})
    return json.load(urllib.request.urlopen(r,timeout=60))
for bp,name in [(1447,"dad hat"),(1735,"foam trucker"),(1734,"mesh trucker")]:
    pps=g(f"/v1/catalog/blueprints/{bp}/print_providers.json")
    print("==",bp,name,"providers:",[(p["id"],p["title"]) for p in pps])
    for p in pps:
        vs=g(f"/v1/catalog/blueprints/{bp}/print_providers/{p['id']}/variants.json")["variants"]
        pos=sorted({ph["position"]+f"({ph.get('width')}x{ph.get('height')})" for v in vs for ph in v.get("placeholders",[])})
        print("  pp",p["id"],p["title"],"positions:",pos)

import json,urllib.request,re
def g(u):
    try: return json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"alphadog"}),timeout=60))
    except Exception as e: print("ERR",u,e); return None
r=g("https://api.printful.com/products")
items=(r or {}).get("result",[])
print("printful products:",len(items))
hats=[p for p in items if re.search(r"hat|cap|beanie|snapback|trucker",(p.get("type_name","")+" "+p.get("title","")),re.I)]
print("hats:",len(hats))
allp=set()
for p in hats:
    d=g(f"https://api.printful.com/products/{p['id']}")
    if not d: continue
    files=[f.get("id") or f.get("type") for f in d["result"]["product"].get("files",[])]
    opts=[o.get("id") for o in d["result"]["product"].get("options",[])]
    allp.update(files)
    if any(re.search(r"label|inside|inner",str(x),re.I) for x in files+opts):
        print("LABEL?",p["id"],p.get("title"),files,opts)
print("ALL hat file types:",sorted(allp))

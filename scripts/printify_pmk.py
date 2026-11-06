import os,json,urllib.request,hashlib,time,re
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
def get(u):
    for t in range(3):
        time.sleep(1.2)
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
        except Exception as e: time.sleep(5)
info=json.load(open("out/prodinfo.json")); SH=[x["id"] for x in call("/v1/shops.json")]
for key,v in info.items():
    if "|hoodie|" not in key or "line_classic" not in key: continue
    breed=key.split("|")[0]; pid=v["id"]; p=None
    for sh in SH:
        try: p=call(f"/v1/shops/{sh}/products/{pid}.json"); break
        except Exception: pass
    if not p: continue
    base=sorted({int(re.search(r"/mockup/[^/]+/\d+/(\d+)/",i["src"]).group(1)) for i in p["images"] if "/mockup/" in i["src"]})
    cand=sorted({j for b in base for j in range(b-4,b+12)})
    good=None
    for col,var in v["cols"].items():
        d=f"out/pmk/{breed}/hoodie/{col.replace(' ','_')}"; os.makedirs(d,exist_ok=True); seen=set()
        for i in (good or cand):
            b=get(f"https://images.printify.com/mockup/{pid}/{var}/{i}/x.jpg?camera_label=front")
            if not b: continue
            h=hashlib.md5(b).hexdigest()
            if h in seen: continue
            seen.add(h); open(f"{d}/{i}.jpg","wb").write(b)
        if good is None: good=sorted(int(f[:-4]) for f in os.listdir(d))
    print("done",breed,good,flush=True)

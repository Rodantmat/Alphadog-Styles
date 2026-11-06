import os,json,urllib.request,hashlib,time,re
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
def get(u):
    for t in range(3):
        time.sleep(1.2)
        try: return urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
        except Exception: time.sleep(5)
st=json.load(open("out/state_dark_tiktok.json")); sh=[x["id"] for x in call("/v1/shops.json")]
COL=["Navy","Red","Maroon","Forest","Asphalt","Dark Grey Heather","Black"]
for n,(key,v) in enumerate(st.items()):
    breed=key.split("|")[0]; pid=v["id"]; p=None
    for s in sh:
        try: p=call(f"/v1/shops/{s}/products/{pid}.json"); break
        except Exception: pass
    if not p: print("noprod",key); continue
    base=sorted({int(re.search(r"/mockup/[^/]+/\d+/(\d+)/",i["src"]).group(1)) for i in p["images"] if "/mockup/" in i["src"]})
    cand=sorted({j for b in base for j in range(b-4,b+14)})
    cols=[COL[(n+k)%len(COL)] for k in range(2)]; good=None
    for c in cols:
        var=[x["id"] for x in p["variants"] if x["title"].startswith(c+" /") and x["title"].endswith("/ M")]
        if not var: print("novar",breed,c); continue
        d=f"out/pmk/{breed}/darktee/{c.replace(' ','_')}"; os.makedirs(d,exist_ok=True); seen=set()
        for i in (good or cand):
            b=get(f"https://images.printify.com/mockup/{pid}/{var[0]}/{i}/x.jpg?camera_label=front")
            if not b: continue
            h=hashlib.md5(b).hexdigest()
            if h in seen: continue
            seen.add(h); open(f"{d}/{i}.jpg","wb").write(b)
        if good is None: good=sorted(int(f[:-4]) for f in os.listdir(d))
    print("done",breed,cols,good,flush=True)

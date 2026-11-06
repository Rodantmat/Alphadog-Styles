import os,json,urllib.request,hashlib,time,re
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
info=json.load(open("out/prodinfo.json")); SH=[x["id"] for x in call("/v1/shops.json")]
SZ={"S","M","L","XL","2XL","3XL","4XL","5XL"}
for key in ["french_bulldog|line_classic|tee|pair","french_bulldog|line_classic|hoodie|pair"]:
    pid=info[key]["id"];p=None
    for sh in SH:
        try: p=call(f"/v1/shops/{sh}/products/{pid}.json"); break
        except Exception: pass
    ids=[]; 
    for im in p["images"]:
        m=re.search(r"/mockup/[^/]+/(\d+)/(\d+)/",im["src"]); 
        if m: ids.append(int(m.group(2)))
    var=[int(re.search(r"/mockup/[^/]+/(\d+)/",im["src"]).group(1)) for im in p["images"] if "/mockup/" in im["src"]][0]
    lo,hi=min(ids),max(ids); print("KEY",key,"bp",p["blueprint_id"],"var",var,"ids",sorted(set(ids)),flush=True)
    d=f"out/mockscan/{p['blueprint_id']}"; os.makedirs(d,exist_ok=True); seen={}
    for i in sorted({j for b0 in set(ids) for j in range(b0-4,b0+12)}):
        time.sleep(1.2)
        try: b=urllib.request.urlopen(urllib.request.Request(f"https://images.printify.com/mockup/{pid}/{var}/{i}/x.jpg?camera_label=front",headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
        except Exception as e: print("ERR",i,e,flush=True); continue
        h=hashlib.md5(b).hexdigest()[:8]
        if h in seen: continue
        seen[h]=i; open(f"{d}/{i}.jpg","wb").write(b); print("NEW",p["blueprint_id"],i,flush=True)

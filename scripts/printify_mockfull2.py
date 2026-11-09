import os,json,re,time,hashlib,urllib.request,sys
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
pids=json.load(open("out/mockcount_pids.json"))
only=sys.argv[1:] 
SH=[s["id"] for s in call("/v1/shops.json")]
os.makedirs("out/mockfull",exist_ok=True)
for prod,pid in pids.items():
    if only and prod not in only: continue
    p=None
    for sh in SH:
        try: p=call(f"/v1/shops/{sh}/products/{pid}.json"); break
        except Exception: pass
    known={}; vars_=set()
    for im in p["images"]:
        m=re.search(r"/mockup/[^/]+/(\d+)/(\d+)/",im["src"]); lab=re.search(r"camera_label=([^&]+)",im["src"])
        if m: known[int(m.group(2))]=lab.group(1) if lab else ""; vars_.add(int(m.group(1)))
    var=sorted(vars_)[0]
    ids=sorted({j for k in known for j in range(k-40,k+70)})
    d=f"out/mockfull/{prod.replace(' ','_').replace(chr(39),'')}"; os.makedirs(d,exist_ok=True)
    found={}; seen={}
    print("PROD",prod,"var",var,"probing",len(ids),"known",known,flush=True)
    for i in ids:
        url=f"https://images.printify.com/mockup/{pid}/{var}/{i}/x.jpg?camera_label=front"
        try: b=urllib.request.urlopen(urllib.request.Request(url,headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
        except Exception as e: time.sleep(0.25); continue
        if len(b)<3000: continue
        h=hashlib.md5(b).hexdigest()[:10]
        found[i]=dict(h=h,bytes=len(b),dup_of=seen.get(h),label=known.get(i,""))
        if h not in seen:
            seen[h]=i; open(f"{d}/{i}.jpg","wb").write(b)
        print("HIT",i,found[i],flush=True); time.sleep(0.3)
    json.dump(dict(pid=pid,var=var,known=known,found=found),open(f"{d}/found.json","w"))
    print("DONE",prod,"distinct images",len(seen),"ids",sorted(found),flush=True)

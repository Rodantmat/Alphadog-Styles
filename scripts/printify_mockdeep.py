import os,json,re,time,hashlib,urllib.request,sys,concurrent.futures as cf
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
cfg=json.load(open("out/mockcount_pids2.json"))
W=int(os.environ.get("W","600"))
only=sys.argv[1:]
SH=[s["id"] for s in call("/v1/shops.json")]
def get(a):
    pid,var,i=a
    for t in range(2):
        try:
            b=urllib.request.urlopen(urllib.request.Request(f"https://images.printify.com/mockup/{pid}/{var}/{i}/x.jpg?camera_label=front",headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
            return i,b
        except Exception as e:
            time.sleep(2 if '429' in str(e) else 0.4)
    return i,None
for prod,c in cfg.items():
    if only and prod not in only: continue
    pid=c["pid"]; p=None
    for sh in SH:
        try: p=call(f"/v1/shops/{sh}/products/{pid}.json"); break
        except Exception: pass
    vs=sorted({int(re.search(r"/mockup/[^/]+/(\d+)/",im["src"]).group(1)) for im in p["images"] if "/mockup/" in im["src"]})
    known={int(re.search(r"/mockup/[^/]+/\d+/(\d+)/",im["src"]).group(1)) for im in p["images"] if "/mockup/" in im["src"]}
    ids=sorted({j for k in known|set(c["seeds"]) for j in range(max(1,k-W),k+W+1)})
    d=f"out/mockdeep/{prod.replace(' ','_').replace(chr(39),'')}"; os.makedirs(d,exist_ok=True)
    print("PROD",prod,"variants",vs,"ids",len(ids),flush=True)
    seen={};found={}
    with cf.ThreadPoolExecutor(3) as ex:
        for i,b in ex.map(get,[(pid,vs[0],i) for i in ids]):
            if not b or len(b)<3000: continue
            h=hashlib.md5(b).hexdigest()[:10]
            if h not in seen:
                seen[h]=i; open(f"{d}/{i}.jpg","wb").write(b); print("NEW",i,len(b),flush=True)
            found[i]=h
    # second variant check: do all found distinct ids exist for another variant too
    import collections
    cnt=collections.Counter(found.values()); bad={h for h,n in cnt.items() if n>25}
    print('placeholder-like hashes',bad,'errors',len(ids)-len(found),flush=True)
    json.dump(dict(pid=pid,variants=vs,found=found,distinct=sorted(seen.values())),open(f"{d}/found.json","w"))
    print("DONE",prod,"distinct",len(seen),sorted(seen.values()),flush=True)

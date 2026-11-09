import os,json,re,urllib.request,collections
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
pids=json.load(open("out/mockcount_pids.json"))
shop=call("/v1/shops.json")
res={}
for prod,pid in pids.items():
    p=None
    for s in shop:
        try: p=call(f"/v1/shops/{s['id']}/products/{pid}.json"); break
        except Exception as e: p=None
    if not p: res[prod]={"pid":pid,"err":"not found"}; continue
    cols={}
    for v in p["variants"]:
        t=v.get("title","")
        cols[v["id"]]=t.split("/")[0].strip()
    per=collections.defaultdict(lambda: collections.defaultdict(set))
    for im in p["images"]:
        m=re.search(r"/mockup/[^/]+/(\d+)/(\d+)/",im["src"])
        lab=re.search(r"camera_label=([^&]+)",im["src"])
        for vid in im.get("variant_ids",[]):
            per[cols.get(vid,str(vid))][vid].add((m.group(2) if m else "?",lab.group(1) if lab else (im.get("position") or "")))
    summ={}
    for c,vs in per.items():
        counts=sorted(set(len(x) for x in vs.values()))
        one=sorted(next(iter(vs.values())))
        summ[c]=dict(variants=len(vs),pics_per_variant=counts,cams=[f"{a}:{b}" for a,b in one])
    res[prod]=dict(pid=pid,title=p["title"],total_images=len(p["images"]),colours=summ)
json.dump(res,open("out/mockcount_result.json","w"),indent=1)
for k,v in res.items():
    print("==",k,v.get("title"),v.get("total_images"))
    for c,s in (v.get("colours") or {}).items(): print("  ",c,s["variants"],s["pics_per_variant"],s["cams"])

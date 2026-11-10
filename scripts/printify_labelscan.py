"""READ-ONLY scan of every live product: where is the brand logo placed? Output out/labelscan/summary.json
(per blueprint: available positions, and per placeholder position the image ids + counts + sample product ids)."""
import os,json,sys,time,urllib.request,collections,concurrent.futures as cf
T=os.environ["PRINTIFY_TOKEN"].strip(); H={"Authorization":"Bearer "+T,"User-Agent":"a"}
def call(p):
    for t in range(6):
        try: return json.loads(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers=H),timeout=90).read())
        except Exception as e: time.sleep(20+15*t if "429" in str(e) else 3+3*t); err=e
    raise err
shops=call("/v1/shops.json"); print([(s["id"],s["title"]) for s in shops],flush=True)
prods=[]
for s in shops:
    pg=1
    while True:
        d=call(f"/v1/shops/{s['id']}/products.json?limit=50&page={pg}"); prods+=[(s["id"],p) for p in d["data"]]
        if pg>=d["last_page"]: break
        pg+=1
print("products",len(prods),flush=True)
neck=json.load(open("out/neck_ids.json")); LOGO=set(neck.values())
summ=collections.defaultdict(lambda:collections.defaultdict(lambda:collections.defaultdict(list)))
avail={}
def one(sp):
    s,p=sp
    out=[]
    for a in p["print_areas"]:
        for ph in a["placeholders"]:
            for im in ph["images"]: out.append((ph["position"],im["id"],im.get("x"),im.get("y"),im.get("scale")))
    return s,p["id"],p["blueprint_id"],p["print_provider_id"],p["title"],out
with cf.ThreadPoolExecutor(8) as ex:
    for k,(s,pid,bp,pv,title,out) in enumerate(ex.map(one,prods)):
        for pos,iid,x,y,sc in out: summ[bp][pos][iid].append((s,pid))
        avail.setdefault((bp,pv),None)
        if k%500==0: print(k,flush=True)
for (bp,pv) in avail:
    try:
        v=call(f"/v1/catalog/blueprints/{bp}/print_providers/{pv}/variants.json")["variants"]
        avail[(bp,pv)]=sorted({p["position"] for x in v for p in x["placeholders"]})
    except Exception as e: avail[(bp,pv)]=str(e)[:60]
res={}
for bp,d in summ.items():
    res[str(bp)]={"available":{f"{k[0]}/{k[1]}":v for k,v in avail.items() if k[0]==bp},
      "positions":{pos:{iid:{"n":len(l),"logo":iid in LOGO,"sample":l[:2]} for iid,l in ims.items() if len(l)>=2 or iid in LOGO} for pos,ims in d.items()}}
os.makedirs("out/labelscan",exist_ok=True); json.dump(res,open("out/labelscan/summary.json","w"),indent=1)
print("done")

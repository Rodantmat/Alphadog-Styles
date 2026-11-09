"""Move hoodie BACK art lower (hood must not cover it): art height <= HMAX of print area, bottom edge at BOT of print area.
usage: printify_lower.py APPLY SHARD N [PID...]   -> out/lower/shard<N>.tsv"""
import os,json,sys,time,urllib.request,urllib.error,concurrent.futures as cf
T=os.environ["PRINTIFY_TOKEN"].strip(); H={"Authorization":"Bearer "+T,"User-Agent":"a","Content-Type":"application/json"}
HMAX=float(os.environ.get("HMAX","0.66")); BOT=float(os.environ.get("BOT","0.96"))
def call(p,method="GET",body=None):
    err=None
    for t in range(5):
        try:
            rq=urllib.request.Request("https://api.printify.com"+p,headers=H,method=method,data=json.dumps(body).encode() if body is not None else None)
            return json.load(urllib.request.urlopen(rq,timeout=120))
        except urllib.error.HTTPError as e:
            err=e; b=e.read()[:300]
            if e.code in(400,404,422): raise RuntimeError(f"{e.code} {b}")
            time.sleep(30 if e.code==429 else 4+5*t)
        except Exception as e: err=e; time.sleep(4+5*t)
    raise err
apply_,sh,n=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]); only=set(sys.argv[4:])
rows=[r for r in json.load(open("out/mockidx/index.json")) if r["bp"]==77 and (not only or r["pid"] in only)]
rows=[r for i,r in enumerate(sorted(rows,key=lambda r:r["pid"])) if i%n==sh]
dims={}
def area(bp,prov,vid):
    k=(bp,prov)
    if k not in dims:
        d=call(f"/v1/catalog/blueprints/{bp}/print_providers/{prov}/variants.json")["variants"]
        dims[k]={v["id"]:{p["position"]:(p["width"],p["height"]) for p in v["placeholders"]} for v in d}
    return dims[k].get(vid,{}).get("back")
os.makedirs("out/lower",exist_ok=True); out=open(f"out/lower/shard{sh}.tsv","w"); out.write("shop\tpid\ttitle\tbefore(scale,y)\tafter(scale,y)\tstatus\n")
def one(r):
    try:
        p=call(f"/v1/shops/{r['shop']}/products/{r['pid']}.json"); log=[]; ch=False
        for a in p["print_areas"]:
            for ph in a["placeholders"]:
                if ph["position"]!="back": continue
                ar=area(p["blueprint_id"],p["print_provider_id"],a["variant_ids"][0])
                if not ar: continue
                W,Hh=ar
                for im in ph["images"]:
                    if im.get("name")=="text_layer.svg": continue
                    ratio=im["height"]/im["width"]; s=im["scale"]
                    s=min(s,HMAX*Hh/(W*ratio),0.9)          # height cap, width cap
                    h=s*W*ratio; y=round(BOT-h/(2*Hh),3)
                    log.append((im["scale"],im["y"],round(s,3),y))
                    if abs(s-im["scale"])>0.0005 or abs(y-im["y"])>0.0005: im["scale"]=round(s,3); im["y"]=y; ch=True
        st="nochange"
        if ch:
            body={"print_areas":[{"variant_ids":a["variant_ids"],"placeholders":[{"position":ph["position"],"images":[{k2:im[k2] for k2 in("id","x","y","scale","angle") if k2 in im} for im in ph["images"] if im.get("name")!="text_layer.svg"]} for ph in a["placeholders"] if ph["images"]]} for a in p["print_areas"]]}
            if apply_:
                try: call(f"/v1/shops/{r['shop']}/products/{r['pid']}.json","PUT",body); st="UPDATED"
                except Exception as e: st="ERR "+str(e)[:160]
            else: st="would-update"
        return [f"{r['shop']}\t{r['pid']}\t{p['title']}\t{l[0]},{l[1]}\t{l[2]},{l[3]}\t{st}\n" for l in log] or [f"{r['shop']}\t{r['pid']}\t{p['title']}\t-\t-\tno-back\n"]
    except Exception as e: return [f"{r['shop']}\t{r['pid']}\t{r['title']}\tERR\t\t{str(e)[:100]}\n"]
with cf.ThreadPoolExecutor(3) as ex:
    for i,res in enumerate(ex.map(one,rows)):
        for l in res: out.write(l)
        out.flush()
        if i%20==0: print(i,len(rows),flush=True)
out.close()

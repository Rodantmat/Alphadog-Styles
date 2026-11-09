"""AUDIT every product's front/back artwork: geometry vs print area + art touching its own canvas edge (cut at source).
usage: printify_audit.py SHARD NSHARDS [PID...]  -> out/audit/shard<N>.tsv"""
import os,json,sys,urllib.request,time,io,threading,concurrent.futures as cf
from PIL import Image
import numpy as np
T=os.environ["PRINTIFY_TOKEN"].strip(); H={"Authorization":"Bearer "+T,"User-Agent":"a"}
def call(p,raw=False):
    err=None
    for t in range(5):
        try:
            r=urllib.request.urlopen(urllib.request.Request(p if p.startswith("http") else "https://api.printify.com"+p,headers=H),timeout=90).read()
            return r if raw else json.loads(r)
        except Exception as e: err=e; time.sleep(3+4*t)
    raise err
sh,n=int(sys.argv[1]),int(sys.argv[2]); only=set(sys.argv[3:])
rows=json.load(open("out/mockidx/index.json")); rows=[r for r in rows if r["bp"] in(77,145,12,1734,1735,1447,1402,18,39) and (not only or r["pid"] in only)]
rows=[r for i,r in enumerate(sorted(rows,key=lambda r:r["pid"])) if i%n==sh]
os.makedirs("out/audit",exist_ok=True); L=threading.Lock(); dims={}; arts={}
def area(bp,prov,vid,pos):
    k=(bp,prov)
    if k not in dims:
        d=call(f"/v1/catalog/blueprints/{bp}/print_providers/{prov}/variants.json")["variants"]
        dims[k]={v["id"]:{p["position"]:(p["width"],p["height"]) for p in v["placeholders"]} for v in d}
    return dims[k].get(vid,{}).get(pos)
def art(iid):
    if iid in arts: return arts[iid]
    try:
        u=call(f"/v1/uploads/{iid}.json"); b=call(u["preview_url"],raw=True); im=Image.open(io.BytesIO(b)).convert("RGBA"); a=np.array(im)[:,:,3]
        if a.max()==0: r=None
        else:
            ys,xs=np.where(a>20); h,w=a.shape; r=(round(xs.min()/w,3),round(ys.min()/h,3),round((xs.max()+1)/w,3),round((ys.max()+1)/h,3),u.get("width"),u.get("height"))
    except Exception as e: r=("err",str(e)[:40])
    arts[iid]=r; return r
out=open(f"out/audit/shard{sh}.tsv","w"); out.write("shop\tpid\ttitle\tbp\tprov\tpos\timg\tx\ty\tscale\tareaW\tareaH\timgW\timgH\tbbox\toverflow\tedgecut\n")
def one(r):
    try: p=call(f"/v1/shops/{r['shop']}/products/{r['pid']}.json")
    except Exception as e: return [f"{r['shop']}\t{r['pid']}\t{r['title']}\tERR\t{e}\n"]
    res=[]
    for a in p["print_areas"]:
        for ph in a["placeholders"]:
            if ph["position"] in("neck","left_sleeve","right_sleeve") or not ph["images"]: continue
            for im in ph["images"]:
                ar=area(p["blueprint_id"],p["print_provider_id"],a["variant_ids"][0],ph["position"])
                if not ar: res.append(f"{r['shop']}\t{r['pid']}\t{p['title']}\t{p['blueprint_id']}\t{p['print_provider_id']}\t{ph['position']}\t{im['id']}\tNOAREA\n"); continue
                W,Hh=ar; w=im["scale"]*W; h=w*im["height"]/im["width"]; cx,cy=im["x"]*W,im["y"]*Hh
                ov=[]
                if cy-h/2<-2: ov.append(f"top{round(-(cy-h/2)/h*100)}%")
                if cy+h/2>Hh+2: ov.append(f"bottom{round((cy+h/2-Hh)/h*100)}%")
                if cx-w/2<-2: ov.append("left")
                if cx+w/2>W+2: ov.append("right")
                bb=art(im["id"]); ec=""
                if bb and bb[0]!="err":
                    if bb[1]<0.004: ec+="T"
                    if bb[3]>0.996: ec+="B"
                    if bb[0]<0.004: ec+="L"
                    if bb[2]>0.996: ec+="R"
                    # visible content vs print area
                    cy0=cy-h/2+bb[1]*h; cy1=cy-h/2+bb[3]*h
                    if cy0<-2 or cy1>Hh+2: ov.append("CONTENTCLIP")
                res.append(f"{r['shop']}\t{r['pid']}\t{p['title']}\t{p['blueprint_id']}\t{p['print_provider_id']}\t{ph['position']}\t{im['id']}\t{im['x']}\t{im['y']}\t{im['scale']}\t{W}\t{Hh}\t{im['width']}\t{im['height']}\t{bb}\t{','.join(ov)}\t{ec}\n")
    return res
with cf.ThreadPoolExecutor(6) as ex:
    for k,res in enumerate(ex.map(one,rows)):
        for l in res: out.write(l)
        if k%50==0: out.flush(); print(k,len(rows),flush=True)
out.close()

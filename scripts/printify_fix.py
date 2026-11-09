"""Fix artwork that overflows its print area: shrink (scale) about its centre so visible content sits inside the area with margin.
usage: printify_fix.py APPLY(0|1) SHARD N [PID...]  reads out/audit/*.tsv (rows with overflow); writes out/fix/shard<N>.tsv"""
import os,json,sys,glob,csv,time,urllib.request,threading,concurrent.futures as cf
T=os.environ["PRINTIFY_TOKEN"].strip(); H={"Authorization":"Bearer "+T,"User-Agent":"a","Content-Type":"application/json"}
def call(p,method="GET",body=None):
    err=None
    for t in range(5):
        try:
            rq=urllib.request.Request("https://api.printify.com"+p,headers=H,method=method,data=json.dumps(body).encode() if body is not None else None)
            return json.load(urllib.request.urlopen(rq,timeout=120))
        except urllib.error.HTTPError as e:
            err=e; msg=e.read()[:300]
            if e.code in(400,404,422): raise RuntimeError(f"{e.code} {msg}")
            time.sleep(4+5*t)
        except Exception as e: err=e; time.sleep(4+5*t)
    raise err
apply_,sh,n=int(sys.argv[1]),int(sys.argv[2]),int(sys.argv[3]); only=set(sys.argv[4:])
bad={}
for f in glob.glob("out/audit/shard*.tsv"):
    for r in csv.DictReader(open(f),delimiter="\t"):
        if r.get("overflow") and r["pid"]: bad.setdefault((r["shop"],r["pid"]),[]).append(r)
keys=sorted(k for k in bad if not only or k[1] in only); keys=[k for i,k in enumerate(keys) if i%n==sh]
M=0.04  # margin
os.makedirs("out/fix",exist_ok=True); out=open(f"out/fix/shard{sh}.tsv","w"); out.write("shop\tpid\ttitle\tpos\tbefore_scale\tafter_scale\tstatus\n")
def fix(k):
    shop,pid=k; p=call(f"/v1/shops/{shop}/products/{pid}.json"); res=[]; changed=False
    # dims from the audit rows
    dim={(r["pos"],r["img"]):r for r in bad[k]}
    for a in p["print_areas"]:
        for ph in a["placeholders"]:
            for im in ph["images"]:
                r=dim.get((ph["position"],im["id"]))
                if not r: continue
                W,Hh=float(r["areaW"]),float(r["areaH"]); w=im["scale"]*W; h=w*im["height"]/im["width"]; cx,cy=im["x"]*W,im["y"]*Hh
                import re
                fl=[float(x) for x in re.findall(r"(?<![\w.])\d\.\d+|(?<=\()\d\.\d+",r["bbox"].replace("np.float64(","(").split(", 4")[0])] if "err" not in r["bbox"] else []
                bb=tuple(fl[:4]) if len(fl)>=4 else (0,0,1,1)
                # visible content box relative to image centre, as fractions of image w/h
                lim=1.0
                # allowed half extents
                ax=min(cx,W-cx)*(1-M); ay=min(cy,Hh-cy)*(1-M)
                # content extents from centre (in units of full image size): left=(0.5-bb0), right=(bb2-0.5) etc
                ex=max(0.5-bb[0],bb[2]-0.5); ey=max(0.5-bb[1],bb[3]-0.5)
                s_x=ax/(ex*im["width"]/im["width"]*W) ; s_y=ay/(ey*(im["height"]/im["width"])*W)
                new=round(min(im["scale"],s_x,s_y),3)
                res.append((ph["position"],im["scale"],new))
                if new<im["scale"]-0.001: im["scale"]=new; changed=True
    st="nochange"
    if changed:
        body={"print_areas":[{"variant_ids":a["variant_ids"],"placeholders":[{"position":ph["position"],"images":[{k2:im[k2] for k2 in("id","x","y","scale","angle") if k2 in im} for im in ph["images"]]} for ph in a["placeholders"]]} for a in p["print_areas"]]}
        if apply_:
            try: call(f"/v1/shops/{shop}/products/{pid}.json","PUT",body); st="UPDATED"
            except Exception as e: st="ERR "+str(e)[:200]
        else: st="would-update"
    return [f"{shop}\t{pid}\t{p['title']}\t{x[0]}\t{x[1]}\t{x[2]}\t{st}\n" for x in res]
with cf.ThreadPoolExecutor(3) as ex:
    for i,res in enumerate(ex.map(fix,keys)):
        for l in res: out.write(l)
        out.flush(); 
        if i%20==0: print(i,len(keys),flush=True)
out.close()

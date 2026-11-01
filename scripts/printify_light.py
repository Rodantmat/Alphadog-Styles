"""Light-only launch helper. env: MODE (probe|hoodies|tees|publish), SHOP, CHANNEL, PRINTIFY_TOKEN, plus per-mode vars."""
import os, json, time, urllib.request, urllib.error
T=os.environ["PRINTIFY_TOKEN"]; MODE=os.environ.get("MODE","probe")
def call(m,p,b=None,retry=8):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:600]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep((40 if e.code==429 else 10)*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
if MODE=="probe":
    r=call("GET","/v1/catalog/blueprints/12/print_providers/99/variants.json")
    vs=r["variants"]; print("n variants",len(vs))
    print("colors",sorted({v["options"]["color"] for v in vs}))
    print("sizes",sorted({v["options"]["size"] for v in vs}))
    print("placeholders",json.dumps(vs[0]["placeholders"]))
    json.dump(vs,open("out/bella_variants.json","w"))
    h=call("GET","/v1/catalog/blueprints/77/print_providers/99/variants.json")["variants"]
    import collections
    print("HOODIE placeholders",collections.Counter(json.dumps(v["placeholders"]) for v in h).most_common(4))
    # hoodie sample product light/dark info
    SHOP=int(os.environ["SHOP"]); st=json.load(open(f"out/state_{os.environ['CHANNEL']}.json"))
    k=next(k for k in st if k.endswith("hoodie|pair") or k.endswith("hoodie|portrait"))
    p=call("GET",f"/v1/shops/{SHOP}/products/{st[k]['id']}.json")
    print("hoodie",k,p["blueprint_id"],p.get("visible"),p.get("is_locked"),len(p["variants"]),"enabled",sum(v["is_enabled"] for v in p["variants"]))
    print(json.dumps({kk:p[kk] for kk in p if kk not in("variants","images","print_areas","options","description")})[:700])
    print("external",p.get("external"))

if MODE not in("probe","fetch"):
    import base64
    CH=os.environ["CHANNEL"]; SHOP=int(os.environ["SHOP"]); EXTRA=os.environ.get("EXTRA","")
    BREEDS=json.load(open("scripts/breeds25.json"))
    DES=["line_classic","line_cool","line_heart","geo_classic","geo_cool","geo_heart"]
    up=json.load(open("out/uploads.json")); neck=json.load(open("out/neck_ids.json"))
    SF=f"out/state_light_{CH}.json"; LS=json.load(open(SF)) if os.path.exists(SF) else {}
    def save(): json.dump(LS,open(SF,"w"),indent=1)
    BELLA_LIGHT=["White","Natural","Soft Cream","Ash","Athletic Heather","Sand Dune","Light Blue","Soft Pink"]
    HOOD_LIGHT=["White","Sand","Sport Grey","Light Blue","Light Pink","Ash"]
    if CH=="etsy": BELLA_LIGHT=BELLA_LIGHT[:5]; HOOD_LIGHT=HOOD_LIGHT[:4]
    SIZES=["S","M","L","XL","2XL","3XL"]
    TEE_P={"etsy":{"front":2799,"pair":3299},"ebay":{"front":2299,"pair":2999},"tiktok":{"front":2499,"pair":3199}}
    HOOD_P={"etsy":{"front":4999,"pair":5799},"ebay":{"front":4499,"pair":5499},"tiktok":{"front":4999,"pair":5999}}
    SUR={"tee":{"2XL":200,"3XL":400},"hoodie":{"2XL":400,"3XL":800}}
    def price(prod,layout,size):
        base=(TEE_P if prod=="tee" else HOOD_P)[CH]["pair" if layout=="pair" else "front"]
        return base+SUR[prod].get(size,0)
    def selection():
        out=[]
        if CH=="etsy":
            st=json.load(open("out/state_etsy.json"))
            for k in st: out.append(k)
        elif CH=="ebay":
            for bi,(slug,_,_) in enumerate(BREEDS):
                for d in DES:
                    if bi<25: out.append(f"{slug}|{d}|tee|portrait")
                    if bi<8: out.append(f"{slug}|{d}|hoodie|portrait")
        else:
            for slug,_,_ in BREEDS:
                for d in DES:
                    for lay in ("pair","portrait","pocket"):
                        for prod in ("tee","hoodie"): out.append(f"{slug}|{d}|{prod}|{lay}")
        return out

    DIMF="out/upl_dims.json"; DIMS=json.load(open(DIMF)) if os.path.exists(DIMF) else {}
    def dims(i):
        if i not in DIMS:
            r=call("GET",f"/v1/uploads/{i}.json"); DIMS[i]=[r["width"],r["height"]]; json.dump(DIMS,open(DIMF,"w"))
        return DIMS[i]
    AREAS={"tee":{"front":(2767,3362),"back":(2767,3362)},"hoodie":{"front":(3531,2352),"back":(3852,3210)}}
    def fit(prod,side,kind,iw,ih):
        W,H=AREAS[prod][side]; a=iw/ih
        if kind=="back":
            if prod=="hoodie":  # hood covers the top of the window: smaller and bottom-aligned
                hf=float(os.environ.get("HOODBACK","0.77")); w=min(0.97,hf*H*a/W); h=w*W/a/H
                return dict(x=0.5,y=round(1-h/2-0.005,3),scale=round(w,3))
            w=min(0.97,0.97*H*a/W); return dict(x=0.5,y=0.5,scale=round(w,3))
        if kind=="pocket":
            w=min((0.30*3185/W if prod=="tee" else 0.26),0.30*H*a/W); h=w*W/a/H
            return dict(x=0.76,y=round(0.05+h/2 if prod=="hoodie" else 0.17,3),scale=round(w,3))
        w=min(0.75 if prod=="tee" else 0.58,0.95*H*a/W); h=w*W/a/H
        return dict(x=0.5,y=round(min(0.5,0.04+h/2),3),scale=round(w,3))
    def sync_wait(): time.sleep(0.35)
    if MODE=="hoodies":
        base=json.load(open(f"out/state_{CH}.json")); n=0
        for k in selection():
            slug,d,prod,lay=k.split("|")
            if prod!="hoodie" or k in LS or k not in base: continue
            pid=base[k]["id"]; p=call("GET",f"/v1/shops/{SHOP}/products/{pid}.json")
            vs=[{"id":v["id"],"price":price("hoodie",lay,v["options"] if False else next((s for s in SIZES if v["title"].endswith("/ "+s) or v["title"].endswith("/"+s)),"M")),"is_enabled":(v["is_enabled"] and any(v["title"].startswith(c) for c in HOOD_LIGHT))} for v in p["variants"]]
            pas=[]
            for a_ in p["print_areas"]:
                phs=[]
                for q in a_["placeholders"]:
                    ims=[]
                    for im in q["images"]:
                        if im.get("type")!="image/png": continue
                        d_=dict(id=im["id"],angle=0)
                        if q["position"]=="front": d_.update(fit("hoodie","front","pocket" if lay in("pair","pocket") else "big",*dims(im["id"])))
                        elif q["position"]=="back": d_.update(fit("hoodie","back","back",*dims(im["id"])))
                        else: d_.update(x=im["x"],y=im["y"],scale=im["scale"])
                        ims.append(d_)
                    if ims: phs.append({"position":q["position"],"images":ims})
                pas.append({"variant_ids":a_["variant_ids"],"placeholders":phs})
            try: call("PUT",f"/v1/shops/{SHOP}/products/{pid}.json",{"variants":vs,"print_areas":pas},retry=1)
            except Exception:
                print("PAYLOAD",json.dumps(pas)[:1500]); print("ORIG",json.dumps([[ (q["position"],[(i["id"],i.get("type")) for i in q["images"]]) for q in a_["placeholders"]] for a_ in p["print_areas"]])[:1500]); raise
            LS[k]={"id":pid,"prod":"hoodie","enabled":sum(v["is_enabled"] for v in vs),"published":False}; save(); n+=1
            if n%25==0: print("hoodies",n,flush=True)
            sync_wait()
        print("HOODIES DONE",n,flush=True)
    if MODE=="tees":
        V=call("GET","/v1/catalog/blueprints/12/print_providers/99/variants.json")["variants"]; maxn=int(EXTRA or 100000); n=0
        vs=[v for v in V if v["options"]["size"] in SIZES and v["options"]["color"] in BELLA_LIGHT]
        THEME={"line":"Continuous Line Art","geo":"Geometric"}; VAR={"classic":"Classic","cool":"Cool","heart":"Heart"}
        ids=[v["id"] for v in vs]; W,H=2767,3362; ASP={"front":1169/1200,"back":4471/5400}
        def place(side,kind):
            a=ASP[side]
            if kind=="pocket": w=0.30*3185/W; h=w*W/a/H; return dict(x=0.76,y=0.17,scale=round(w,3))
            if kind=="back": w=min(0.95*H*a/W,0.95); return dict(x=0.5,y=0.5,scale=round(w,3))
            w=0.75; h=w*W/a/H; return dict(x=0.5,y=round(min(0.5,0.04+h/2),3),scale=w)
        for k in selection():
            slug,d,prod,lay=k.split("|")
            if prod!="tee" or k in LS: continue
            if n>=maxn: break
            disp=next(x[1] for x in BREEDS if x[0]==slug); desc=next(x[2] for x in BREEDS if x[0]==slug)
            th,vr=d.split("_"); ts={"line":"Line Art","geo":"Geometric"}[th]
            ls={"pair":"Pocket Portrait + Full Body Back","pocket":"Pocket Print","portrait":"Big Portrait"}[lay]
            if CH=="etsy": title=f"{disp} {THEME[th]} {VAR[vr]} Dog Lover T-Shirt | {ls}"
            else:
                ls2={"pair":"Front & Back","pocket":"Pocket Print","portrait":"Big Portrait"}[lay]
                title=f"{disp} T-Shirt Dog Lover {ts} {VAR[vr]} {ls2}"
                if len(title)>80: title=f"{disp} T-Shirt Dog {ts} {VAR[vr]} {ls2}"
                if len(title)>80: title=title[:80].rsplit(" ",1)[0]
            ph=[]
            if lay in("pair","pocket"): ph.append({"position":"front","images":[dict(id=up[f"{slug}/{d}/front_blackink"],angle=0,**fit("tee","front","pocket",*dims(up[f"{slug}/{d}/front_blackink"])))]})
            if lay=="portrait": ph.append({"position":"front","images":[dict(id=up[f"{slug}/{d}/frontbig_blackink"],angle=0,**fit("tee","front","big",*dims(up[f"{slug}/{d}/frontbig_blackink"])))]})
            if lay=="pair": ph.append({"position":"back","images":[dict(id=up[f"{slug}/{d}/back_blackink"],angle=0,**fit("tee","back","back",*dims(up[f"{slug}/{d}/back_blackink"])))]})
            ph.append({"position":"neck","images":[{"id":neck["blackink"],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
            body={"title":title,"description":f"<p>{desc.capitalize()}: the {disp} captured in {THEME[th].lower()} artwork, {VAR[vr].lower()} style.</p><p>Premium soft Bella+Canvas 3001 unisex jersey tee with {THEME[th].lower()} artwork. Layout: {ls.lower()}.</p><p>Unisex fit, soft and comfortable. Made to order by a Printify partner; allow about 10 business days to produce before shipping.</p>",
              "blueprint_id":12,"print_provider_id":99,
              "variants":[{"id":i,"price":price("tee",lay,next(v["options"]["size"] for v in vs if v["id"]==i)),"is_enabled":True} for i in ids],
              "print_areas":[{"variant_ids":ids,"placeholders":ph}],
              "tags":[t[:20] for t in [disp.lower(),"dog lover shirt","dog mom gift","dog dad gift","dog breed shirt","line art dog" if th=="line" else "geometric dog","minimalist dog","pet lover gift","dog owner gift","unisex t-shirt","dog portrait","gift for dog lover","dog art"]][:13]}
            p=call("POST",f"/v1/shops/{SHOP}/products.json",body)
            LS[k]={"id":p["id"],"prod":"tee","enabled":len(ids),"published":False}; save(); n+=1
            print("OK",k,p["id"],flush=True); sync_wait()
        print("TEES DONE",n,flush=True)
    if MODE=="publish":
        cnt=int(EXTRA or 1); n=0
        for k,v in LS.items():
            if v.get("published") or "#old" in k: continue
            if n>=cnt: break
            call("POST",f"/v1/shops/{SHOP}/products/{v['id']}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True})
            v["published"]=True; save(); n+=1; print("PUBLISHED",k,v["id"],flush=True); time.sleep(1.5)
        print("PUBLISH DONE",n,flush=True)
    if MODE=="check":
        for k,v in list(LS.items())[:int(EXTRA or 3)]:
            p=call("GET",f"/v1/shops/{SHOP}/products/{v['id']}.json")
            print(k,p["blueprint_id"],"enabled",sum(x["is_enabled"] for x in p["variants"]),"ext",p.get("external"),flush=True)
            for im in p["images"][:4]: print("  IMG",im["src"],im.get("variant_ids")[:1],flush=True)
if MODE=="fetch":
    os.makedirs("out/mock3",exist_ok=True)
    for i,u in enumerate(os.environ["EXTRA"].split()):
        d=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"a"}),timeout=60).read()
        open(f"out/mock3/{i}.jpg","wb").write(d); print("saved",i,len(d),flush=True)
if MODE=="sample":
    os.makedirs("out/mock4",exist_ok=True)
    ks=[k for k in LS if "#old" not in k]; n=int(EXTRA or 12); step=max(1,len(ks)//n); info=[]
    for i,k in enumerate(ks[::step][:n]):
        p=call("GET",f"/v1/shops/{SHOP}/products/{LS[k]['id']}.json")
        for j,im in enumerate(p["images"][:6]):
            try:
                d=urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"}),timeout=60).read()
                open(f"out/mock4/{CH}_{i:02d}_{j}.jpg","wb").write(d)
            except Exception as e: print("ERR",e)
        info.append(k); print("sampled",i,k,flush=True)
    json.dump(info,open(f"out/mock4/{CH}_keys.json","w"))
if MODE=="oldcheck":
    os.makedirs("out/mock4",exist_ok=True)
    for k,v in LS.items():
        if "#old" not in k: continue
        p=call("GET",f"/v1/shops/{SHOP}/products/{v['id']}.json")
        print("OLD",k,p["title"],"external",p.get("external"),"visible",p.get("visible"),flush=True)
        for a_ in p["print_areas"]:
            for q in a_["placeholders"]:
                for im in q["images"]:
                    print(" ",q["position"],im.get("type"),im.get("scale"),im.get("x"),im.get("y"),flush=True)
        for j,im in enumerate(p["images"][:4]):
            open(f"out/mock4/old_{j}.jpg","wb").write(urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"}),timeout=60).read())
if MODE=="verify":
    res={}; bad=0
    for k,v in LS.items():
        if "#old" in k: continue
        p=call("GET",f"/v1/shops/{SHOP}/products/{v['id']}.json"); prod=v["prod"]; probs=[]
        for a_ in p["print_areas"]:
            for q in a_["placeholders"]:
                if q["position"] not in("front","back"): continue
                W,H=AREAS[prod][q["position"]]
                for im in q["images"]:
                    if im.get("type")!="image/png": continue
                    iw,ih=dims(im["id"]); s=im["scale"]; h=s*W/(iw/ih)/H
                    l,r=im["x"]-s/2,im["x"]+s/2; t,b=im["y"]-h/2,im["y"]+h/2
                    if l<-0.005 or r>1.005 or t<-0.005 or b>1.005: probs.append(f'{q["position"]} out of window l={l:.2f} r={r:.2f} t={t:.2f} b={b:.2f}')
        enabled=[x for x in p["variants"] if x["is_enabled"]]
        if not enabled: probs.append("no enabled variants")
        res[k]={"ok":not probs,"probs":probs}; bad+=bool(probs)
        time.sleep(0.2)
    json.dump(res,open(f"out/verify_{CH}.json","w"),indent=1)
    print("VERIFIED",len(res),"BAD",bad,flush=True)
    for k,r in res.items():
        if not r["ok"]: print("BAD",k,r["probs"],flush=True)

if MODE=="refit":
    n=0; FITV="v3-"+os.environ.get("HOODBACK","0.77")
    for k,v in LS.items():
        if v.get("fit")==FITV: continue
        prod=v["prod"]; lay=k.split("|")[3].split("#")[0]
        p=call("GET",f"/v1/shops/{SHOP}/products/{v['id']}.json"); pas=[]
        for a_ in p["print_areas"]:
            phs=[]
            for q in a_["placeholders"]:
                ims=[]
                for im in q["images"]:
                    if im.get("type")!="image/png": continue
                    d_=dict(id=im["id"],angle=0)
                    if q["position"]=="front": d_.update(fit(prod,"front","pocket" if lay in("pair","pocket") else "big",*dims(im["id"])))
                    elif q["position"]=="back": d_.update(fit(prod,"back","back",*dims(im["id"])))
                    else: d_.update(x=im["x"],y=im["y"],scale=im["scale"])
                    ims.append(d_)
                if ims: phs.append({"position":q["position"],"images":ims})
            pas.append({"variant_ids":a_["variant_ids"],"placeholders":phs})
        call("PUT",f"/v1/shops/{SHOP}/products/{v['id']}.json",{"print_areas":pas}); v["fit"]=FITV; save(); n+=1; time.sleep(1.0)
        if n%20==0: print("refit",n,flush=True)
    print("REFIT DONE",n,flush=True)

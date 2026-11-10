"""New product lines for a sales channel (default TikTok): unisex tank, women's racerback tank, men's polo, women's polo, 3 caps.
Light colors + black-ink art only (same uploaded art as the tees). MODE=build creates drafts, MODE=publish publishes N per run.
Env: PRINTIFY_TOKEN, SHOP, CHANNEL, MODE, EXTRA (max items)."""
import os,json,time,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"]; SHOP=int(os.environ["SHOP"]); CH=os.environ.get("CHANNEL","tiktok"); MODE=os.environ.get("MODE","build"); EXTRA=int(os.environ.get("EXTRA") or 100000)
def call(m,p,b=None,retry=8):
    for a in range(retry):
        r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:900]
            if e.code in(429,500,502,503,504) and a<retry-1: time.sleep(min(300,30*(a+1))); continue
            raise RuntimeError(f"{e.code} {p} {msg}")
BREEDS=json.load(open("scripts/breeds25.json")); DES=["line_classic","line_cool","line_heart","geo_classic","geo_cool","geo_heart"]
up=json.load(open("out/uploads.json"))
SF=f"out/state_extras_{CH}.json"; LS=json.load(open(SF)) if os.path.exists(SF) else {}
def save(): json.dump(LS,open(SF,"w"),indent=1)
DIMF="out/upl_dims.json"; DIMS=json.load(open(DIMF)) if os.path.exists(DIMF) else {}
def dims(i):
    if i not in DIMS:
        r=call("GET",f"/v1/uploads/{i}.json"); DIMS[i]=[r["width"],r["height"]]; json.dump(DIMS,open(DIMF,"w"))
    return DIMS[i]
# product: blueprint, position, light colors, sizes, price (cents, TikTok), surcharge, art key, rule, name
P={
 "tank":dict(bp=39,pos="front",colors=["White","Athletic Heather"],sizes=["XS","S","M","L","XL","2XL"],price=2499,sur={"2XL":200},art="frontbig",rule="big",
             name="Tank Top",blank="Bella+Canvas 3480 unisex jersey tank: soft, lightweight 100% Airlume cotton (heathers include polyester), retail fit."),
 "wtank":dict(bp=18,pos="front",colors=["Solid White","Heather Grey","Solid Mint","Solid Tahiti Blue","Solid Light Orange","Solid Warm Gray"],sizes=["XS","S","M","L","XL","2XL"],price=2399,sur={"2XL":200},art="frontbig",rule="big",
             name="Women's Racerback Tank",blank="Next Level 1533 women's ideal racerback tank: lightweight, form-fitting, cotton/poly blend."),
 "polo":dict(bp=1402,pos="left_chest",colors=["White","Athletic Heather"],sizes=["S","M","L","XL","2XL","3XL"],price=3499,sur={"2XL":200,"3XL":400},art="front",rule="fill",
             name="Polo Shirt",blank="JERZEES 443M men's piqué polo with the dog printed on the chest. Classic fit, ribbed collar."),
 "wpolo":dict(bp=6488,pos="left_chest_dtf",colors=["White","Platinum","Charity Pink"],sizes=["XS","S","M","L","XL","2XL","3XL"],price=3999,sur={"2XL":200,"3XL":400},art="front",rule="fill",
             name="Women's Polo Shirt",blank="CORE365 women's Origin performance piqué polo with the dog printed on the chest. Moisture-wicking, snag-resistant."),
 "cap_dad":dict(bp=1447,pos="front_dtf",colors=["White","Khaki","Stone","Light Blue","Pink"],sizes=None,price=2699,sur={},art="front",rule="fill",
             name="Dad Hat",blank="Yupoong 6245CM classic dad cap: unstructured, low profile, cotton twill, adjustable strap. Printed front."),
 "cap_foam":dict(bp=1735,pos="front_dtf",colors=["White","Light Pink/White","Blue/White"],sizes=None,price=2499,sur={},art="front",rule="fill",
             name="Foam Trucker Hat",blank="OTTO 39-165 retro foam-front trucker hat with mesh back and snapback. Printed front."),
 "cap_mesh":dict(bp=1734,pos="front_dtf",colors=["White"],sizes=None,price=2599,sur={},art="front",rule="fill",
             name="Mesh Trucker Cap",blank="Yupoong 6006 five-panel trucker cap with mesh back and snapback. Printed front."),
}
# OWNER RULE (docs/RULES_LEDGER P1/P2): logo ONLY on the inside neck label; products without a neck position (polo, caps) carry NO logo. Never use back/hat positions.
# brand logo / label (same AlphaDog logo as the tee & hoodie neck labels)
NECK=json.load(open("out/neck_ids.json"))["blackink"]
LABEL={"tank":("neck",dict(x=.5,y=.5,scale=1.0)),"wtank":("neck",dict(x=.5,y=.5,scale=1.0)),
       "polo":None,"wpolo":None,
       "cap_dad":None,"cap_foam":None,"cap_mesh":None}
def label_ph(prod):
    L=LABEL.get(prod)
    return [{"position":L[0],"images":[dict(id=NECK,angle=0,**L[1])]}] if L else []
def place(spec,area,iw,ih):
    W,H=area; a=iw/ih
    if spec["rule"]=="fill": k=.92; w=min(k,k*H*a/W); return dict(x=.5,y=.5,scale=round(w,3))
    w=min(.75,.95*H*a/W); h=w*W/a/H; return dict(x=.5,y=round(min(.5,.04+h/2),3),scale=round(w,3))
THEME={"line":"Continuous Line Art","geo":"Geometric"}; VAR={"classic":"Classic","cool":"Cool","heart":"Heart"}
if MODE=="build":
    n=0; VV={}
    for slug,disp,desc in BREEDS:
        for d in DES:
            for prod,spec in P.items():
                if prod in os.environ.get("SKIP","").split(","): continue
                k=f"{slug}|{d}|{prod}"
                if k in LS: continue
                if n>=EXTRA: break
                if prod not in VV:
                    vs=call("GET",f"/v1/catalog/blueprints/{spec['bp']}/print_providers/99/variants.json")["variants"]
                    sel=[v for v in vs if v["options"].get("color") in spec["colors"] and (spec["sizes"] is None or v["options"].get("size") in spec["sizes"])]
                    area=next(([ph["width"],ph["height"]] for ph in sel[0]["placeholders"] if ph["position"]==spec["pos"]))
                    VV[prod]=(sel,area)
                sel,area=VV[prod]; th,vr=d.split("_")
                img=up[f"{slug}/{d}/{spec['art']}_blackink"]
                ts={"line":"Line Art","geo":"Geometric"}[th]
                title=f"{disp} {spec['name']} Dog Lover {ts} {VAR[vr]}"
                if len(title)>80: title=f"{disp} {spec['name']} Dog {ts} {VAR[vr]}"[:80]
                body={"title":title,
                  "description":f"<p>{desc.capitalize()}: the {disp} in {THEME[th].lower()} artwork, {VAR[vr].lower()} style.</p><p>{spec['blank']}</p><p>Made to order by a Printify partner and shipped within the US.</p>",
                  "blueprint_id":spec["bp"],"print_provider_id":99,
                  "variants":[{"id":v["id"],"price":spec["price"]+spec["sur"].get(v["options"].get("size"),0),"is_enabled":True} for v in sel],
                  "print_areas":[{"variant_ids":[v["id"] for v in sel],"placeholders":[{"position":spec["pos"],"images":[dict(id=img,angle=0,**place(spec,area,*dims(img)))]}]+label_ph(prod)}],
                  "tags":[t[:20] for t in [disp.lower(),"dog lover gift","dog mom gift","dog dad gift","dog breed","line art dog" if th=="line" else "geometric dog","minimalist dog","pet lover gift",spec["name"].lower()[:20],"dog portrait","gift for dog lover","dog art"]][:13]}
                p=call("POST",f"/v1/shops/{SHOP}/products.json",body)
                LS[k]={"id":p["id"],"prod":prod,"published":False}; save(); n+=1
                if n%20==0: print("built",n,flush=True)
                time.sleep(0.4)
    print("EXTRAS BUILD DONE",n,len(LS),flush=True)
if MODE=="publish":  # published flags live in a separate file so the build job and the publish cron never edit the same file
    PF=f"out/state_extras_{CH}_pub.json"; PUB=json.load(open(PF)) if os.path.exists(PF) else {}
    LF=f"out/state_extras_{CH}_label.json"; LAB=json.load(open(LF)) if os.path.exists(LF) else {}
    skip=os.environ.get("SKIP","").split(","); n=0
    for k,v in LS.items():
        if PUB.get(k) or v["prod"] in skip: continue
        if LABEL.get(v["prod"]) and not LAB.get(k): continue   # wait until the logo label is on it
        if n>=EXTRA: break
        call("POST",f"/v1/shops/{SHOP}/products/{v['id']}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True})
        PUB[k]=True; json.dump(PUB,open(PF,"w")); n+=1; time.sleep(1.5)
    print("EXTRAS PUBLISH DONE",n,len(PUB),"/",len(LS),flush=True)
if MODE=="relabel":  # add the AlphaDog logo label to products built before labels existed; re-publish ones already live
    LF=f"out/state_extras_{CH}_label.json"; LAB=json.load(open(LF)) if os.path.exists(LF) else {}
    PF=f"out/state_extras_{CH}_pub.json"; PUB=json.load(open(PF)) if os.path.exists(PF) else {}
    n=0; fails=0
    for k,v in LS.items():
        if LAB.get(k) or not LABEL.get(v["prod"]): continue
        if n>=EXTRA: break
        try:
            p=call("GET",f"/v1/shops/{SHOP}/products/{v['id']}.json"); pos=LABEL[v["prod"]][0]
            pas=[]
            for a in p["print_areas"]:
                phs=[{"position":q["position"],"images":[{"id":i["id"],"x":i["x"],"y":i["y"],"scale":i["scale"],"angle":i.get("angle",0)} for i in q["images"]]} for q in a["placeholders"] if q["position"]!=pos and q.get("images")]
                pas.append({"variant_ids":a["variant_ids"],"placeholders":phs+label_ph(v["prod"])})
            call("PUT",f"/v1/shops/{SHOP}/products/{v['id']}.json",{"print_areas":pas},retry=4)
            if PUB.get(k): call("POST",f"/v1/shops/{SHOP}/products/{v['id']}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True})
            LAB[k]=True; json.dump(LAB,open(LF,"w")); n+=1
            if n%25==0: print("relabelled",n,flush=True)
        except Exception as e:
            fails+=1; print("RELABEL FAIL",k,str(e)[:900],flush=True)
            if fails>20: break
        time.sleep(0.5)
    print("RELABEL DONE",n,"fails",fails,len(LAB),flush=True)
if MODE=="check":
    os.makedirs("out/extras_check",exist_ok=True); n=0
    for k,v in list(LS.items())[:EXTRA]:
        p=call("GET",f"/v1/shops/{SHOP}/products/{v['id']}.json")
        for j,im in enumerate(p["images"][:10]):
            fn=f"out/extras_check/{k.replace('|','_')}_{j}_{im.get('position')}.jpg"
            try: open(fn,"wb").write(urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"}),timeout=60).read()); n+=1
            except Exception as e: print("ERR",e)
    print("CHECK DONE",n)

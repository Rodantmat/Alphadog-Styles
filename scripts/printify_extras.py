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
            msg=e.read().decode()[:300]
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
                  "print_areas":[{"variant_ids":[v["id"] for v in sel],"placeholders":[{"position":spec["pos"],"images":[dict(id=img,angle=0,**place(spec,area,*dims(img)))]}]}],
                  "tags":[t[:20] for t in [disp.lower(),"dog lover gift","dog mom gift","dog dad gift","dog breed","line art dog" if th=="line" else "geometric dog","minimalist dog","pet lover gift",spec["name"].lower()[:20],"dog portrait","gift for dog lover","dog art"]][:13]}
                p=call("POST",f"/v1/shops/{SHOP}/products.json",body)
                LS[k]={"id":p["id"],"prod":prod,"published":False}; save(); n+=1
                if n%20==0: print("built",n,flush=True)
                time.sleep(0.4)
    print("EXTRAS BUILD DONE",n,len(LS),flush=True)
if MODE=="publish":
    n=0
    for k,v in LS.items():
        if v.get("published"): continue
        if n>=EXTRA: break
        call("POST",f"/v1/shops/{SHOP}/products/{v['id']}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True})
        v["published"]=True; save(); n+=1; time.sleep(1.5)
    print("EXTRAS PUBLISH DONE",n,sum(1 for v in LS.values() if v.get("published")),"/",len(LS),flush=True)

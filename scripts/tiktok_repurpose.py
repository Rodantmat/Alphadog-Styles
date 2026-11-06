"""Repurpose the legacy light-only Printify tee listings (TikTok) into dark-shade single-breed tees, same slot.
Env: PRINTIFY_TOKEN, MODE (check|one|all), ONLY (optional tiktok listing id suffix). Keeps the Printify product (so order mapping stays correct)."""
import os,json,time,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"]; SHOP=29546485; MODE=os.environ.get("MODE","check"); ONLY=os.environ.get("ONLY","")
def call(m,p,b=None,retry=6):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try:
            x=urllib.request.urlopen(r,timeout=120).read(); return json.loads(x) if x else {}
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:500]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep(30*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
# (TikTok listing id suffix, legacy state key)
SLOTS=[("629924364734","french_bulldog|geo_classic|tee|pair"),("630561505726","french_bulldog|line_cool|tee|pocket"),
("631113122238","french_bulldog|geo_classic|tee|pocket"),("639713870270","french_bulldog|line_heart|tee|pocket"),
("639715115454","french_bulldog|geo_cool|tee|portrait"),("640287572414","french_bulldog|line_classic|tee|pair"),
("649934275006","french_bulldog|line_cool|tee|pair"),("651522015678","french_bulldog|line_heart|tee|pair"),
("651566514622","french_bulldog|geo_classic|tee|portrait"),("652510298558","french_bulldog|line_classic|tee|pocket"),
("653201768894","french_bulldog|line_classic|tee|portrait"),("653446480318","french_bulldog|geo_heart|tee|pair"),
("654581891518","french_bulldog|geo_cool|tee|pocket"),("663932240318","french_bulldog|line_cool|tee|portrait"),
("982061941182","dachshund|geo_cool|tee|pair"),("984248680894","dachshund|line_classic|tee|pocket")]
TARGET=["bulldog","american_pit_bull_terrier","boxer","pug","boston_terrier","yorkshire_terrier","shih_tzu","australian_shepherd",
"doberman_pinscher","great_dane","pomeranian","bernese_mountain_dog","siberian_husky","pembroke_welsh_corgi","cavalier_king_charles_spaniel","miniature_schnauzer"]
NAME={"bulldog":"English Bulldog","american_pit_bull_terrier":"American Pit Bull Terrier","boxer":"Boxer","pug":"Pug","boston_terrier":"Boston Terrier",
"yorkshire_terrier":"Yorkshire Terrier","shih_tzu":"Shih Tzu","australian_shepherd":"Australian Shepherd","doberman_pinscher":"Doberman Pinscher","great_dane":"Great Dane",
"pomeranian":"Pomeranian","bernese_mountain_dog":"Bernese Mountain Dog","siberian_husky":"Siberian Husky","pembroke_welsh_corgi":"Pembroke Welsh Corgi",
"cavalier_king_charles_spaniel":"Cavalier King Charles Spaniel","miniature_schnauzer":"Miniature Schnauzer"}
DARK=["Black","Navy","Dark Grey Heather","Forest","Maroon","Asphalt","Red"]
SIZES=["S","M","L","XL","2XL","3XL"]; SUR={"2XL":200,"3XL":400}
up=json.load(open("out/uploads.json")); neck=json.load(open("out/neck_ids.json"))
LS=json.load(open("out/state_light_tiktok.json"))
DIMS={}
def dims(i):
    if i not in DIMS:
        r=call("GET",f"/v1/uploads/{i}.json"); DIMS[i]=[r["width"],r["height"]]
    return DIMS[i]
W,H=2767,3362
def fit(kind,iw,ih):
    a=iw/ih
    if kind=="pocket": w=min(0.30*3185/W,0.30*H*a/W); return dict(x=0.76,y=0.17,scale=round(w,3))
    if kind=="back": w=min(0.97,0.97*H*a/W); return dict(x=0.5,y=0.5,scale=round(w,3))
    w=min(0.75,0.95*H*a/W); h=w*W/a/H; return dict(x=0.5,y=round(min(0.5,0.04+h/2),3),scale=round(w,3))
V=call("GET","/v1/catalog/blueprints/12/print_providers/99/variants.json")["variants"]
def build(i):
    slug=TARGET[i]; disp=NAME[slug]
    if i<8: d,lay="line_classic","pair"; title=f"{disp} Shirt | Line Art Dog T-Shirt in Black & Dark Colors, Dog Mom Dad Gift"; style="continuous line art"
    else: d,lay="geo_cool","portrait"; title=f"{disp} Shirt | Geometric Sunglasses Dog T-Shirt in Black & Dark Colors, Dog Lover Gift"; style="geometric sunglasses art"
    vs=[v for v in V if v["options"]["color"] in DARK and v["options"]["size"] in SIZES]
    ids=[v["id"] for v in vs]
    ph=[]
    if lay=="pair":
        fk=up[f"{slug}/{d}/front_whiteink"]; bk=up[f"{slug}/{d}/back_whiteink"]
        ph+= [{"position":"front","images":[dict(id=fk,angle=0,**fit("pocket",*dims(fk)))]},{"position":"back","images":[dict(id=bk,angle=0,**fit("back",*dims(bk)))]}]
    else:
        fk=up[f"{slug}/{d}/frontbig_whiteink"]; ph.append({"position":"front","images":[dict(id=fk,angle=0,**fit("big",*dims(fk)))]})
    ph.append({"position":"neck","images":[{"id":neck["whiteink"],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
    return slug,disp,d,lay,title,style,vs,ids,ph
def run(i,ts,key):
    pid=LS[key]["id"]; p=call("GET",f"/v1/shops/{SHOP}/products/{pid}.json")
    ext=(p.get("external") or {}).get("id"); print("slot",i,key,"printify",pid,"tiktok",ext,"title",p["title"][:50],flush=True)
    if not str(ext).endswith(ts): print("MISMATCH - skipping",flush=True); return False
    if MODE=="check": return True
    slug,disp,d,lay,title,style,vs,ids,ph=build(i)
    enabled=set(ids); allv=[]
    for v in p["variants"]:
        sz=next((s for s in SIZES if v["title"].endswith("/ "+s) or v["title"].endswith("/"+s)),"M")
        allv.append({"id":v["id"],"price":(3199 if lay=="pair" else 2499)+SUR.get(sz,0),"is_enabled":v["id"] in enabled})
    missing=enabled-{v["id"] for v in p["variants"]}
    if missing: print("variants not on product, will rebuild:",len(missing),flush=True)
    body={"title":title,"description":f"<p>The {disp} in {style} on a premium soft Bella+Canvas 3001 unisex tee, printed in white ink so it pops on dark colors.</p><p>Unisex fit, soft and comfortable. Made to order, ships in about 5-10 business days.</p>",
      "tags":[t[:20] for t in [disp.lower(),f"{disp.lower()} shirt","dog lover shirt","dog mom gift","dog dad gift","black dog shirt","dog breed shirt","minimalist dog","pet lover gift","dog owner gift","unisex t-shirt","dog art","gift for dog lover"]][:13],
      "variants":allv,"print_areas":[{"variant_ids":sorted(v["id"] for v in p["variants"]),"placeholders":ph}]}
    if missing:
        body["blueprint_id"]=12; body["print_provider_id"]=99
        print("ABORT: product lacks dark variants; cannot edit in place",flush=True); return False
    call("PUT",f"/v1/shops/{SHOP}/products/{pid}.json",body,retry=1); print("EDITED",title[:60],flush=True)
    time.sleep(20)
    call("POST",f"/v1/shops/{SHOP}/products/{pid}/publish.json",{"title":True,"description":True,"images":True,"variants":True,"tags":True,"keyfeatures":True,"shipping_template":True})
    print("PUBLISHED",pid,flush=True); return True
n=0
for i,(ts,key) in enumerate(SLOTS):
    if ONLY and ts!=ONLY: continue
    if MODE=="one" and n>=1: break
    try:
        if run(i,ts,key): n+=1
    except Exception as e: print("ERR",i,e,flush=True)
    time.sleep(3)
print("DONE",n,flush=True)

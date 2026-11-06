"""Restore a legacy light Printify tee exactly as printify_light.py built it (black ink, light colours). Env: KEY (state key)"""
import os,json,time,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"]; SHOP=29546485; KEY=os.environ["KEY"]
def call(m,p,b=None):
    d=json.dumps(b).encode() if b is not None else None
    r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
    try: x=urllib.request.urlopen(r,timeout=120).read(); return json.loads(x) if x else {}
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:400]); raise
LS=json.load(open("out/state_light_tiktok.json")); up=json.load(open("out/uploads.json")); neck=json.load(open("out/neck_ids.json"))
B=json.load(open("scripts/breeds25.json"))
slug,d,prod,lay=KEY.split("|"); pid=LS[KEY]["id"]
p=call("GET",f"/v1/shops/{SHOP}/products/{pid}.json")
V=call("GET","/v1/catalog/blueprints/12/print_providers/99/variants.json")["variants"]
LIGHT=["White","Natural","Soft Cream","Ash","Athletic Heather","Sand Dune","Light Blue","Soft Pink"]; SIZES=["S","M","L","XL","2XL","3XL"]; SUR={"2XL":200,"3XL":400}
vs=[v for v in V if v["options"]["size"] in SIZES and v["options"]["color"] in LIGHT]; ids=[v["id"] for v in vs]
print("light variants",len(ids),"expected enabled",LS[KEY]["enabled"])
W,H=2767,3362
def dims(i): r=call("GET",f"/v1/uploads/{i}.json"); return r["width"],r["height"]
def fit(kind,iw,ih):
    a=iw/ih
    if kind=="pocket": w=min(0.30*3185/W,0.30*H*a/W); return dict(x=0.76,y=0.17,scale=round(w,3))
    if kind=="back": w=min(0.97,0.97*H*a/W); return dict(x=0.5,y=0.5,scale=round(w,3))
    w=min(0.75,0.95*H*a/W); h=w*W/a/H; return dict(x=0.5,y=round(min(0.5,0.04+h/2),3),scale=round(w,3))
ph=[]
if lay in("pair","pocket"): k=up[f"{slug}/{d}/front_blackink"]; ph.append({"position":"front","images":[dict(id=k,angle=0,**fit("pocket",*dims(k)))]})
if lay=="portrait": k=up[f"{slug}/{d}/frontbig_blackink"]; ph.append({"position":"front","images":[dict(id=k,angle=0,**fit("big",*dims(k)))]})
if lay=="pair": k=up[f"{slug}/{d}/back_blackink"]; ph.append({"position":"back","images":[dict(id=k,angle=0,**fit("back",*dims(k)))]})
ph.append({"position":"neck","images":[{"id":neck["blackink"],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
disp=next(x[1] for x in B if x[0]==slug); desc=next(x[2] for x in B if x[0]==slug)
th,vr=d.split("_"); THEME={"line":"Continuous Line Art","geo":"Geometric"}; VAR={"classic":"Classic","cool":"Cool","heart":"Heart"}; ts={"line":"Line Art","geo":"Geometric"}[th]
ls={"pair":"Pocket Portrait + Full Body Back","pocket":"Pocket Print","portrait":"Big Portrait"}[lay]; ls2={"pair":"Front & Back","pocket":"Pocket Print","portrait":"Big Portrait"}[lay]
title=f"{disp} T-Shirt Dog Lover {ts} {VAR[vr]} {ls2}"
if len(title)>80: title=f"{disp} T-Shirt Dog {ts} {VAR[vr]} {ls2}"
base={"pair":3199,"pocket":3199,"portrait":2499}[lay]
sz=lambda v: v["options"]["size"]
allv=[]
enabled=set(ids)
for v in p["variants"]:
    s=next((s for s in SIZES if v["title"].endswith("/ "+s) or v["title"].endswith("/"+s)),"M")
    allv.append({"id":v["id"],"price":base+SUR.get(s,0),"is_enabled":v["id"] in enabled})
body={"title":title,"description":f"<p>{desc.capitalize()}: the {disp} captured in {THEME[th].lower()} artwork, {VAR[vr].lower()} style.</p><p>Premium soft Bella+Canvas 3001 unisex jersey tee with {THEME[th].lower()} artwork. Layout: {ls.lower()}.</p><p>Unisex fit, soft and comfortable. Made to order by a Printify partner; allow about 10 business days to produce before shipping.</p>",
 "tags":[t[:20] for t in [disp.lower(),"dog lover shirt","dog mom gift","dog dad gift","dog breed shirt","line art dog" if th=="line" else "geometric dog","minimalist dog","pet lover gift","dog owner gift","unisex t-shirt","dog portrait","gift for dog lover","dog art"]][:13],
 "variants":allv,"print_areas":[{"variant_ids":sorted({i for a_ in p["print_areas"] for i in a_["variant_ids"]}),"placeholders":ph}]}
call("PUT",f"/v1/shops/{SHOP}/products/{pid}.json",body); print("RESTORED",title,"enabled",sum(x["is_enabled"] for x in allv))

"""Fix mini poodle Geometric Heart art (front was only the small heart; back had head+body).
Swaps old upload ids -> corrected art in every product of every shop. Keeps on-garment HEIGHT (scale adjusted by aspect)."""
import os,json,base64,urllib.request,urllib.error,time
T=os.environ["PRINTIFY_TOKEN"].strip();DRY=os.environ.get("DRY","1")=="1"
def call(m,p,b=None,retry=9):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:400]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep(20*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
up=json.load(open("out/uploads.json"))
BREED=os.environ.get("BREED","mini_poodle"); DES=os.environ.get("DES","geo_heart"); B=f"{BREED}/{DES}/"
SRC=os.environ.get("SRC") or f"shop/art/{BREED}/{DES}_fixed"
KINDS=["front_blackink","front_whiteink","back_blackink","back_whiteink"]+([f"frontbig_{i}" for i in ("blackink","whiteink")] if os.path.exists(f"{SRC}/frontbig_blackink.png") else [])
new={}
for k in KINDS:
    if DRY: new[k]="NEW_"+k; continue
    fn=f"{SRC}/{k}.png"
    new[k]=call("POST","/v1/uploads/images.json",{"file_name":f"{BREED}_{DES}_fixed_{k}.png","contents":base64.b64encode(open(fn,"rb").read()).decode()})["id"]
from PIL import Image
def asp(fn): im=Image.open(fn); return im.width/im.height
NA={k:asp(f"{SRC}/{k}.png") for k in KINDS}
OLD={}
for kind in ["front","frontbig","back"]:
    for ink in ["blackink","whiteink"]:
        k=B+f"{kind}_{ink}"
        if k in up:
            u=call("GET",f"/v1/uploads/{up[k]}.json"); nk=f"{kind}_{ink}" if f"{kind}_{ink}" in KINDS else ("back" if kind=="back" else "front")+"_"+ink; OLD[up[k]]=(nk, u["width"]/u["height"])
print("old ids",{k:v for k,v in OLD.items()},"new aspects",NA,flush=True)
stats={};touched=[]
for s in call("GET","/v1/shops.json"):
    SHOP=s["id"]; st=stats.setdefault(f'{SHOP} {s.get("title")}',{"fixed":0,"failed":0}); page=1
    while True:
        r=call("GET",f"/v1/shops/{SHOP}/products.json?limit=50&page={page}")
        for p in r["data"]:
            if not any(im["id"] in OLD for a in p["print_areas"] for q in a["placeholders"] for im in q["images"]): continue
            def fix(im):
                d={k:v for k,v in im.items() if k in("id","x","y","scale","angle")}
                if im["id"] in OLD:
                    nk,oa=OLD[im["id"]]; d["id"]=new[nk]; d["scale"]=min(round(im["scale"]*NA[nk]/oa,4),0.99)
                return d
            pa=[{"variant_ids":a["variant_ids"],"placeholders":[{"position":q["position"],"images":[fix(im) for im in q["images"] if im.get("type")!="text/plain"]} for q in a["placeholders"] if q["images"]]} for a in p["print_areas"]]
            touched.append([SHOP,p["id"],p["title"][:70],p.get("blueprint_id")])
            if DRY: st["fixed"]+=1; continue
            try: call("PUT",f"/v1/shops/{SHOP}/products/{p['id']}.json",{"print_areas":pa}); st["fixed"]+=1
            except Exception: st["failed"]+=1
            time.sleep(0.3)
        if page>=r.get("last_page",1): break
        page+=1
json.dump({"stats":stats,"touched":touched,"new_ids":new},open("out/artfix_result.json","w"),indent=1)
print(json.dumps(stats,indent=1)); [print(t) for t in touched]

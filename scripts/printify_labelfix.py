"""FIX brand-label placement on every live product (owner rule: logo ONLY on the inside neck label, tone-on-tone: black ink on light garments, white ink on dark, never printed outside).
 1) polo (bp1402): remove the logo printed on the OUTSIDE back (polo has no neck-label position)
 2) caps (1447 etc): remove logo/embroidery placed on back/left/right
 3) any neck label: ink must match garment tone (dark colours -> whiteink v3, light -> blackink v3); old v1 ids -> v3; splits print areas when a group mixes tones
 DRY=1 only reports. Output out/labelfix_result.json. Env: PRINTIFY_TOKEN, DRY"""
import os,json,time,urllib.request,urllib.error,collections
T=os.environ["PRINTIFY_TOKEN"].strip(); DRY=os.environ.get("DRY","1")=="1"
def call(m,p,b=None,retry=8):
    for a in range(retry):
        r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:1200]
            if e.code in(429,500,502,503,504) and a<retry-1: time.sleep(20*(a+1)); continue
            raise RuntimeError(f"{e.code} {p} {msg}")
DARK=("black","navy","charcoal","dark","asphalt","forest","maroon","espresso","brown","deep","military","indigo","midnight","heather navy","storm","graphite","burgundy","cardinal","royal","kelly","evergreen","dk ","pine","cocoa","chocolate","coal","olive","hunter","emerald","purple","plum","denim","slate","steel","oxford","iron","bottle","army")
def is_dark(c): c=(c or "").lower(); return any(k in c for k in DARK) and not any(k in c for k in ("light","white","natural"))
# neck v3 upload ids (logo + "AlphaDog Styles" name); text_layer.svg entries (text/plain) are part of the label and are kept
B2=json.load(open("out/brand_v2_ids.json")); V3={"white":B2["neck_whiteink_v3"],"black":B2["neck_blackink_v3"]}; OLD_V1=set(json.load(open('out/neck_ids.json')).values())
prods=[]
for s_ in call("GET","/v1/shops.json"):
    pg=1
    while True:
        d=call("GET",f"/v1/shops/{s_['id']}/products.json?limit=50&page={pg}"); prods+=[(s_["id"],p) for p in d["data"]]
        if pg>=d["last_page"]: break
        pg+=1
ONLY=set(filter(None,os.environ.get("ONLY","").split(",")))
if ONLY: prods=[(s_,p) for s_,p in prods if p["id"] in ONLY]
print("products",len(prods),flush=True)
if ONLY: print(json.dumps([(p["id"],p["print_areas"]) for s_,p in prods][:1])[:3000])
OUTER={1402:{"back"},1447:{"back_hat_embroidery","left_hat_embroidery","right_hat_embroidery","back"},2041:{"back_hat_embroidery","left_hat_embroidery","right_hat_embroidery"}}
catcache={}
def colors(bp,pv):
    if (bp,pv) not in catcache:
        catcache[(bp,pv)]={v["id"]:v["options"].get("color") for v in call("GET",f"/v1/catalog/blueprints/{bp}/print_providers/{pv}/variants.json")["variants"]}
    return catcache[(bp,pv)]
res={"removed_outer":[],"neck_fixed":[],"errors":[],"colors":{}}
def logo_like(im,bp,pos): return im["id"] in OLD_V1 or im["id"] in V3.values() or (pos in OUTER.get(bp,()) )
for s,p in prods:
    bp=p["blueprint_id"]; pv=p["print_provider_id"]; changed=False; new_areas=[]
    for a in p["print_areas"]:
        phs=[]
        for ph in a["placeholders"]:
            if ph["position"] in OUTER.get(bp,()) and ph["images"]:
                res["removed_outer"].append([s,p["id"],p["title"][:60],bp,ph["position"]]); changed=True; continue
            phs.append(ph)
        # tone check on neck
        neck=next((ph for ph in phs if ph["position"]=="neck" and any(i.get("type")!="text/plain" for i in ph["images"])),None)
        if neck:
            names_=" ".join((im.get("name") or "") for q in phs if q["position"]!="neck" for im in q["images"]).lower()
            ink="white" if "whiteink" in names_ else "black" if "blackink" in names_ else None
            groups={"white":[],"black":[]}
            if ink: groups[ink]=list(a["variant_ids"])
            cur=next(i["id"] for i in neck["images"] if i.get("type")!="text/plain")
            ok=(ink is None) or cur==V3[ink]
            if not ok:
                res["neck_fixed"].append([s,p["id"],p["title"][:60],bp,{g:len(l) for g,l in groups.items()},cur[:8]]); changed=True
                for g,l in groups.items():
                    if not l: continue
                    nph=[dict(q) for q in phs if q["position"]!="neck"]+[{"position":"neck","images":[{"id":V3[g],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]+[i for i in neck["images"] if i.get("type")=="text/plain"]}]
                    new_areas.append({"variant_ids":l,"placeholders":[{"position":q["position"],"images":[{k:v for k,v in im.items() if k in("id","x","y","scale","angle")} for im in q["images"]]} for q in nph]})
                continue
        new_areas.append({"variant_ids":a["variant_ids"],"placeholders":[{"position":q["position"],"images":[(im if im.get("type")=="text/plain" else {k:v for k,v in im.items() if k in("id","x","y","scale","angle")}) for im in q["images"]]} for q in phs if q["images"]]})
    if changed and not DRY:
        try:
            call("PUT",f"/v1/shops/{s}/products/{p['id']}.json",{"print_areas":new_areas})
            if p.get("external"): call("POST",f"/v1/shops/{s}/products/{p['id']}/publish.json",{"title":False,"description":False,"images":True,"variants":False,"tags":False,"keyfeatures":False,"shipping_template":False})
        except Exception as e: res["errors"].append([s,p["id"],str(e)[:1200]])
        time.sleep(0.4)
os.makedirs("out",exist_ok=True); json.dump(res,open("out/labelfix_result.json","w"),indent=1)
print("DRY" if DRY else "LIVE","outer removed",len(res["removed_outer"]),"neck fixed",len(res["neck_fixed"]),"errors",len(res["errors"]))
print(collections.Counter((r[3],r[4]) for r in res["removed_outer"])); print(collections.Counter(r[3] for r in res["neck_fixed"])); print(res["colors"])

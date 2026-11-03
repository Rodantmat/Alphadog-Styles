import os,json,base64,urllib.request,urllib.error,time
T=os.environ["PRINTIFY_TOKEN"].strip();SHOP=29544854
def call(m,p,b=None):
    d=json.dumps(b).encode() if b is not None else None
    r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
    try: return json.load(urllib.request.urlopen(r,timeout=120))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:1500]); raise
def upl(fn): return call("POST","/v1/uploads/images.json",{"file_name":"alphadog_"+os.path.basename(fn),"contents":base64.b64encode(open(fn,"rb").read()).decode()})["id"]
ids={k:upl(f"shop/brand/{k}.png") for k in ["neck_blackink_v2","neck_whiteink_v2","capback_blackink","capback_whiteink"]}
json.dump(ids,open("out/brand_v2_ids.json","w"))
# find existing products to copy
prods=[];pg=1
while True:
    r=call("GET",f"/v1/shops/{SHOP}/products.json?limit=50&page={pg}"); prods+=r["data"]
    if pg>=r["last_page"]: break
    pg+=1
def pick(bp): return next(p for p in prods if p["blueprint_id"]==bp and not p["title"].startswith(("NECK LABEL TEST","BRAND TEST","PILOT")))
res={};os.makedirs("out/brandtest",exist_ok=True)
def mk(name,src,colors,extra):
    vs=[v for v in src["variants"] if v["is_enabled"]]
    keep=[v for v in vs if any(c.lower() in v["title"].lower() for c in colors)][:4] or vs[:2]
    kid=[v["id"] for v in keep]
    pa=[]
    for a in src["print_areas"]:
        vids=[i for i in a["variant_ids"] if i in kid]
        if not vids: continue
        ph=[{"position":q["position"],"images":[{k:v for k,v in im.items() if k in("id","x","y","scale","angle")} for im in q["images"]]} for q in a["placeholders"] if q["images"] and q["position"]!="neck"]
        ph.append(extra); pa.append({"variant_ids":vids,"placeholders":ph})
    body={"title":f"BRAND TEST {name} (draft, delete me)","description":"test","blueprint_id":src["blueprint_id"],"print_provider_id":src["print_provider_id"],
          "variants":[{"id":v["id"],"price":v["price"],"is_enabled":True} for v in keep],"print_areas":pa}
    p=call("POST",f"/v1/shops/{SHOP}/products.json",body); time.sleep(25); p=call("GET",f"/v1/shops/{SHOP}/products/{p['id']}.json")
    res[name]={"id":p["id"],"src":src["id"],"src_cost":sorted({v["cost"] for v in src["variants"] if v["id"] in kid}),"new_cost":sorted({v["cost"] for v in p["variants"] if v["is_enabled"]}),
       "positions":sorted({ph["position"] for a in p["print_areas"] for ph in a["placeholders"]})}
    seen=set()
    for im in p["images"]:
        if im["position"] in seen: continue
        seen.add(im["position"]); d=urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"})).read(); open(f"out/brandtest/{name}_{im['position']}.jpg","wb").write(d)
mk("tee",pick(145),["White"],{"position":"neck","images":[{"id":ids["neck_blackink_v2"],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
mk("cap",pick(1447),["Khaki","Stone"],{"position":"back_hat_embroidery","images":[{"id":ids["capback_blackink"],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
json.dump(res,open("out/brandtest/result.json","w"),indent=1); print(json.dumps(res,indent=1))

import os,json,base64,urllib.request,urllib.error,time
T=os.environ["PRINTIFY_TOKEN"].strip();SHOP=29544854
def call(m,p,b=None):
    d=json.dumps(b).encode() if b is not None else None
    r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
    try: return json.load(urllib.request.urlopen(r,timeout=120))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:1500]); raise
def upl(fn): return call("POST","/v1/uploads/images.json",{"file_name":"alphadog_"+os.path.basename(fn),"contents":base64.b64encode(open(fn,"rb").read()).decode()})["id"]
ids=json.load(open("out/brand_v2_ids.json")) if os.path.exists("out/brand_v2_ids.json") else {k:upl(f"shop/brand/{k}.png") for k in ["neck_blackink_v2","neck_whiteink_v2","capback_blackink","capback_whiteink"]}
for k in ["neck_blackink_v3","neck_whiteink_v3"]:
    if k not in ids: ids[k]=upl(f"shop/brand/{k}.png")
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
    keep=[v for v in vs if any(c.lower() in v["title"].lower() for c in colors)][:6] or vs[:2]
    kid=[v["id"] for v in keep]
    pa=[]
    for a in src["print_areas"]:
        vids=[i for i in a["variant_ids"] if i in kid]
        if not vids: continue
        ph=[{"position":q["position"],"images":[{k:v for k,v in im.items() if k in("id","x","y","scale","angle")} for im in q["images"]]} for q in a["placeholders"] if q["images"] and q["position"]!="neck"]
        if extra: ph.append(extra)
        pa.append({"variant_ids":vids,"placeholders":ph})
    body={"title":f"BRAND TEST {name} (draft, delete me)","description":"test","blueprint_id":src["blueprint_id"],"print_provider_id":src["print_provider_id"],
          "variants":[{"id":v["id"],"price":v["price"],"is_enabled":True} for v in keep],"print_areas":pa}
    p=call("POST",f"/v1/shops/{SHOP}/products.json",body); time.sleep(25); p=call("GET",f"/v1/shops/{SHOP}/products/{p['id']}.json")
    res[name]={"id":p["id"],"src":src["id"],"src_cost":sorted({v["cost"] for v in src["variants"] if v["id"] in kid}),"new_cost":sorted({v["cost"] for v in p["variants"] if v["is_enabled"]}),
       "positions":sorted({ph["position"] for a in p["print_areas"] for ph in a["placeholders"]})}
    seen=set()
    for im in p["images"]:
        key=im["position"]+("_"+im["src"].split("camera_label=")[-1].split("&")[0] if "camera_label=" in im["src"] else "")
        if key in seen: continue
        seen.add(key); im["position"]=key; d=urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"})).read(); open(f"out/brandtest/{name}_{im['position']}.jpg","wb").write(d)
MODE=os.environ.get("MODE","cap")
if MODE=="tee": mk("tee",pick(145),["White"],{"position":"neck","images":[{"id":ids["neck_blackink_v3"],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
if MODE=="cap":
  up=json.load(open("out/uploads.json"))
  vs=[v for v in call("GET","/v1/catalog/blueprints/1447/print_providers/99/variants.json")["variants"] if v["options"].get("color") in ("Khaki","Stone")]
  print("cap variants",[(v["id"],v["title"]) for v in vs])
  src={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in vs],
   "print_areas":[{"variant_ids":[v["id"] for v in vs],"placeholders":[{"position":"front_dtf","images":[{"id":up["french_bulldog/line_classic/front_blackink"],"x":0.5,"y":0.5,"scale":0.55,"angle":0}]}]}]}
  mk("cap",src,["Khaki","Stone"],{"position":"back_hat_embroidery","images":[{"id":ids["capback_blackink"],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
  src2=json.loads(json.dumps(src)); mk("cap_noback",src2,["Khaki","Stone"],None)
if MODE=="capfront":
  fid=upl("shop/brand/capfront_fb_line_classic_test.png")
  vs=[v for v in call("GET","/v1/catalog/blueprints/1447/print_providers/99/variants.json")["variants"] if v["options"].get("color") in ("Khaki","Stone")]
  src={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in vs],
   "print_areas":[{"variant_ids":[v["id"] for v in vs],"placeholders":[{"position":"front_dtf","images":[{"id":fid,"x":0.5,"y":0.5,"scale":1.0,"angle":0}]}]}]}
  mk("cap_frontbrand",src,["Khaki","Stone"],None)
if MODE in ("sidetest2","sidetest3"):
  from PIL import Image
  t=Image.open("shop/brand/capside_blackink_tight.png"); tid=upl("shop/brand/capside_blackink_tight.png")
  cv=call("GET","/v1/catalog/blueprints/1447/print_providers/99/variants.json")["variants"]; kv=[v for v in cv if v["options"].get("color")=="Stone"]
  PW,PH=next((q["width"],q["height"]) for q in cv[0]["placeholders"] if q["position"]=="left_hat_embroidery")
  hfrac=(PW/(t.width/t.height))/PH; y=round(1-hfrac/2-0.01,3); print("placeholder",PW,PH,"hfrac",hfrac,"y",y)
  hid=upl("shop/brand/capfront_minipoodle_geoheart_head.png")
  SC=float(os.environ.get("SC","0.75")) if MODE=="sidetest3" else 1.0
  y=round(1-hfrac*SC/2-0.005,3)
  for nm,pos,x in ([("left_low","left_hat_embroidery",.5),("right_low","right_hat_embroidery",.5)] if MODE=="sidetest2" else [("left_lowback","left_hat_embroidery",round(1-SC/2-0.005,3)),("right_lowback","right_hat_embroidery",round(SC/2+0.005,3))]):
    srcc={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in kv],"print_areas":[{"variant_ids":[v["id"] for v in kv],"placeholders":[{"position":"front_dtf","images":[{"id":hid,"x":.5,"y":.5,"scale":.35,"angle":0}]}]}]}
    mk(("SIDE2_" if MODE=="sidetest2" else "SIDE3_")+nm,srcc,["Stone"],{"position":pos,"images":[{"id":tid,"x":x,"y":y,"scale":SC,"angle":0}]}); print(nm,x,y,SC)
if MODE=="sidetest":
  cv=call("GET","/v1/catalog/blueprints/1447/print_providers/99/variants.json")["variants"]; kv=[v for v in cv if v["options"].get("color")=="Stone"]
  hid=upl("shop/brand/capfront_minipoodle_geoheart_head.png")
  for nm,pos,x,y,sc in [("left_center","left_hat_embroidery",.5,.5,1.0),("left_backlow","left_hat_embroidery",.85,.8,.6),("right_center","right_hat_embroidery",.5,.5,1.0)]:
    srcc={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in kv],"print_areas":[{"variant_ids":[v["id"] for v in kv],"placeholders":[{"position":"front_dtf","images":[{"id":hid,"x":.5,"y":.5,"scale":.35,"angle":0}]}]}]}
    mk("SIDE_"+nm,srcc,["Stone"],{"position":pos,"images":[{"id":ids["capback_blackink"],"x":x,"y":y,"scale":sc,"angle":0}]})
if MODE=="capheart":
  from PIL import Image
  head=Image.open("shop/brand/capfront_minipoodle_geoheart_head.png")
  hid=upl("shop/brand/capfront_minipoodle_geoheart_head.png")
  cv=call("GET","/v1/catalog/blueprints/1447/print_providers/99/variants.json")["variants"]; W,H=next((q["width"],q["height"]) for q in cv[0]["placeholders"] if q["position"]=="front_dtf")
  kv=[v for v in cv if v["options"].get("color")=="Khaki"]; w=min(.92,.92*H*(head.width/head.height)/W)
  srcc={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in kv],"print_areas":[{"variant_ids":[v["id"] for v in kv],"placeholders":[{"position":"front_dtf","images":[{"id":hid,"x":.5,"y":.5,"scale":round(w,3),"angle":0}]}]}]}
  mk("SAMPLE_cap_khaki_minipoodle_geoheart_head",srcc,["Khaki"],None)
if MODE in ("capopts","capopts2"):
  up=json.load(open("out/uploads.json"))
  def dims(i): u=call("GET",f"/v1/uploads/{i}.json"); return u["width"],u["height"]
  cv=call("GET","/v1/catalog/blueprints/1447/print_providers/99/variants.json")["variants"]; W,H=next((q["width"],q["height"]) for q in cv[0]["placeholders"] if q["position"]=="front_dtf")
  kv=[v for v in cv if v["options"].get("color")=="Khaki"]
  for d in (["geo_classic","geo_cool","line_heart","line_classic"] if MODE=="capopts" else ["geo_heart/frontbig","geo_heart/back"]):
    cid=up[f"mini_poodle/{d}_blackink"] if "/" in d else up[f"mini_poodle/{d}/front_blackink"]; iw,ih=dims(cid); w=min(.92,.92*H*(iw/ih)/W)
    srcc={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in kv],"print_areas":[{"variant_ids":[v["id"] for v in kv],"placeholders":[{"position":"front_dtf","images":[{"id":cid,"x":.5,"y":.5,"scale":round(w,3),"angle":0}]}]}]}
    mk(f"CAPOPT_{d.replace('/','_')}",srcc,["Khaki"],None)
if MODE=="samples":
  up=json.load(open("out/uploads.json"))
  def dims(i): u=call("GET",f"/v1/uploads/{i}.json"); return u["width"],u["height"]
  def ph(bp,pos):
      v=call("GET",f"/v1/catalog/blueprints/{bp}/print_providers/99/variants.json")["variants"]
      return v,next((q["width"],q["height"]) for q in v[0]["placeholders"] if q["position"]==pos)
  # cap: khaki dad hat, mini poodle geo_heart front
  cv,(W,H)=ph(1447,"front_dtf"); cid=up["mini_poodle/geo_heart/front_blackink"]; iw,ih=dims(cid); a=iw/ih; w=min(.92,.92*H*a/W)
  kv=[v for v in cv if v["options"].get("color")=="Khaki"]
  srcc={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in kv],
    "print_areas":[{"variant_ids":[v["id"] for v in kv],"placeholders":[{"position":"front_dtf","images":[{"id":cid,"x":.5,"y":.5,"scale":round(w,3),"angle":0}]}]}]}
  mk("SAMPLE_cap_khaki_minipoodle_geoheart",srcc,["Khaki"],None)
  # tee: Bella 3001 Natural, front line_cool pocket head, back line_heart body, v3 neck
  tv,(FW,FH)=ph(12,"front"); _,(BW,BH)=ph(12,"back")
  fid=up["mini_poodle/line_cool/front_blackink"]; bid=up["mini_poodle/line_heart/back_blackink"]
  fw=0.30*3185/FW; ba=(lambda d:d[0]/d[1])(dims(bid)); bw=min(.95*BH*ba/BW,.95)
  nv=[v for v in tv if v["options"].get("color")=="Natural" and v["options"].get("size") in ("S","M","L","XL","2XL")]
  srct={"id":"scratch","blueprint_id":12,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2999,"is_enabled":True,"cost":0} for v in nv],
    "print_areas":[{"variant_ids":[v["id"] for v in nv],"placeholders":[{"position":"front","images":[{"id":fid,"x":.76,"y":.17,"scale":round(fw,3),"angle":0}]},
      {"position":"back","images":[{"id":bid,"x":.5,"y":.5,"scale":round(bw,3),"angle":0}]}]}]}
  mk("SAMPLE_tee_natural_minipoodle",srct,["Natural"],{"position":"neck","images":[{"id":ids["neck_blackink_v3"],"x":.5,"y":.5,"scale":1.0,"angle":0}]})
if MODE=="final":
  cv=call("GET","/v1/catalog/blueprints/1447/print_providers/99/variants.json")["variants"]
  print("PLACEHOLDERS",json.dumps(cv[0].get("placeholders")),json.dumps({k:v for k,v in cv[0].items() if k!="placeholders"}))
  from PIL import Image
  head=Image.open("shop/brand/capfront_minipoodle_geoheart_head.png"); hid=upl("shop/brand/capfront_minipoodle_geoheart_head.png")
  W,H=next((q["width"],q["height"]) for q in cv[0]["placeholders"] if q["position"]=="front_dtf")
  kv=[v for v in cv if v["options"].get("color")=="Khaki"]; w=min(.92,.92*H*(head.width/head.height)/W)
  srcc={"id":"scratch","blueprint_id":1447,"print_provider_id":99,"variants":[{"id":v["id"],"title":v["title"],"price":2699,"is_enabled":True,"cost":0} for v in kv],"print_areas":[{"variant_ids":[v["id"] for v in kv],"placeholders":[{"position":"front_dtf","images":[{"id":hid,"x":.5,"y":.5,"scale":round(w,3),"angle":0}]}]}]}
  mk("FINAL_cap_khaki_minipoodle_geoheart_backbrand",srcc,["Khaki"],{"position":"back_hat_embroidery","images":[{"id":ids["capback_blackink"],"x":.5,"y":.5,"scale":1.0,"angle":0}]})
  t=call("GET",f"/v1/shops/{SHOP}/products/6ae98c3776dc38811905cf5a.json")
  seen=set()
  for im in t["images"]:
    key=im["position"]+("_"+im["src"].split("camera_label=")[-1].split("&")[0] if "camera_label=" in im["src"] else "")
    if key in seen: continue
    seen.add(key); open(f"out/brandtest/FINAL_tee_{key}.jpg","wb").write(urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"})).read())
  print("TEE", [(ph["position"],[(i.get("x"),i.get("y"),i.get("scale")) for i in ph["images"]]) for a in t["print_areas"][:1] for ph in a["placeholders"]])
if MODE=="ship":
  for bp in (1447,12):
    r=call("GET",f"/v1/catalog/blueprints/{bp}/print_providers/99/shipping.json"); print("SHIP",bp,[(pr["countries"],pr["first_item"],pr["additional_items"],len(pr["variant_ids"]),(18100 in pr["variant_ids"] or 105377 in pr["variant_ids"])) for pr in r["profiles"] if "US" in pr["countries"]]); print("SHIPV2",bp,json.dumps(call("GET",f"/v2/catalog/blueprints/{bp}/print_providers/99/shipping.json"))[:1500])
  for pid in ("6ae996c2985328babd0caec9","6ae98c3776dc38811905cf5a"):
    t=call("GET",f"/v1/shops/{SHOP}/products/{pid}.json"); print("COST",pid,[(v["title"],v["cost"]) for v in t["variants"] if v["is_enabled"]])
old=json.load(open("out/brandtest/result.json")) if os.path.exists("out/brandtest/result.json") else {}
old.update(res);res=old
json.dump(res,open("out/brandtest/result.json","w"),indent=1); print(json.dumps(res,indent=1))

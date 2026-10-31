import os,json,base64,urllib.request,urllib.error,time
T=os.environ["PRINTIFY_TOKEN"];SHOP=29544854
def call(m,p,b=None):
    d=json.dumps(b).encode() if b is not None else None
    r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
    try: return json.load(urllib.request.urlopen(r,timeout=120))
    except urllib.error.HTTPError as e: print("HTTP",e.code,e.read().decode()[:1200]); raise
up=json.load(open("out/uploads.json")); V=json.load(open("out/printify_variants.json"))
ids={}
for k in ["whiteink","blackink"]:
    b=base64.b64encode(open(f"shop/brand/neck_{k}.png","rb").read()).decode()
    ids[k]=call("POST","/v1/uploads/images.json",{"file_name":f"alphadog_neck_{k}.png","contents":b})["id"]
S="french_bulldog/line_classic/"
def front(ink):return {"position":"front","images":[{"id":up[S+"front_"+ink],"x":0.76,"y":0.17,"scale":0.30,"angle":0}]}
res={}
for name,bp,bk,frontscale in [("tee",145,"145",None),("hoodie",77,"77",None)]:
    vs=[v for v in V[bk]["variants"] if v["options"]["size"] in ("S","M","L","XL") and v["options"]["color"] in ("White","Black")]
    lv=[v["id"] for v in vs if v["options"]["color"]=="White"]; dv=[v["id"] for v in vs if v["options"]["color"]=="Black"]
    def area(vids,ink):
        f=front(ink)
        if name=="hoodie": f["images"][0].update(y=0.25,scale=0.26)
        return {"variant_ids":vids,"placeholders":[f,{"position":"neck","images":[{"id":ids[ink],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]}]}
    body={"title":f"NECK LABEL TEST {name} (draft, delete me)","description":"test","blueprint_id":bp,"print_provider_id":99,
      "variants":[{"id":v["id"],"price":3000,"is_enabled":True} for v in vs],"print_areas":[area(lv,"blackink"),area(dv,"whiteink")]}
    try:
        p=call("POST",f"/v1/shops/{SHOP}/products.json",body)
    except Exception as e:
        res[name]={"error":"create failed"}; continue
    time.sleep(20); p=call("GET",f"/v1/shops/{SHOP}/products/{p['id']}.json")
    res[name]={"id":p["id"],"costs":sorted({v["cost"] for v in p["variants"] if v["is_enabled"]}),
      "print_areas":[[ph["position"] for ph in a["placeholders"]] for a in p["print_areas"]],
      "images":len(p["images"])}
    os.makedirs("out/neck",exist_ok=True); seen=set()
    for im in p["images"]:
        key=(im["position"],tuple(im.get("variant_ids",[])[:1]))
        if im["position"] in seen: continue
        seen.add(im["position"])
        d=urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"})).read(); open(f"out/neck/{name}_{im['position']}.jpg","wb").write(d)
json.dump(res,open("out/neck_result.json","w"),indent=1); print(json.dumps(res,indent=1))

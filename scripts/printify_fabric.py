import os,json,time,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"];SHOP=29544854
def call(m,p,b=None):
    d=json.dumps(b).encode() if b is not None else None
    r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
    for i in range(5):
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            if e.code==429: time.sleep(30); continue
            print("HTTP",e.code,e.read().decode()[:600]); raise
up=json.load(open("out/uploads.json")); S="french_bulldog/line_classic/"
CANDS=[("tee",12,99),("tee",706,29),("tee",139,99),("hoodie",1298,29),("hoodie",696,99),("hoodie",175,99),("hoodie",528,99),("hoodie",793,99)]
res={}
for kind,bp,prov in CANDS:
    key=f"{kind}_{bp}_{prov}"
    try:
        b=call("GET",f"/v1/catalog/blueprints/{bp}.json")
        vs=call("GET",f"/v1/catalog/blueprints/{bp}/print_providers/{prov}/variants.json")["variants"]
        res[key]={"title":b["title"],"brand":b["brand"],"model":b["model"],"desc":b["description"][:400],"nvar":len(vs)}
        cols=sorted({v["options"].get("color","") for v in vs}); res[key]["colors"]=cols
        pick=[v for v in vs if v["options"].get("color") in ("White","Black") and v["options"].get("size") in ("S","XL","2XL","3XL")]
        if not pick: res[key]["note"]="no White/Black S-3XL"; continue
        pos=[p["position"] for p in vs[0]["placeholders"]]
        lv=[v["id"] for v in pick if v["options"]["color"]=="White"]; dv=[v["id"] for v in pick if v["options"]["color"]=="Black"]
        def area(ids,ink):
            return {"variant_ids":ids,"placeholders":[{"position":"front","images":[{"id":up[S+"front_"+ink],"x":.5,"y":.3,"scale":.3,"angle":0}]},{"position":"back","images":[{"id":up[S+"back_"+ink],"x":.5,"y":.5,"scale":.8,"angle":0}]}]}
        body={"title":f"COSTTEST {key} (draft)","description":"cost test","blueprint_id":bp,"print_provider_id":prov,
          "variants":[{"id":v["id"],"price":3000,"is_enabled":True} for v in pick],"print_areas":[area(lv,"blackink")]+([area(dv,"whiteink")] if dv else [])}
        p=call("POST",f"/v1/shops/{SHOP}/products.json",body); time.sleep(8)
        p=call("GET",f"/v1/shops/{SHOP}/products/{p['id']}.json")
        res[key]["product"]=p["id"]
        res[key]["costs"]={v["title"]:v["cost"] for v in p["variants"] if v["is_enabled"]}
    except Exception as e:
        res[key]=res.get(key,{}); res[key]["error"]=str(e)[:200]
    json.dump(res,open("out/fabric.json","w"),indent=1)
print("done")

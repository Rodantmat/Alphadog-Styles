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
vs=call("GET","/v1/catalog/blueprints/12/print_providers/99/variants.json")["variants"]
pick=[v for v in vs if v["options"].get("color") in ("White","Black") and v["options"].get("size") in ("S","XL","2XL","3XL")]
lv=[v["id"] for v in pick if v["options"]["color"]=="White"]; dv=[v["id"] for v in pick if v["options"]["color"]=="Black"]
def area(ids,ink): return {"variant_ids":ids,"placeholders":[{"position":"front","images":[{"id":up[S+"front_"+ink],"x":.5,"y":.3,"scale":.3,"angle":0}]}]}
body={"title":"COSTTEST tee_12 front-only (draft)","description":"cost test","blueprint_id":12,"print_provider_id":99,
 "variants":[{"id":v["id"],"price":3000,"is_enabled":True} for v in pick],"print_areas":[area(lv,"blackink"),area(dv,"whiteink")]}
p=call("POST",f"/v1/shops/{SHOP}/products.json",body); time.sleep(8)
p=call("GET",f"/v1/shops/{SHOP}/products/{p['id']}.json")
json.dump({"id":p["id"],"costs":{v["title"]:v["cost"] for v in p["variants"] if v["is_enabled"]}},open("out/fabric2.json","w"),indent=1)

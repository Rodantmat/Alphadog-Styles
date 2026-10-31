import os, json, base64, urllib.request, urllib.error, sys, time
T=os.environ["PRINTIFY_TOKEN"]; SHOP=29544854
def call(method,path,body=None):
    data=json.dumps(body).encode() if body is not None else None
    r=urllib.request.Request("https://api.printify.com"+path,data=data,method=method,
        headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"alphadog"})
    try:
        return json.load(urllib.request.urlopen(r,timeout=120))
    except urllib.error.HTTPError as e:
        print("HTTP",e.code,e.read().decode()[:1500]); raise
art="shop/art/golden_retriever_line_classic"
ids={}
for k in ["front_blackink","front_whiteink","back_blackink","back_whiteink"]:
    b=base64.b64encode(open(f"{art}/{k}.png","rb").read()).decode()
    r=call("POST","/v1/uploads/images.json",{"file_name":f"golden_line_classic_{k}.png","contents":b})
    ids[k]=r["id"]; print("uploaded",k,r["id"],r.get("width"),r.get("height"))
V=json.load(open("out/printify_variants.json"))["145"]["variants"]
light=["White","Natural","Sand","Sport Grey","Ice Grey","Light Blue","Light Pink"]
dark=["Black","Navy","Charcoal","Dark Heather","Forest Green","Maroon"]
sizes=["S","M","L","XL","2XL","3XL"]
price={"S":2799,"M":2799,"L":2799,"XL":2799,"2XL":2999,"3XL":3199}
vl,vd,variants=[],[],[]
for v in V:
    c,s=v["options"]["color"],v["options"]["size"]
    if s not in sizes: continue
    if c in light: vl.append(v["id"])
    elif c in dark: vd.append(v["id"])
    else: continue
    variants.append({"id":v["id"],"price":price[s],"is_enabled":True})
print("variants",len(variants),"light",len(vl),"dark",len(vd))
def pa(vids,ink):
    return {"variant_ids":vids,"placeholders":[
      {"position":"front","images":[{"id":ids[f"front_{ink}"],"x":0.74,"y":0.17,"scale":0.30,"angle":0}]},
      {"position":"back","images":[{"id":ids[f"back_{ink}"],"x":0.5,"y":0.5,"scale":0.92,"angle":0}]}]}
body={"title":"PILOT Golden Retriever Line Art Tee - Pocket Portrait and Full Body Back (draft)",
 "description":"Pilot draft. Continuous-line golden retriever: small head emblem on the left chest and a large full-body back print. Not for sale.",
 "blueprint_id":145,"print_provider_id":99,"variants":variants,"print_areas":[pa(vl,"blackink"),pa(vd,"whiteink")]}
p=call("POST",f"/v1/shops/{SHOP}/products.json",body)
print("created product",p["id"],p["title"],"| variants",len(p["variants"]),"| visible",p.get("visible"))
time.sleep(25)
p=call("GET",f"/v1/shops/{SHOP}/products/{p['id']}.json")
imgs=p.get("images",[])
print("mockups",len(imgs))
os.makedirs("out/pilot_mockups",exist_ok=True)
seen=set(); n=0
for im in imgs:
    key=(im.get("variant_ids") or [0])[0]
    if im["position"] in seen and n>=8: continue
    seen.add(im["position"])
    try:
        d=urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"alphadog"}),timeout=60).read()
        open(f"out/pilot_mockups/m{n:02d}_{im['position']}.jpg","wb").write(d); n+=1
    except Exception as e: print("img err",e)
    if n>=8: break
print("saved",n)

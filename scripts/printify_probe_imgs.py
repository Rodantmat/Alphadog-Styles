import os,json,urllib.request,urllib.error,copy
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(m,p,b=None):
    r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"User-Agent":"a","Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(r,timeout=60))
    except urllib.error.HTTPError as e: return {"ERR":e.code,"msg":e.read().decode()[:300]}
SHOP,PID=29546485,"6ae6cfcd5d17aa531b00d623"
p=call("GET",f"/v1/shops/{SHOP}/products/{PID}.json")
for a in p["print_areas"][:1]:
    for ph in a["placeholders"]:
        for im in ph["images"]:
            if im.get("type")=="text/plain": print("TEXT",json.dumps(im))
# test 1: PUT unchanged full objects
pa=[{"variant_ids":a["variant_ids"],"placeholders":[{"position":q["position"],"images":q["images"]} for q in a["placeholders"] if q["images"]]} for a in p["print_areas"]]
#print("PUT unchanged:",json.dumps(call("PUT",f"/v1/shops/{SHOP}/products/{PID}.json",{"print_areas":pa}))[:300])

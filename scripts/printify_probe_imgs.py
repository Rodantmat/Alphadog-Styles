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
pa=[{"variant_ids":a["variant_ids"],"placeholders":[{"position":q["position"],"images":[{k:v for k,v in im.items() if k in("id","x","y","scale","angle")} for im in q["images"] if im.get("type")!="text/plain"]} for q in a["placeholders"] if q["images"]]} for a in p["print_areas"]]
r=call("PUT",f"/v1/shops/{SHOP}/products/{PID}.json",{"print_areas":pa}); print("PUT drop text:",json.dumps(r)[:200])
import time; time.sleep(30)
p2=call("GET",f"/v1/shops/{SHOP}/products/{PID}.json")
print("NECK AFTER",[ [im.get("name") for im in ph["images"]] for a in p2["print_areas"][:1] for ph in a["placeholders"] if ph["position"]=="neck"])
seen=set()
for im in p2["images"]:
    if im["position"]=="neck" or "collar" in im["src"]:
        if im["src"] in seen: continue
        seen.add(im["src"]); print("MOCK",im["position"],im["src"][:200]); 
        open("neck_after.jpg","wb").write(urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"})).read()); break

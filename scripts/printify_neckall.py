import os,json,base64,urllib.request,urllib.error,time,sys
T=os.environ["PRINTIFY_TOKEN"];SHOP=int(os.environ["SHOP"]);LIMIT=int(os.environ.get("LIMIT","100000"))
def call(m,p,b=None,retry=4):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:500]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep(8*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
up=json.load(open("out/uploads.json")) if os.path.exists("out/uploads.json") else {}
neck=json.load(open("out/neck_ids.json")) if os.path.exists("out/neck_ids.json") else {}
for k in ("whiteink","blackink"):
    if k not in neck:
        b=base64.b64encode(open(f"shop/brand/neck_{k}.png","rb").read()).decode()
        neck[k]=call("POST","/v1/uploads/images.json",{"file_name":f"alphadog_neck_{k}.png","contents":b})["id"]
json.dump(neck,open("out/neck_ids.json","w"))
ink={v:k.split("_")[-1] for k,v in up.items()}
page=1;done=skipped=failed=0
while True:
    r=call("GET",f"/v1/shops/{SHOP}/products.json?limit=50&page={page}")
    for p in r["data"]:
        if done>=LIMIT: break
        areas=p["print_areas"]
        if any(ph["position"]=="neck" for a in areas for ph in a["placeholders"]): skipped+=1; continue
        if p["title"].startswith("NECK LABEL TEST") or p["title"].startswith("PILOT"): skipped+=1; continue
        new=[]; ok=True
        for a in areas:
            inks={ink.get(im["id"]) for ph in a["placeholders"] for im in ph["images"]}-{None}
            if len(inks)!=1: ok=False; break
            i=inks.pop()
            ph=[{"position":q["position"],"images":[{k:v for k,v in im.items() if k in("id","x","y","scale","angle")} for im in q["images"]]} for q in a["placeholders"]]
            ph.append({"position":"neck","images":[{"id":neck[i],"x":0.5,"y":0.5,"scale":1.0,"angle":0}]})
            new.append({"variant_ids":a["variant_ids"],"placeholders":ph})
        if not ok: failed+=1; print("SKIP (ink unknown)",p["id"],flush=True); continue
        try: call("PUT",f"/v1/shops/{SHOP}/products/{p['id']}.json",{"print_areas":new}); done+=1
        except Exception: failed+=1
        if done%50==0: print("done",done,flush=True)
        time.sleep(0.3)
    if page>=r.get("last_page",1) or done>=LIMIT: break
    page+=1
print("FINISHED done",done,"skipped",skipped,"failed",failed,flush=True)

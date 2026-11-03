"""Swap every existing neck label (logo-only) to v3: logo + 'AlphaDog Styles' (Quicksand), all shops."""
import os,json,base64,urllib.request,urllib.error,time
T=os.environ["PRINTIFY_TOKEN"].strip();LIMIT=int(os.environ.get("LIMIT","100000"));DRY=os.environ.get("DRY")=="1"
def call(m,p,b=None,retry=9):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:400]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep(20*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
old=json.load(open("out/neck_ids.json")); v3=json.load(open("out/brand_v2_ids.json"))
MAP={old["blackink"]:v3["neck_blackink_v3"],old["whiteink"]:v3["neck_whiteink_v3"]}
stats={};CACHE={}
def resolve(i):
    if i in MAP: return MAP[i]
    if i in MAP.values(): return i
    if i not in CACHE:
        try: fn=call("GET",f"/v1/uploads/{i}.json").get("file_name","")
        except Exception: fn=""
        CACHE[i]=v3["neck_whiteink_v3"] if "neck_whiteink" in fn and "v3" not in fn else v3["neck_blackink_v3"] if "neck_blackink" in fn and "v3" not in fn else None
        print("upload",i,fn,"->",CACHE[i],flush=True)
    return CACHE[i]
for s in call("GET","/v1/shops.json"):
    SHOP=s["id"]; st=stats.setdefault(f'{SHOP} {s.get("title")} {s.get("sales_channel")}',{"swapped":0,"already":0,"noneck":0,"other":0,"failed":0})
    page=1
    while True:
        r=call("GET",f"/v1/shops/{SHOP}/products.json?limit=50&page={page}")
        for p in r["data"]:
            if sum(v["swapped"] for v in stats.values())>=LIMIT: break
            ids=[im["id"] for a in p["print_areas"] for ph in a["placeholders"] if ph["position"]=="neck" for im in ph["images"]]
            if not ids: st["noneck"]+=1; continue
            todo=[i for i in ids if resolve(i) and resolve(i)!=i]
            if not todo:
                if any(resolve(i)==i for i in ids): st["already"]+=1
                else: st["other"]+=1; print("no brand neck image",SHOP,p["id"],ids,flush=True)
                continue
            new=[{"variant_ids":a["variant_ids"],"placeholders":[{"position":q["position"],"images":[{**{k:v for k,v in im.items() if k in("id","x","y","scale","angle")},**({"id":resolve(im["id"])} if q["position"]=="neck" and resolve(im["id"]) else {})} for im in q["images"]]} for q in a["placeholders"] if q["images"]]} for a in p["print_areas"]]
            if DRY: st["swapped"]+=1; continue
            try: call("PUT",f"/v1/shops/{SHOP}/products/{p['id']}.json",{"print_areas":new}); st["swapped"]+=1
            except Exception: st["failed"]+=1
            time.sleep(0.3)
        if page>=r.get("last_page",1): break
        page+=1
    print(json.dumps(stats),flush=True)
json.dump(stats,open("out/neckv3_result.json","w"),indent=1); print("FINISHED",json.dumps(stats,indent=1))

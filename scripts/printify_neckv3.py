"""Swap every existing neck label (logo-only) to v3: logo + 'AlphaDog Styles' (Quicksand), all shops."""
import os,json,base64,urllib.request,urllib.error,time
T=os.environ["PRINTIFY_TOKEN"].strip();LIMIT=int(os.environ.get("LIMIT","100000"));DRY=os.environ.get("DRY")=="1"
def call(m,p,b=None,retry=4):
    for a in range(retry):
        d=json.dumps(b).encode() if b is not None else None
        r=urllib.request.Request("https://api.printify.com"+p,data=d,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json","User-Agent":"a"})
        try: return json.load(urllib.request.urlopen(r,timeout=120))
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:400]
            if e.code in (429,500,502,503,504) and a<retry-1: time.sleep(8*(a+1)); continue
            print("HTTP",e.code,p,msg,flush=True); raise
old=json.load(open("out/neck_ids.json")); v3=json.load(open("out/brand_v2_ids.json"))
MAP={old["blackink"]:v3["neck_blackink_v3"],old["whiteink"]:v3["neck_whiteink_v3"]}
stats={}
for s in call("GET","/v1/shops.json"):
    SHOP=s["id"]; st=stats.setdefault(f'{SHOP} {s.get("title")} {s.get("sales_channel")}',{"swapped":0,"already":0,"noneck":0,"other":0,"failed":0})
    page=1
    while True:
        r=call("GET",f"/v1/shops/{SHOP}/products.json?limit=50&page={page}")
        for p in r["data"]:
            if sum(v["swapped"] for v in stats.values())>=LIMIT: break
            ids=[im["id"] for a in p["print_areas"] for ph in a["placeholders"] if ph["position"]=="neck" for im in ph["images"]]
            if not ids: st["noneck"]+=1; continue
            if all(i in MAP.values() for i in ids): st["already"]+=1; continue
            if not all(i in MAP for i in ids): st["other"]+=1; print("unknown neck image",SHOP,p["id"],flush=True); continue
            new=[{"variant_ids":a["variant_ids"],"placeholders":[{"position":q["position"],"images":[{**{k:v for k,v in im.items() if k in("id","x","y","scale","angle")},**({"id":MAP[im["id"]]} if q["position"]=="neck" else {})} for im in q["images"]]} for q in a["placeholders"] if q["images"]]} for a in p["print_areas"]]
            if DRY: st["swapped"]+=1; continue
            try: call("PUT",f"/v1/shops/{SHOP}/products/{p['id']}.json",{"print_areas":new}); st["swapped"]+=1
            except Exception: st["failed"]+=1
            time.sleep(0.3)
        if page>=r.get("last_page",1): break
        page+=1
    print(json.dumps(stats),flush=True)
json.dump(stats,open("out/neckv3_result.json","w"),indent=1); print("FINISHED",json.dumps(stats,indent=1))

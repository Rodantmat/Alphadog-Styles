import os,json,io,urllib.request,time,concurrent.futures as cf
from PIL import Image
T=os.environ["PRINTIFY_TOKEN"].strip()
def g(p):
    for a in range(4):
        try: return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
        except Exception: time.sleep(3)
up=json.load(open("out/uploads.json"))
# what's actually used: also scan current products for upload ids per key (catches later swaps like artfix)
os.makedirs("out/art_check",exist_ok=True)
keys=[k for k in up if k.endswith("_blackink")]
def job(k):
    fn="out/art_check/"+k.replace("/","__")+".png"
    u=g(f"/v1/uploads/{up[k]}.json") or {}
    try:
        im=Image.open(io.BytesIO(urllib.request.urlopen(urllib.request.Request(u["preview_url"],headers={"User-Agent":"a"}),timeout=90).read())).convert("RGBA")
        a=im.split()[3]; bb=a.getbbox()
        bg=Image.new("L",im.size,255); bg.paste(Image.new("L",im.size,0),mask=a)  # ink=black
        if bb: bg=bg.crop(bb)
        bg.thumbnail((600,600)); bg.save(fn,optimize=True); return k,"ok",u.get("width"),u.get("height")
    except Exception as e: return k,"ERR "+str(e)[:80],None,None
res=list(cf.ThreadPoolExecutor(8).map(job,keys))
json.dump(res,open("out/art_check/_index.json","w"),indent=0)
print(sum(r[1]=="ok" for r in res),"/",len(res)); [print(r) for r in res if r[1]!="ok"]
# also: which upload ids are live in products now (by position), to catch swaps
ids={}
for shop in [s["id"] for s in g("/v1/shops.json")]:
    pg=1
    while True:
        r=g(f"/v1/shops/{shop}/products.json?limit=50&page={pg}")
        for p in r["data"]:
            for a in p["print_areas"]:
                for ph in a["placeholders"]:
                    for im in ph["images"]: ids.setdefault(im["id"],set()).add(ph["position"])
        if pg>=r["last_page"]: break
        pg+=1
inv={v:k for k,v in up.items()}
live=[i for i in ids if i not in inv]
json.dump({"live_ids_not_in_uploads":len(live),"total_live":len(ids)},open("out/art_check/_live.json","w"))
print("live ids",len(ids),"unknown",len(live))

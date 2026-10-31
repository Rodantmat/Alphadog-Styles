import os,json,urllib.request
T=os.environ["PRINTIFY_TOKEN"];SHOP=os.environ["SHOP"]
os.makedirs("out/mock",exist_ok=True)
for pid in os.environ["PIDS"].split(","):
    r=urllib.request.Request(f"https://api.printify.com/v1/shops/{SHOP}/products/{pid}.json",headers={"Authorization":"Bearer "+T,"User-Agent":"a"})
    p=json.load(urllib.request.urlopen(r)); seen=set(); n=0
    for im in p["images"]:
        k=(im["position"],im.get("is_default"))
        if im["position"] in seen: continue
        seen.add(im["position"])
        d=urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"})).read()
        open(f"out/mock/{pid}_{im['position']}.jpg","wb").write(d)
    # also a dark variant mockup
    dark=[im for im in p["images"] if im["position"]=="back"]
    if len(dark)>3:
        d=urllib.request.urlopen(urllib.request.Request(dark[-1]["src"],headers={"User-Agent":"a"})).read(); open(f"out/mock/{pid}_back_last.jpg","wb").write(d)
        fr=[im for im in p["images"] if im["position"]=="front"][-1]
        d=urllib.request.urlopen(urllib.request.Request(fr["src"],headers={"User-Agent":"a"})).read(); open(f"out/mock/{pid}_front_last.jpg","wb").write(d)

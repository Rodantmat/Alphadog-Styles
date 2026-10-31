import os,json,urllib.request
T=os.environ["PRINTIFY_TOKEN"];SHOP=os.environ["SHOP"]
os.makedirs("out/mock2",exist_ok=True)
WANT=["Black","White","Navy","Sand","Light Blue","Forest Green","Maroon","Sport Grey"]
for pid in os.environ["PIDS"].split(","):
    r=urllib.request.Request(f"https://api.printify.com/v1/shops/{SHOP}/products/{pid}.json",headers={"Authorization":"Bearer "+T,"User-Agent":"a"})
    p=json.load(urllib.request.urlopen(r))
    col={}
    for v in p["variants"]:
        c=v["title"].split(" / ")[0]; col.setdefault(c,[]).append(v["id"])
    got=0
    for c in WANT:
        if c not in col: continue
        for pos in ("front","back"):
            for im in p["images"]:
                if im["position"]==pos and col[c][0] in im.get("variant_ids",[]):
                    d=urllib.request.urlopen(urllib.request.Request(im["src"],headers={"User-Agent":"a"})).read()
                    open(f"out/mock2/{pid}_{c.replace(' ','')}_{pos}.jpg","wb").write(d); got+=1; break
    print(pid,got)

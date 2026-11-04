import urllib.request,os,json,sys
ids=sys.argv[1].split(",");os.makedirs("out/scenery/pick",exist_ok=True)
L={x["id"]:x for x in json.load(open("out/scenery/list.json"))}
log=[]
for n,i in enumerate(ids):
    d=urllib.request.urlopen(urllib.request.Request(f"https://picsum.photos/id/{i}/1080/1920.jpg",headers={"User-Agent":"Mozilla/5.0"})).read()
    open(f"out/scenery/pick/{n:02d}_{i}.jpg","wb").write(d);log.append((i,L[i]["author"],L[i]["url"]))
json.dump(log,open("out/scenery/pick/credits.json","w"));print(log)

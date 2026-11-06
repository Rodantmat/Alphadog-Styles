import os,json,urllib.request,collections
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p): return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
pid=os.environ["PIDS"].split(",")[0]
p=call(f"/v1/shops/{os.environ['SHOP']}/products/{pid}.json")
seen=set()
for im in p["images"]:
    k=im["src"].split("?")[1] if "?" in im["src"] else im["src"]
    if im["position"]=="front" and "front" not in seen: print("FULLSRC front",im["src"]); seen.add("front")
    if im["position"]=="back" and "back" not in seen: print("FULLSRC back",im["src"]); seen.add("back")
    if "hanging" in im["src"] and "hang" not in seen: print("FULLSRC hang",im["src"]); seen.add("hang")

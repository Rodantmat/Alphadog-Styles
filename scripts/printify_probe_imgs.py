import os,json,urllib.request,urllib.error
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(m,p,b=None):
    r=urllib.request.Request("https://api.printify.com"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"User-Agent":"a","Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(r,timeout=60))
    except urllib.error.HTTPError as e: return {"ERR":e.code,"msg":e.read().decode()[:300]}
ids="6ae6caa273cf98f438066f1e 6ae6ca9f5d17aa531b00d13c 6ae6ca9cf0cc71d31d095073 6ae6ca994a39c0f86906c217 6ae6ca96f0cc71d31d09506c 6ae6ca935d17aa531b00d12a 6ae6ca8073cf98f438066eea 6ae6ca7d340a0b43b901ba36 6ae6ca7abdc68f81c20f1b66 6ae6ca785d17aa531b00d108 6ae6ca75340a0b43b901ba24 6ae6ca724a39c0f86906c1be".split()
for pid in ids:
    r=call("POST",f"/v1/shops/29546485/products/{pid}/publishing_failed.json",{"reason":"Stuck in publishing; unlock for edit"})
    p=call("GET",f"/v1/shops/29546485/products/{pid}.json")
    print("U",pid,json.dumps(r)[:150],"locked now",p.get("is_locked"))

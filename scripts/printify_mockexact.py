import os,json,re,time,hashlib,urllib.request
T=os.environ["PRINTIFY_TOKEN"].strip()
def call(p):
    return json.load(urllib.request.urlopen(urllib.request.Request("https://api.printify.com"+p,headers={"Authorization":"Bearer "+T,"User-Agent":"a"}),timeout=60))
P=json.load(open("out/mockcount_pids2.json"))
R=lambda a,b:list(range(a,b+1))
SITE={
"Hoodie":[98424,98425,98426,98427,98428,98429,98430,98432,100682,100683,100684,100685,102766,110151,111847,111848,127688,127738],
"Tee B":[92547,92578,92579,92580,92581,92582,92583,92584,92585,92720,92735,92736]+R(102044,102054)+[102057,102058,102059,102060,102061,102062,111785,111786,111787,111788],
"Tee A":[97992,97993,97994]+R(100615,100623)+[110135,127670,127673],
"Mesh Trucker Cap":[109494,109529,110007,110013,110020,110021],
"Foam Trucker Hat":[109489,110280,110281,110282,110570,127559],
"Dad Hat":[110918]+R(135042,135049)+[110858,112104,112107],
"Polo":[101910,102236,102926,103301,103302],
"Racerback Tank":[48,49,111806,111807,119048],
"Tank Top":[101889,101892,119051],
"Women's Polo":[154228,154230,154232,154234,154236,154168,154229],
}
SH=[s["id"] for s in call("/v1/shops.json")]
res={}
for prod,ids in SITE.items():
    pid=P[prod]["pid"]; p=None
    for sh in SH:
        try: p=call(f"/v1/shops/{sh}/products/{pid}.json"); break
        except Exception: pass
    var=sorted({int(re.search(r"/mockup/[^/]+/(\d+)/",im["src"]).group(1)) for im in p["images"]})[0]
    d="out/mockexact/"+prod.replace(" ","_").replace("'",""); os.makedirs(d,exist_ok=True)
    seen={}; ok=[]; bad=[]
    for i in ids:
        try: b=urllib.request.urlopen(urllib.request.Request(f"https://images.printify.com/mockup/{pid}/{var}/{i}/x.jpg?camera_label=front",headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
        except Exception as e: bad.append(i); time.sleep(.3); continue
        h=hashlib.md5(b).hexdigest()[:10]
        if len(b)<3000: bad.append(i); continue
        dup=seen.get(h); seen.setdefault(h,i)
        open(f"{d}/{i}.jpg","wb").write(b); ok.append((i,h,dup))
        time.sleep(.3)
    res[prod]=dict(var=var,ok=ok,bad=bad,distinct=len(seen))
    print(prod,"var",var,"fetched",len(ok),"distinct",len(seen),"bad",bad,"dups",[(i,d) for i,h,d in ok if d],flush=True)
json.dump(res,open("out/mockexact/result.json","w"))

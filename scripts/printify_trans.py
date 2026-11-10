import os,json,time,io,urllib.request,sys
from PIL import Image
P=json.load(open("out/mockcount_pids2.json")); R=json.load(open("out/mockexact/result.json"))
LIM=int(os.environ.get("LIM","0")); S=os.environ.get("SIZE","2048")
out="out/mocktrans"; log=[]
for prod,v in R.items():
    pid=P[prod]["pid"]; var=v["var"]; d=f"{out}/"+prod.replace(" ","_").replace("'",""); os.makedirs(d,exist_ok=True)
    ids=[i for i,h,dup in v["ok"] if not dup]
    if LIM: ids=ids[:LIM]
    for i in ids:
        u=f"https://images.printify.com/mockup/{pid}/{var}/{i}/x.png?camera_label=front&t={int(time.time()*1000)}&s={S}&transparent_background=true&use_cache=false"
        try:
            b=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
            im=Image.open(io.BytesIO(b)); a=im.getchannel("A") if im.mode=="RGBA" else None
            tr=0 if a is None else sum(1 for p in a.resize((64,64)).getdata() if p<10)/4096
            open(f"{d}/{i}.png","wb").write(b)
            msg=f"{prod} {i} {im.size} {im.mode} bytes={len(b)} transp={tr:.2f}"
        except Exception as e: msg=f"{prod} {i} FAIL {e}"
        print(msg,flush=True); time.sleep(.4)

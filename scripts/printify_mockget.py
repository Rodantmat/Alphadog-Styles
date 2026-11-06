import urllib.request,os,hashlib
pid=os.environ.get("PID","6aed2ee9e7be4e1ecd0985e1");var=os.environ.get("VAR","18102")
L=["front","back","folded","hanging-1","hanging-2","hanging-3","hanging-4","person-1","person-2","person-3","person-4","person-5","person-6","person-7","person-8","person-9","person-10","hanging-5","lifestyle","context","front-lifestyle","person"]
os.makedirs("out/mockget",exist_ok=True);seen={}
import time
for l in L:
    time.sleep(2)
    try:
        d=urllib.request.urlopen(urllib.request.Request(f"https://images.printify.com/mockup/{pid}/{var}/102044/x.jpg?camera_label={l}",headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
    except Exception as e: print("ERR",l,e); continue
    h=hashlib.md5(d).hexdigest()[:8]; print("GOT",l,len(d),h,"DUP" if h in seen else "")
    seen[h]=l; open(f"out/mockget/{l}.jpg","wb").write(d)

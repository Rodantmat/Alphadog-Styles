import urllib.request,os,hashlib,time
pid="6aed2ee9e7be4e1ecd0985e1";var="18102"
os.makedirs("out/mockget2",exist_ok=True);seen={}
for i in range(102044,102063):
    time.sleep(1.2)
    try: d=urllib.request.urlopen(urllib.request.Request(f"https://images.printify.com/mockup/{pid}/{var}/{i}/x.jpg?camera_label=front",headers={"User-Agent":"Mozilla/5.0"}),timeout=30).read()
    except Exception as e: print("ERR",i,e); continue
    h=hashlib.md5(d).hexdigest()[:8]
    if h in seen: print("DUP",i,seen[h]); continue
    seen[h]=i; print("NEW",i,len(d)); open(f"out/mockget2/{i}.jpg","wb").write(d)

"""Crawl Mixkit free stock music (license: Mixkit Free License - commercial use, no attribution) -> out/musiclib/index.json
Pages: whole catalogue pagination + every genre / mood page."""
import re,json,urllib.request,time,os
H={"User-Agent":"Mozilla/5.0"}
def get(u):
    for t in range(4):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60).read().decode("utf8","ignore")
        except Exception as e: err=e; time.sleep(3+3*t)
    return None
RX=re.compile(r'\{"@id":"([^"]+)","@type":"MusicRecording","name":"([^"]+)","genre":"([^"]*)","byArtist":"([^"]*)","duration":"([^"]*)","url":"(https://assets[^"]+)"')
tracks={}; log=[]; T0=time.time()
def scan(base,maxp=40):
    n_total=0
    for p in range(1,maxp+1):
        if time.time()-T0>1200: break
        u=base if p==1 else base.rstrip("/")+f"/?page={p}" if "?" not in base else base+f"&page={p}"
        h=get(u)
        if not h: break
        new=0
        for m in RX.finditer(h):
            _,name,genre,artist,dur,url=m.groups(); idm=re.search(r"/music/(\d+)/",url)
            if not idm: continue
            tid=idm.group(1)
            if tid not in tracks: tracks[tid]={"id":"mx"+tid,"title":name,"artist":artist,"genre":genre,"dur":dur,"url":url,"tags":[]}; new+=1
            tracks[tid]["tags"]=sorted(set(tracks[tid]["tags"]+[base.rstrip("/").split("/")[-1]]))
        n_total+=new; log.append((u,new))
        print("  ",u,new,flush=True)
        if new==0 and p>1: break
    return n_total
print("all",scan("https://mixkit.co/free-stock-music/"),len(tracks),flush=True)
home=get("https://mixkit.co/free-stock-music/") or ""
cats=sorted(set(re.findall(r'href="/free-stock-music/((?:genre|mood|tag)/[a-z0-9\-]+|[a-z0-9\-]+)/"',home)))
print("category links",len(cats),cats[:60],flush=True)
for c in cats:
    if c in("genre","mood","tag"): continue
    n=scan(f"https://mixkit.co/free-stock-music/{c}/"); print(c,n,len(tracks),flush=True)
os.makedirs("out/musiclib",exist_ok=True); json.dump(sorted(tracks.values(),key=lambda x:int(x["id"][2:])),open("out/musiclib/index.json","w"),indent=0)
print("TOTAL",len(tracks))

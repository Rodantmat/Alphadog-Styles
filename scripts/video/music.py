import re,urllib.request,os,json,subprocess
os.makedirs("out/music",exist_ok=True)
H={"User-Agent":"Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60).read()
items={}
for tag in ["happy","feel-good","summer","fun","upbeat","travel","hip-hop","pop"]:
    try: html=get(f"https://mixkit.co/free-stock-music/tag/{tag}/").decode("utf8","ignore")
    except Exception as e: print(tag,"ERR",e); continue
    for m in re.finditer(r'(https://assets\.mixkit\.co/music/[^"\' ]+?\.mp3)',html):
        u=m.group(1); ctx=html[max(0,m.start()-1500):m.start()+1500]
        t=re.search(r'data-audio-player-title-value="([^"]+)"',ctx) or re.search(r'item-grid-card__title[^>]*>\s*<a[^>]*>([^<]+)',ctx)
        items.setdefault(u,{"title":t.group(1).strip() if t else "?","tags":set()})["tags"].add(tag)
print(len(items))
L=[{"url":u,"title":v["title"],"tags":sorted(v["tags"])} for u,v in items.items()]
json.dump(L,open("out/music/list.json","w"),indent=1)
for n,x in enumerate(L[:14]):
    try:
        raw=f"/tmp/m{n}.mp3";open(raw,"wb").write(get(x["url"]))
        subprocess.run(["ffmpeg","-y","-v","error","-i",raw,"-t","75","-ac","2","-ar","44100","-b:a","128k",f"out/music/t{n:02d}.mp3"],check=True)
        x["file"]=f"t{n:02d}.mp3"
    except Exception as e: print(n,"ERR",e)
json.dump(L,open("out/music/list.json","w"),indent=1)

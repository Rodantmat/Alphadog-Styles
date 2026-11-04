import re,urllib.request,os,json
os.makedirs("out/music",exist_ok=True)
H={"User-Agent":"Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60).read()
items={}
for tag in ["happy","summer","fun","pop"]:
    html=get(f"https://mixkit.co/free-stock-music/tag/{tag}/").decode("utf8","ignore")
    for m in re.finditer(r'\{"@id":"([^"]+)","@type":"MusicRecording","name":"([^"]+)","genre":"([^"]*)","byArtist":"([^"]*)","duration":"([^"]*)","url":"(https://assets[^"]+)"',html):
        _,name,genre,artist,dur,url=m.groups()
        it=items.setdefault(url,{"title":name,"artist":artist,"genre":genre,"dur":dur,"url":url,"tags":[]});it["tags"].append(tag)
L=sorted(items.values(),key=lambda x:-len(x["tags"]))
print(len(L))
for x in L[:40]:
    print(x["title"],"|",x["artist"],"|",x["dur"],"|",x["tags"])
sel=L[:14]
for n,x in enumerate(sel):
    try: open(f"out/music/t{n:02d}.mp3","wb").write(get(x["url"]));x["file"]=f"t{n:02d}.mp3"
    except Exception as e: print("ERR",n,e)
json.dump(sel,open("out/music/list.json","w"),indent=1)

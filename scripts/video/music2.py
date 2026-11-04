import re,urllib.request,os,json,subprocess
os.makedirs("out/music2",exist_ok=True)
H={"User-Agent":"Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=90).read()
by={}
for tag in ["hip-hop","pop","upbeat","tech-house","deep-house","dance","party","funk","latin","electronic","beats","trap"]:
    try: html=get(f"https://mixkit.co/free-stock-music/tag/{tag}/").decode("utf8","ignore")
    except Exception as e:
        try: html=get(f"https://mixkit.co/free-stock-music/{tag}/").decode("utf8","ignore")
        except Exception as e2: print(tag,"ERR",e2); continue
    n=0
    for m in re.finditer(r'\{"@id":"([^"]+)","@type":"MusicRecording","name":"([^"]+)","genre":"([^"]*)","byArtist":"([^"]*)","duration":"([^"]*)","url":"(https://assets[^"]+)"',html):
        _,name,genre,artist,dur,url=m.groups(); by.setdefault(tag,[]).append({"title":name,"artist":artist,"genre":genre,"dur":dur,"url":url,"tag":tag}); n+=1
    print(tag,n)
sel=[];seen=set();i=0
while len(sel)<30 and any(len(v)>i for v in by.values()):
    for t,v in by.items():
        if len(v)>i and v[i]["url"] not in seen and len(sel)<30: seen.add(v[i]["url"]);sel.append(v[i])
    i+=1
for n,x in enumerate(sel):
    try:
        raw=f"/tmp/r{n}.mp3";open(raw,"wb").write(get(x["url"]))
        subprocess.run(["ffmpeg","-y","-v","error","-ss","12","-t","60","-i",raw,"-ac","1","-b:a","96k",f"out/music2/m{n:02d}.mp3"],check=True,capture_output=True)
        x["file"]=f"m{n:02d}.mp3"
    except Exception as e: print("ERR",n,repr(e)); x["err"]=repr(e)
    print(n,x["tag"],x["title"],"|",x["artist"],"|",x["dur"])
json.dump(sel,open("out/music2/list.json","w"),indent=1)

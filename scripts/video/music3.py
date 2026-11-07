# Adds NEW Mixkit tracks (never overwrites): scans several pages per tag, skips urls already in list.json, appends m<N>.mp3
import re,urllib.request,os,json,subprocess,sys
N_NEW=int(sys.argv[1]) if len(sys.argv)>1 else 60
D="out/music2";L=D+"/list.json";lst=json.load(open(L));have={x["url"] for x in lst}
H={"User-Agent":"Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=90).read()
cand=[]
tags=["hip-hop","pop","upbeat","tech-house","deep-house","dance","party","funk","latin","electronic","beats","trap","summer","happy","chill","lo-fi","rock","reggae","disco","fun"]
pat=r'\{"@id":"([^"]+)","@type":"MusicRecording","name":"([^"]+)","genre":"([^"]*)","byArtist":"([^"]*)","duration":"([^"]*)","url":"(https://assets[^"]+)"'
for tag in tags:
  for pg in (1,2,3,4):
    u=f"https://mixkit.co/free-stock-music/tag/{tag}/"+("" if pg==1 else f"page/{pg}/")
    try: html=get(u).decode("utf8","ignore")
    except Exception as e: print(tag,pg,"ERR",e); break
    n=0
    for m in re.finditer(pat,html):
      _,name,genre,artist,dur,url=m.groups()
      if url in have or any(c["url"]==url for c in cand): continue
      cand.append({"title":name,"artist":artist,"genre":genre,"dur":dur,"url":url,"tag":tag});n+=1
    print(tag,pg,n)
    if n==0: break
nxt=len(lst);added=0
for x in cand:
  if added>=N_NEW: break
  try:
    raw="/tmp/r.mp3";open(raw,"wb").write(get(x["url"]))
    f=f"m{nxt:02d}.mp3"
    subprocess.run(["ffmpeg","-y","-v","error","-ss","12","-t","60","-i",raw,"-ac","1","-b:a","96k",f"{D}/{f}"],check=True,capture_output=True)
    x["file"]=f;lst.append(x);nxt+=1;added+=1;print("ADD",f,x["title"],"|",x["artist"])
  except Exception as e: print("ERR",x["title"],repr(e))
json.dump(lst,open(L,"w"),indent=1);print("added",added,"total",len(lst))

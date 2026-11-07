# Grow out/music2 to TARGET tracks (default 300) from Mixkit (free commercial licence, no attribution), themed + energy-filtered.
import re,urllib.request,os,json,subprocess,sys,collections
TARGET=int(sys.argv[1]) if len(sys.argv)>1 else 300
D="out/music2";L=D+"/list.json";lst=json.load(open(L));have={x["url"] for x in lst}
H={"User-Agent":"Mozilla/5.0"}
def get(u): return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=90).read()
THEME={"hip-hop":"Hip-hop & Trap","trap":"Hip-hop & Trap","beats":"Hip-hop & Trap","rap":"Hip-hop & Trap","r-b":"Hip-hop & Trap",
"pop":"Pop & Party","dance":"Pop & Party","party":"Pop & Party","disco":"Funk & Disco","funk":"Funk & Disco",
"electronic":"Electronic & House","tech-house":"Electronic & House","deep-house":"Electronic & House","house":"Electronic & House","edm":"Electronic & House","techno":"Electronic & House",
"latin":"Latin & Reggae","reggae":"Latin & Reggae","summer":"Feel-good","happy":"Feel-good","fun":"Feel-good","upbeat":"Feel-good","uplifting":"Feel-good",
"rock":"Rock & Guitar","guitar":"Rock & Guitar","chill":"Chill & Lo-fi","lo-fi":"Chill & Lo-fi"}
BAD=("sleep","ambient","meditation","horror","sad","cinematic","classical","piano","dark","documentary","relax","spa","drone")
pat=r'\{"@id":"([^"]+)","@type":"MusicRecording","name":"([^"]+)","genre":"([^"]*)","byArtist":"([^"]*)","duration":"([^"]*)","url":"(https://assets[^"]+)"'
tags=list(THEME)
try:
  idx=get("https://mixkit.co/free-stock-music/").decode("utf8","ignore")
  for t in re.findall(r'/free-stock-music/(?:tag/)?([a-z0-9-]+)/',idx):
    if t not in tags and t not in ("tag","page") and not any(b in t for b in BAD): tags.append(t)
except Exception as e: print("index ERR",e)
print("tags",tags)
cand=[];seen=set(have)
for tag in tags:
  th=THEME.get(tag,"Feel-good")
  for pg in range(1,9):
    got=0
    for u in ([f"https://mixkit.co/free-stock-music/tag/{tag}/?page={pg}",f"https://mixkit.co/free-stock-music/{tag}/?page={pg}"] if pg>1 else [f"https://mixkit.co/free-stock-music/tag/{tag}/",f"https://mixkit.co/free-stock-music/{tag}/"]):
      try: html=get(u).decode("utf8","ignore")
      except Exception as e: continue
      for m in re.finditer(pat,html):
        _,name,genre,artist,dur,url=m.groups()
        if url in seen or any(b in (genre+name).lower() for b in BAD): continue
        seen.add(url);cand.append({"title":name,"artist":artist,"genre":genre,"dur":dur,"url":url,"tag":tag,"theme":th});got+=1
      if html: break
    print(tag,pg,got)
    if got==0: break
print("candidates",len(cand))
for x in lst:
  x.setdefault("theme",THEME.get(x.get("tag"),"Feel-good"))
# energy filter with librosa
import numpy as np
try:
  import librosa
except Exception: librosa=None
def score(path):
  if not librosa: return 1.0,0
  y,sr=librosa.load(path,sr=22050,mono=True,duration=45)
  tempo,_=librosa.beat.beat_track(y=y,sr=sr);tempo=float(np.atleast_1d(tempo)[0])
  on=float(librosa.onset.onset_strength(y=y,sr=sr).mean());rms=float(librosa.feature.rms(y=y).mean())
  return on*rms*100,tempo
nxt=len(lst);pool=[]
for x in cand:
  if len(lst)+len(pool)>=TARGET*1.6: break
  try:
    raw="/tmp/r.mp3";open(raw,"wb").write(get(x["url"]))
    f=f"m{nxt+len(pool):03d}.mp3"
    subprocess.run(["ffmpeg","-y","-v","error","-ss","10","-t","60","-i",raw,"-ac","1","-b:a","80k",f"{D}/{f}"],check=True,capture_output=True)
    s,bpm=score(f"{D}/{f}");x["file"]=f;x["energy"]=round(s,3);x["bpm"]=round(bpm);pool.append(x)
  except Exception as e: print("ERR",x["title"],repr(e))
pool.sort(key=lambda x:-x["energy"])
need=TARGET-len(lst);keep=[x for x in pool if x["bpm"]>=88 or x["theme"]=="Hip-hop & Trap"]
# balance themes
by=collections.defaultdict(list)
for x in keep: by[x["theme"]].append(x)
sel=[];i=0
while len(sel)<need and any(len(v)>i for v in by.values()):
  for t,v in by.items():
    if len(v)>i and len(sel)<need: sel.append(v[i])
  i+=1
keepf={x["file"] for x in sel}
for x in pool:
  if x["file"] not in keepf: os.remove(f"{D}/{x['file']}")
# renumber selected contiguous after existing
for k,x in enumerate(sel):
  new=f"m{len(lst)+k:03d}.mp3"
  if x["file"]!=new: os.rename(f"{D}/{x['file']}",f"{D}/{new}")
  x["file"]=new
lst+=sel
json.dump(lst,open(L,"w"),indent=1)
print("total",len(lst),collections.Counter(x["theme"] for x in lst))

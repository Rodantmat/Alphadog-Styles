"""Download candidate free clips, make contact sheets (committed to out/video_proto/) + pose stats."""
import os,sys,subprocess,json,urllib.request
os.makedirs("out/video_proto/src",exist_ok=True)
IDS=[87,86,49337,36996,16119,43153]
def get(i):
    for res in ("1080","720","360"):
        u=f"https://assets.mixkit.co/videos/{i}/{i}-{res}.mp4"
        p=f"out/video_proto/src/{i}.mp4"
        try:
            req=urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"})
            open(p,"wb").write(urllib.request.urlopen(req,timeout=90).read()); return p,res
        except Exception as e: print("fail",u,str(e)[:60])
    return None,None
for i in IDS:
    p,res=get(i)
    if not p: continue
    pr=json.loads(subprocess.check_output(["ffprobe","-v","error","-select_streams","v:0","-show_entries","stream=width,height,r_frame_rate,duration","-of","json",p]))["streams"][0]
    print(i,res,pr,os.path.getsize(p)//1024,"KB")
    subprocess.run(["ffmpeg","-y","-v","error","-i",p,"-vf","fps=1/1.5,scale=240:-2,tile=6x1","-frames:v","1",f"out/video_proto/sheet_{i}.jpg"])

"""Scrape free Mixkit clips, rank by 'person seen from behind, centered, torso visible', commit top contact sheets."""
import os,re,json,urllib.request,urllib.error,cv2,numpy as np
import mediapipe as mp
os.makedirs("out/video_scan/sheets",exist_ok=True); os.makedirs("/tmp/clips",exist_ok=True)
UA={"User-Agent":"Mozilla/5.0"}
def get(u,to=60):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=to).read()
cats=["hiking","cycling","walking","running","beach","city","mountains","travel","street","forest","nature","lifestyle","sunset","skateboarding","park"]
ids={}
for c in cats:
    for pg in (1,2,3):
        try: h=get(f"https://mixkit.co/free-stock-video/{c}/?page={pg}").decode("utf8","ignore")
        except Exception as e: break
        for m in re.finditer(r"assets\.mixkit\.co/videos/(\d+)/\1-(?:360|720|1080)\.mp4",h): ids.setdefault(int(m.group(1)),c)
print("candidates",len(ids))
pose=mp.solutions.pose.Pose(static_image_mode=True,model_complexity=1,min_detection_confidence=0.5)
res=[]
for n,(i,c) in enumerate(sorted(ids.items())[:220]):
    p=f"/tmp/clips/{i}.mp4"
    try: open(p,"wb").write(get(f"https://assets.mixkit.co/videos/{i}/{i}-360.mp4"))
    except Exception as e: continue
    cap=cv2.VideoCapture(p); N=int(cap.get(7)); W=cap.get(3); H=cap.get(4)
    if N<30: continue
    sc=[];fr=[]
    for k in range(8):
        cap.set(1,int(N*(k+.5)/8)); ok,f=cap.read()
        if not ok: continue
        fr.append(f); r=pose.process(cv2.cvtColor(f,cv2.COLOR_BGR2RGB))
        if not r.pose_landmarks: sc.append(0); continue
        L=r.pose_landmarks.landmark
        vis=min(L[11].visibility,L[12].visibility,L[23].visibility,L[24].visibility)
        face=np.mean([L[j].visibility for j in (0,2,5,7,8)])  # nose/eyes/ears: low when seen from behind
        span=abs(L[11].x-L[12].x); cx=(L[11].x+L[12].x)/2
        s=(vis>0.6)*(1-face)*min(span/0.18,1)*(1-min(abs(cx-.5)/.5,1))
        sc.append(float(s))
    sc=float(np.mean(sc)) if sc else 0
    res.append((sc,i,c,int(W),int(H),N/ (cap.get(5) or 25)))
    if len(res)%20==0: print(len(res),"scanned")
res.sort(reverse=True)
json.dump(res,open("out/video_scan/ranked.json","w"))
for sc,i,c,W,H,d in res[:16]:
    print(f"{sc:.2f} id={i} cat={c} {W}x{H} {d:.1f}s")
    cap=cv2.VideoCapture(f"/tmp/clips/{i}.mp4"); N=int(cap.get(7)); t=[]
    for k in range(6):
        cap.set(1,int(N*(k+.5)/6)); ok,f=cap.read()
        if ok: t.append(cv2.resize(f,(200,int(200*H/W))))
    if t: cv2.imwrite(f"out/video_scan/sheets/{sc:.2f}_{i}.jpg",np.hstack(t))

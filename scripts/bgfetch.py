#!/usr/bin/env python3
"""Real-photo backgrounds, no login, no API key, commercially free (Poly Haven = CC0). Runs ONLY in GitHub Actions (sandbox has no general internet).
 HDRIs (real 360 photos of outdoor/studio/urban/nature places, no people) -> rectilinear 1080x1920 views (like a real camera, not a raw panorama crop)
 Textures (marble/concrete/wood/fabric/plaster...) -> portrait crops of the 4k diffuse photo.
usage: bgfetch.py OUTDIR HDR_N TEX_N VIEWS"""
import sys,os,json,io,random,urllib.request,math,time
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
H={"User-Agent":"AlphaDogStyles-bg/1.0 (alphadogstyles.com)"}
def get(u,tries=3):
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=120).read()
        except Exception as e:
            err=e; time.sleep(2*(i+1))
    raise err
def J(u): return json.loads(get(u))
def view(eq,yaw,pitch,hfov,W=1080,Hh=1920):
    h,w=eq.shape[:2]; f=(W/2)/math.tan(math.radians(hfov)/2)
    x,y=np.meshgrid(np.arange(W)-W/2,np.arange(Hh)-Hh/2); z=np.full_like(x,f,dtype="float32")
    x=x.astype("float32"); y=y.astype("float32"); n=np.sqrt(x*x+y*y+z*z); x/=n; y/=n; z/=n
    p=math.radians(pitch); y2=y*math.cos(p)-z*math.sin(p); z2=y*math.sin(p)+z*math.cos(p)
    lon=np.arctan2(x,z2)+math.radians(yaw); lat=np.arcsin(np.clip(y2,-1,1))
    mx=((lon/(2*math.pi)+.5)%1.0)*w; my=(lat/math.pi+.5)*h
    return cv2.remap(eq,mx.astype("float32"),my.astype("float32"),cv2.INTER_CUBIC,borderMode=cv2.BORDER_WRAP)
def stats(img):
    a=np.asarray(img.convert("L"),"float32"); return round(float(a.mean()),1),round(float(a[500:1500,250:830].mean()),1),round(float(a[500:1500,250:830].std()),1)
def save(img,out,name,meta,cat):
    img.save(f"{out}/{name}.jpg",quality=88); m,c,s=stats(img); cat.append(dict(file=name+".jpg",mean_lum=m,centre_lum=c,centre_std=s,**meta))
def main():
    out=sys.argv[1]; hn=int(sys.argv[2]); tn=int(sys.argv[3]); nv=int(sys.argv[4]); os.makedirs(out,exist_ok=True); cat=[]; rnd=random.Random(5)
    A=J("https://api.polyhaven.com/assets?t=hdris"); print("hdri assets",len(A))
    ids=sorted(A); rnd.shuffle(ids); done=0
    for i in ids:
        if done>=hn: break
        try:
            F=J(f"https://api.polyhaven.com/files/{i}"); u=F["tonemapped"]["url"]
            im=Image.open(io.BytesIO(get(u))).convert("RGB"); im=im.resize((4096,2048),Image.LANCZOS); eq=np.asarray(im)
            for k in range(nv):
                yaw=rnd.uniform(0,360); pitch=rnd.uniform(-6,10); hf=rnd.uniform(58,78)
                v=Image.fromarray(view(eq,yaw,pitch,hf)); save(v,out,f"pg_{i}_{k}",dict(kind="hdri",src=i,name=A[i].get("name"),cats=A[i].get("categories"),tags=A[i].get("tags"),license="CC0 Poly Haven",yaw=round(yaw),pitch=round(pitch,1),hfov=round(hf)),cat)
            done+=1; print("ok hdri",i,done)
        except Exception as e: print("FAIL hdri",i,repr(e)[:120])
    T=J("https://api.polyhaven.com/assets?t=textures"); print("texture assets",len(T)); ids=sorted(T); rnd.shuffle(ids); done=0
    for i in ids:
        if done>=tn: break
        try:
            F=J(f"https://api.polyhaven.com/files/{i}"); d=F["Diffuse"]; res="4k" if "4k" in d else sorted(d)[-1]; u=d[res]["jpg"]["url"]
            im=Image.open(io.BytesIO(get(u))).convert("RGB"); w,h=im.size
            if h>=w*0.9:   # square-ish: portrait crop
                cw=int(h*9/16); x0=rnd.randint(0,max(0,w-cw)); im=im.crop((x0,0,x0+cw,h))
            else: cw=int(h*9/16); im=im.crop(((w-cw)//2,0,(w-cw)//2+cw,h))
            im=im.resize((1080,1920),Image.LANCZOS); save(im,out,f"pt_{i}",dict(kind="texture",src=i,name=T[i].get("name"),cats=T[i].get("categories"),tags=T[i].get("tags"),license="CC0 Poly Haven"),cat)
            done+=1; print("ok tex",i,done)
        except Exception as e: print("FAIL tex",i,repr(e)[:120])
    json.dump(cat,open(f"{out}/catalog.json","w"),indent=0); print("TOTAL",len(cat))
if __name__=="__main__": main()

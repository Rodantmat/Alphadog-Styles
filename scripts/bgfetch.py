#!/usr/bin/env python3
"""Real-photo backgrounds library builder. Runs ONLY in GitHub Actions (no general internet in the sandbox). Sources (all CC0, no login/key):
 - Poly Haven HDRIs (997 real 360 photos, no people) -> several rectilinear 1080x1920 camera views each
 - Poly Haven textures (869) and ambientCG materials (CC0) -> portrait crops
Every image gets a feature record (luminance, centre busyness, hue/sat/warmth, sky fraction, scene tags, usable-for flags) -> catalog shard json.
usage: bgfetch.py OUTDIR SHARD NSHARDS VIEWS [HDRI_MAX] [TEX_MAX] [AMB_MAX]"""
import sys,os,json,io,random,urllib.request,math,time,zipfile,colorsys
from concurrent.futures import ThreadPoolExecutor
import numpy as np, cv2
from PIL import Image
Image.MAX_IMAGE_PIXELS=None
H={"User-Agent":"AlphaDogStyles-bg/1.0 (alphadogstyles.com)"}
BLOCK=("hospital","factory","warehouse","garage","sewer","toilet","bathroom","prison","parking","workshop","industrial","boiler","tunnel","dirty","grunge","gore","blood","urine","cell","clinic","morgue","server","cabinet")
def get(u,tries=3):
    err=None
    for i in range(tries):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=180).read()
        except Exception as e: err=e; time.sleep(2*(i+1))
    raise err
def J(u): return json.loads(get(u))
def view(eq,yaw,pitch,hfov,W=1080,Hh=1920):
    h,w=eq.shape[:2]; f=(W/2)/math.tan(math.radians(hfov)/2)
    x,y=np.meshgrid(np.arange(W)-W/2,np.arange(Hh)-Hh/2); x=x.astype("float32"); y=y.astype("float32"); z=np.full_like(x,f)
    n=np.sqrt(x*x+y*y+z*z); x/=n; y/=n; z/=n; p=math.radians(pitch); y2=y*math.cos(p)-z*math.sin(p); z2=y*math.sin(p)+z*math.cos(p)
    lon=np.arctan2(x,z2)+math.radians(yaw); lat=np.arcsin(np.clip(y2,-1,1))
    return cv2.remap(eq,(((lon/(2*math.pi)+.5)%1.0)*w).astype("float32"),((lat/math.pi+.5)*h).astype("float32"),cv2.INTER_CUBIC,borderMode=cv2.BORDER_WRAP)
def feats(img):
    a=np.asarray(img.convert("RGB"),"float32"); g=a.mean(axis=2); c=a[480:1500,220:860]; cg=g[480:1500,220:860]
    lap=cv2.Laplacian(cg.astype("float32"),cv2.CV_32F); r,gg,b=[c[:,:,i].mean() for i in range(3)]; hh,ss,vv=colorsys.rgb_to_hsv(r/255,gg/255,b/255)
    top=a[:560]; sky=float(((top[:,:,2]>top[:,:,0]+12)&(top[:,:,2]>110)).mean())
    return dict(mean_lum=round(float(g.mean()),1),centre_lum=round(float(cg.mean()),1),centre_std=round(float(cg.std()),1),busy=round(float(np.abs(lap).mean()),2),hue=round(hh*360),sat=round(ss,2),warm=round(float((r-b)/255),2),sky=round(sky,2),
      lum_top=round(float(g[:480].mean()),1),lum_bot=round(float(g[1440:].mean()),1))
def flags(m,kind,cats,tags,name):
    t=" ".join((cats or [])+(tags or [])+[name or ""]).lower()
    ok=not any(w in t for w in BLOCK)
    people= ok and m["centre_std"]<=58 and m["busy"]<=7 and kind in("hdri","texture")
    flat= ok and m["busy"]<=3.2 and m["centre_std"]<=32
    return dict(ok=ok,people_ok=people,flat_ok=flat,dark=m["centre_lum"]<95,light=m["centre_lum"]>170)
def save(img,out,name,meta,cat):
    img.save(f"{out}/{name}.jpg",quality=86); m=feats(img); cat.append(dict(file=name+".jpg",**m,**flags(m,meta["kind"],meta.get("cats"),meta.get("tags"),meta.get("name")),**meta))
def do_hdri(i,A,out,nv,rnd_seed):
    rnd=random.Random(rnd_seed); cat=[]
    F=J(f"https://api.polyhaven.com/files/{i}"); u=F["tonemapped"]["url"]
    im=Image.open(io.BytesIO(get(u))).convert("RGB").resize((4096,2048),Image.LANCZOS); eq=np.asarray(im)
    for k in range(nv):
        yaw=(360/nv)*k+rnd.uniform(-25,25); pitch=rnd.uniform(0,14); hf=rnd.uniform(56,76)
        save(Image.fromarray(view(eq,yaw,pitch,hf)),out,f"pg_{i}_{k}",dict(kind="hdri",src=i,name=A[i].get("name"),cats=A[i].get("categories"),tags=A[i].get("tags"),license="CC0 Poly Haven",yaw=round(yaw),pitch=round(pitch,1),hfov=round(hf)),cat)
    return cat
def portrait(im,rnd,k=0):
    w,h=im.size; cw=int(h*9/16)
    if cw>w: im=im.resize((int(w*1920/ (w*16/9) ),h)) ; return im.resize((1080,1920))
    x0=rnd.randint(0,max(0,w-cw)); return im.crop((x0,0,x0+cw,h)).resize((1080,1920),Image.LANCZOS)
def do_tex(i,T,out,rnd_seed):
    rnd=random.Random(rnd_seed); cat=[]; F=J(f"https://api.polyhaven.com/files/{i}"); d=F["Diffuse"]; res="4k" if "4k" in d else sorted(d)[-1]
    im=Image.open(io.BytesIO(get(d[res]["jpg"]["url"]))).convert("RGB")
    for k in range(2):
        save(portrait(im,rnd,k),out,f"pt_{i}_{k}",dict(kind="texture",src=i,name=T[i].get("name"),cats=T[i].get("categories"),tags=T[i].get("tags"),license="CC0 Poly Haven"),cat)
    return cat
def do_amb(a,out,rnd_seed):
    rnd=random.Random(rnd_seed); cat=[]; aid=a["assetId"]; dl=a["downloadFolders"]["default"]["downloadFiletypeCategories"]["zip"]["downloads"]
    pick=[x for x in dl if x.get("attribute")=="2K-JPG"] or [x for x in dl if "JPG" in x.get("attribute","")]
    z=zipfile.ZipFile(io.BytesIO(get(pick[0]["downloadLink"]))); n=[x for x in z.namelist() if x.lower().endswith("color.jpg")][0]
    im=Image.open(io.BytesIO(z.read(n))).convert("RGB")
    tags=[t for t in a.get("tags",[])]; 
    save(portrait(im,rnd),out,f"pa_{aid}",dict(kind="texture",src=aid,name=a.get("displayName") or aid,cats=[a.get("displayCategory","")],tags=tags,license="CC0 ambientCG"),cat); return cat
def main():
    out,sh,ns,nv=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]); hm=int(sys.argv[5]) if len(sys.argv)>5 else 9999; tm=int(sys.argv[6]) if len(sys.argv)>6 else 9999; am=int(sys.argv[7]) if len(sys.argv)>7 else 0
    os.makedirs(out,exist_ok=True); cat=[]; jobs=[]
    A=J("https://api.polyhaven.com/assets?t=hdris"); T=J("https://api.polyhaven.com/assets?t=textures"); print("hdri",len(A),"tex",len(T))
    ids=[i for n,i in enumerate(sorted(A)[:hm]) if n%ns==sh]; tids=[i for n,i in enumerate(sorted(T)[:tm]) if n%ns==sh]
    amb=[]
    if am:
        try:
            for off in range(0,am*3,100):
                r=J(f"https://ambientcg.com/api/v2/full_json?type=Material&include=downloadData,tagData,displayData&limit=100&offset={off}&sort=Popular")
                amb+=r.get("foundAssets",[])
            amb=[a for n,a in enumerate(amb[:am]) if n%ns==sh]; print("ambientcg",len(amb))
        except Exception as e: print("AMB list fail",repr(e)[:150])
    def run(fn,*a):
        try: return fn(*a)
        except Exception as e: print("FAIL",fn.__name__,a[0] if not isinstance(a[0],dict) else a[0].get("assetId"),repr(e)[:120]); return []
    with ThreadPoolExecutor(6) as ex:
        fs=[ex.submit(run,do_hdri,i,A,out,nv,hash(i)%100000) for i in ids]+[ex.submit(run,do_tex,i,T,out,hash(i)%100000) for i in tids]+[ex.submit(run,do_amb,a,out,hash(a["assetId"])%100000) for a in amb]
        for n,f in enumerate(fs):
            cat+=f.result()
            if n%20==0: print("done",n,"/",len(fs),len(cat),flush=True)
    json.dump(cat,open(f"{out}/catalog_{sh}.json","w")); print("TOTAL",len(cat))
if __name__=="__main__": main()

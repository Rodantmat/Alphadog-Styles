import sys,os,glob,json,numpy as np,cv2
from rembg import remove,new_session
from PIL import Image
s=new_session("isnet-general-use")
DETAIL={("Tee_B",92736)}
def cutout(f,p,i,force_white=False):
    im=Image.open(f).convert("RGB"); a=np.asarray(im)
    h,w=a.shape[:2]
    if (p,i) in DETAIL: return im,np.ones((h,w),np.float32),"detail-no-bg"
    ai=np.asarray(remove(im,session=s,post_process_mask=True))[...,3].astype(np.float32)/255
    border=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
    if (border.min(axis=1)>=250).mean()<0.5 and not force_white: return im,ai,"scene-isnet"
    def run(th,enc=0.25):
        near=(a.min(axis=2)>=th).astype(np.uint8)
        n,lab,st,_=cv2.connectedComponentsWithStats(near,connectivity=4)
        edge=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]); edge.discard(0)
        bg=np.zeros(n,bool)
        for c in range(1,n):
            if c in edge: bg[c]=True
            elif st[c,4]>=300 and (enc is not None and ai[lab==c].mean()<enc): bg[c]=True
        return (~bg[lab]).astype(np.uint8)
    p0=run(250).astype(bool)
    med=np.median(a.min(axis=2)[p0&(ai>0.5)]) if (p0&(ai>0.5)).any() else 255
    capsprod=p in ('Mesh_Trucker_Cap','Foam_Trucker_Hat')
    th=205 if p=='Dad_Hat' else 226
    if med<215 and not capsprod:
        prod=cv2.erode(run(th,0.6),np.ones((5,5),np.uint8)).astype(np.float32)
        prod=cv2.GaussianBlur(prod,(0,0),0.8); kind="white-bg-floodfill(mid/dark)"
    else:
        prod=cv2.erode(run(250,None),np.ones((3,3),np.uint8)).astype(np.float32)
        near_ai=cv2.dilate((ai>0.3).astype(np.uint8),cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41))).astype(np.float32)
        prod=cv2.GaussianBlur(prod*near_ai,(0,0),0.7); kind="white-bg-floodfill(light)"
    m=(prod>0.5).astype(np.uint8); n,l,stt,_=cv2.connectedComponentsWithStats(m,connectivity=8)
    keep=np.zeros(n,bool)
    if n>1: keep[1:]=stt[1:,4]>=0.02*stt[1:,4].max()
    return im,prod*keep[l],kind
if __name__=="__main__":
    rep={}
    for d in sorted(glob.glob("out/mockexact/*/")):
        p=os.path.basename(d[:-1])
        if p=="Womens_Polo": continue
        o=f"out/cutouts/{p}"; os.makedirs(o,exist_ok=True)
        for f in sorted(glob.glob(d+"*.jpg")):
            i=int(os.path.basename(f)[:-4])
            if not os.path.exists(f"{o}/{i}.png"): continue
            fw=(p,i) in {("Hoodie",100685),("Tee_B",92735),("Tee_A",97994)}
            im,al,kind=cutout(f,p,i,fw)
            m=al>0.02; ys,xs=np.where(m)
            r=Image.fromarray(np.dstack([np.asarray(im),(al*255).astype(np.uint8)]),"RGBA")
            pad=6; r=r.crop((max(0,xs.min()-pad),max(0,ys.min()-pad),min(r.width,xs.max()+pad),min(r.height,ys.max()+pad)))
            r.save(f"{o}/{i}.png"); rep[f"{p}/{i}"]=dict(kind=kind,size=r.size); print(p,i,kind,flush=True)
    json.dump(rep,open("out/cutouts/report.json","w"))

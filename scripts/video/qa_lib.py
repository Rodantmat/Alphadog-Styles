# QA for the merch cutout library: composite on black, flag white halo / lost pieces. usage: qa_lib.py -> out/merch_lib/qa.json + contact sheets in out/merch_lib/qa/
import os,glob,json,sys,cv2,numpy as np
R='/home/claude/alphadog-styles/out/merch_lib/'
def check(p):
    im=cv2.imread(p,cv2.IMREAD_UNCHANGED)
    if im is None or im.shape[2]<4: return {'bad':'noalpha'}
    a=im[...,3].astype(np.float32)/255;rgb=im[...,:3].astype(np.float32);h,w=a.shape
    hard=(a>0.5).astype(np.uint8)
    if hard.sum()<5000: return {'bad':'tiny'}
    k=cv2.distanceTransform(hard,cv2.DIST_L2,3);ring=(k>0)&(k<=4);inner=k>15
    mc=rgb.min(2);gmed=float(np.median(mc[inner])) if inner.sum()>200 else 255.0
    fr=float((mc[ring]>235).mean()) if gmed<170 and ring.sum()>100 else 0.0
    n,l,st,_=cv2.connectedComponentsWithStats(hard);comps=int((st[1:,4]>0.01*hard.sum()).sum()) if n>1 else 1
    sem=float((a[(a>0.02)&(a<0.98)]>0).size)/max(1,hard.sum())
    fill=float(hard.sum())/(h*w)
    return {'fringe':round(fr,4),'gmed':gmed,'comps':comps,'fill':round(fill,3),'bad':'halo' if fr>0.03 else ('frag' if comps>3 else '')}
if __name__=='__main__':
    res={}
    for p in sorted(glob.glob(R+'**/*.webp',recursive=True)):
        res[os.path.relpath(p,R)]=check(p)
    json.dump(res,open(R+'qa.json','w'));b=[k for k,v in res.items() if v.get('bad')]
    print(len(res),'checked',len(b),'flagged')
    os.makedirs(R+'qa',exist_ok=True)
    def sheet(keys,name):
        tiles=[]
        for k in keys:
            im=cv2.imread(R+k,cv2.IMREAD_UNCHANGED);bg=np.zeros(im.shape[:2]+(3,),np.float32);a=im[...,3:4].astype(np.float32)/255;o=(im[...,:3]*a+bg*(1-a)).astype(np.uint8)
            s=220/max(o.shape[:2]);o=cv2.resize(o,(int(o.shape[1]*s),int(o.shape[0]*s)));t=np.zeros((230,230,3),np.uint8);t[:o.shape[0],:o.shape[1]]=o;cv2.putText(t,k.split('/')[-1][:12],(2,226),0,0.4,(0,255,0),1);tiles.append(t)
        cols=8
        while len(tiles)%cols: tiles.append(np.zeros((230,230,3),np.uint8))
        cv2.imwrite(R+'qa/'+name,np.vstack([np.hstack(tiles[i:i+cols]) for i in range(0,len(tiles),cols)]))
    import random;random.seed(1)
    sheet(b[:48],'flagged1.jpg');sheet(random.sample(list(res),48),'random1.jpg')

# d5 funny breed compilation, Tue 2026-11-24: 6 NEW breeds (dachshund, french bulldog, labrador, pit bull, husky, pug), new merch/views, a different REAL photo bg per cut (bgmatch),
# 0.75 s cross-dissolves between cuts (no 0.2 s wipes), each clip once. usage: vidF5.py CFG.json  (cfg: out, cuts[{clip,t0,cx,cap,chip,key,bg}], end[{key}], endhead)
import json,sys,cv2
cfg=json.load(open(sys.argv[1])); sys.argv=[sys.argv[0],'x']
from funny import *
from lib_apparel import apparel_lib
cuts=cfg['cuts']
for i in range(len(cuts)-1):
    a,b=cuts[i]['key'].split('/'),cuts[i+1]['key'].split('/')
    assert a[0]!=b[0] and a[2].replace('_back','')[-2:]!=b[2].replace('_back','')[-2:] and a[1]!=b[1],(a,b)
BGS=[]
for c in cuts:
    im=cv2.imread('/home/claude/alphadog-styles/out/bg/'+c['bg']+'.jpg');im=cv2.resize(im,(1080,1920)).astype(np.float32)
    BGS.append(np.clip(im*0.92,0,255))
clips=[Clip(c['clip'],c['t0'],c['cx'],c.get('zoom',1.0),c.get('yb',0.5)) for c in cuts]
PR=[apparel_lib(c['key'],(440,440)) for c in cuts]
caps=[chip(c['cap'],46) for c in cuts];bchips=[chip(c['chip'],42,fg=(255,255,255,255),bg=(236,72,60,255)) for c in cuts]
EP=[apparel_lib(c['key'],(330,430)) for c in cfg['end']]
endchip=chip(cfg.get('endhead',"WHICH ONE IS YOURS?"),62,fg=(255,255,255,255),bg=(20,20,20,255));cta=V.cta(CTA_TXT)
NC=len(cuts);P=40;X=18;END=84;TOT=P*NC+END+0;
EBG=np.clip(cv2.resize(cv2.imread('/home/claude/alphadog-styles/out/bg/'+cfg['endbg']+'.jpg'),(1080,1920)).astype(np.float32)*0.92,0,255)
def R(k,l):
    """image for cut k (k==NC -> end card) at local frame l"""
    if k<NC:
        t=l/24;fr=BGS[k].copy()
        fr=put_window(fr,clips[k].win(t,punch=0.06*min(l,P)/P),540,1020,1.0,1.0)
        fr=blit(fr,PR[k],790,1250,bounce((l-7)/9),1.0,rot=-7)
        im=toim(fr);ta=min(1,max(l-int(X*0.7),0)/5) if l<P else 1-sm((l-P)/(X*0.6));ta=max(ta,0) if l<P else max(ta,0)
        if l<P and l>=0: ta=min(1,max(l-int(X*0.7),0)/5) if k>0 else min(1,l/4)
        im=overlay(im,caps[k],540,455,ta,scale=bounce(max(l-int(X*0.7),0)/7) if k>0 else bounce(l/7));im=overlay(im,bchips[k],330,1330,ta,scale=bounce(max(l-int(X*0.7)-3,0)/7) if k>0 else bounce((l-3)/7))
    else:
        fr=EBG.copy()
        for j,(cx,cy) in enumerate(((200,920),(540,880),(880,920))): fr=blit(fr,EP[j],cx,cy,bounce((l-8-7*j)/9),1.0,rot=(-5,0,5)[j])
        im=toim(fr);im=overlay(im,endchip,540,470,1.0,scale=bounce(l/9))
        if l>=20: im=paste_c(im,cta,1262,min(1,(l-20)/10))
    return im
p=enc(cfg['out'])
for f in range(TOT):
    k=min(f//P,NC);l=f-k*P
    im=R(k,l)
    if 0<=k-1<NC and l<X:
        a=sm(l/X);prev=R(k-1,l+P)
        im=Image.blend(prev.convert('RGBA'),im.convert('RGBA'),a)
    im=paste_c(im,V.LK,300)
    p.stdin.write(back(im).tobytes())
p.stdin.close();p.wait();print('done')

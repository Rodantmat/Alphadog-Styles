# d1 snack/ride gag, Tue 2026-11-17: border collie, new gag, real photo bg (pg_citrus_orchard_puresky_2), new merch/views/music
import cv2
im=cv2.imread('/home/claude/alphadog-styles/out/bg/pg_citrus_orchard_puresky_2.jpg');cv2.imwrite('/tmp/kl/bgc/pg_citrus_orchard_puresky_2.png',cv2.resize(im,(1080,1920)))
from funny import *
from lib_apparel import apparel_lib
BG=bgc('pg_citrus_orchard_puresky_2')
clip=Clip('50660',1.0,cx=0.62)
keys=['wtank/border_collie/1MI_back','tee/border_collie/2AS','cap_foam/border_collie/2FP']
PR=[apparel_lib(k,(760,700)) for k in keys]
cap1=chip("ME WAITING FOR MY HUMAN",46);cap2=chip("\"JUST ONE LAST EMAIL\"",46)
pay=chip("STILL WAITING.",54,fg=(255,255,255,255),bg=(236,72,60,255))
punch=chip("BORDER COLLIE MOOD",60,fg=(255,255,255,255),bg=(20,20,20,255))
cta=V.cta(CTA_TXT)
T=276;SW=144;p=enc('/tmp/kl/vF1d_silent.mp4')
for f in range(T):
    fr=BG.copy()
    if f<SW+22:
        t=f/24;tt=sm((f-SW)/22)
        s=(0.88+0.12*bounce(f/9)) if f<9 else 1.0
        s=s*(1-0.55*tt);cy=1020-440*tt;al=1-tt
        fr=put_window(fr,clip.win(t,punch=0.05*t/6),540,cy,s,al)
    if f>=SW+8:
        k=min(int((f-SW-8)//34),2);tl=(f-SW-8-34*k)/10
        fr=blit(fr,PR[k],540,905,bounce(min(tl,1))*1.0,1.0)
    im=toim(fr)
    if f<SW+14:
        a=1-sm((f-SW)/10)
        im=overlay(im,cap1,540,422,a*min(1,f/5));im=overlay(im,cap2,540,538,a*min(1,max(f-4,0)/5))
        if f>=76: im=overlay(im,pay,540,1330,a,scale=bounce((f-76)/8)*1.0)
    if f>=SW+8: im=overlay(im,punch,540,455,1.0,scale=bounce((f-SW-8)/9))
    im=paste_c(im,V.LK,300)
    if f>=SW+24: im=paste_c(im,cta,1262,min(1,(f-SW-24)/10))
    p.stdin.write(back(im).tobytes())
p.stdin.close();p.wait();print('done')

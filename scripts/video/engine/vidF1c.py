# d1 snack/ride gag, Fri 2026-11-20: corgi, new joke, real photo bg (pg_chapmans_drive_1), new merch/views/music
import cv2
im=cv2.imread('/home/claude/alphadog-styles/out/bg/pg_chapmans_drive_1.jpg');cv2.imwrite('/tmp/kl/bgc/pg_chapmans_drive_1.png',cv2.resize(im,(1080,1920)))
from funny import *
from lib_apparel import apparel_lib
BG=bgc('pg_chapmans_drive_1')
clip=Clip('45870',1.0,cx=0.5)
keys=['tee/pembroke_welsh_corgi/1LB_back','hoodie/pembroke_welsh_corgi/3SA_back','cap_dad/pembroke_welsh_corgi/2DW']
PR=[apparel_lib(k,(760,700)) for k in keys]
cap1=chip("ME WHEN SOMEONE SAYS",46);cap2=chip("\"WANNA GO FOR WALKIES?\"",46)
pay=chip("ZOOMIES LOADING.",54,fg=(255,255,255,255),bg=(236,72,60,255))
punch=chip("CORGI MOOD",64,fg=(255,255,255,255),bg=(20,20,20,255))
cta=V.cta(CTA_TXT)
T=276;SW=144;p=enc('/tmp/kl/vF1c_silent.mp4')
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

# d1 (drooling Boston terrier gag) re-creation for Fri 2026-11-13: new joke, new background (memphis bg_028), new merch/views, new music
import shutil,sys
shutil.copy('/home/claude/alphadog-styles/out/backgrounds/bg_028_memphis.jpg','/tmp/kl/bgc/memphis28.png') if False else None
import cv2
im=cv2.imread('/home/claude/alphadog-styles/out/backgrounds/bg_028_memphis.jpg');cv2.imwrite('/tmp/kl/bgc/memphis28.png',im)
from funny import *
from lib_apparel import apparel_lib
BG=bgc('memphis28')
clip=Clip('1212',2.0,cx=0.60)
keys=['tee/boston_terrier/1MR_back','hoodie/boston_terrier/2LB','wtank/boston_terrier/1MI']
PR=[apparel_lib(k,(760,700)) for k in keys]
cap1=chip("ME WHEN SOMEONE SAYS",46);cap2=chip("\"WANNA GO FOR A RIDE?\"",46)
pay=chip("DROOLING ALREADY.",54,fg=(255,255,255,255),bg=(236,72,60,255))
punch=chip("BOSTON TERRIER MOOD",64,fg=(255,255,255,255),bg=(20,20,20,255))
cta=V.cta(CTA_TXT)
T=276;SW=144;p=enc('/tmp/kl/vF1b_silent.mp4')
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

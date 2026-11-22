# d1 snack/gag, feed-safe (rule 15: all text/merch rows 430-1580) + breed-led frame 0 (rule 16b). usage (from /tmp/kl): vidF1e.py CFG.json
# cfg: out, bg, clip, t0, cx, keys[3], cap1, cap2, pay, punch
import json,sys,cv2
cfg=json.load(open(sys.argv[1])); sys.argv=[sys.argv[0],'x']
from funny import *
from lib_apparel import apparel_lib
im=cv2.imread('/home/claude/alphadog-styles/out/bg/'+cfg['bg']+'.jpg');cv2.imwrite('/tmp/kl/bgc/'+cfg['bg']+'.png',cv2.resize(im,(1080,1920)))
BG=bgc(cfg['bg'])
clip=Clip(cfg['clip'],cfg.get('t0',1.0),cx=cfg.get('cx',0.5))
PR=[apparel_lib(k,(760,700)) for k in cfg['keys']]
cap1=chip(cfg['cap1'],46);cap2=chip(cfg['cap2'],46)
pay=chip(cfg['pay'],54,fg=(255,255,255,255),bg=(236,72,60,255))
punch=chip(cfg['punch'],60,fg=(255,255,255,255),bg=(20,20,20,255))
cta=V.cta(CTA_TXT)
T=276;SW=144;p=enc(cfg['out'])
for f in range(T):
    fr=BG.copy()
    if f<SW+22:
        t=f/24;tt=sm((f-SW)/22)
        s=(0.88+0.12*bounce(f/9)) if f<9 else 1.0
        s=s*(1-0.55*tt);cy=1070-380*tt;al=1-tt
        fr=put_window(fr,clip.win(t,punch=0.05*t/6),540,cy,s,al)
    if f>=SW+8:
        k=min(int((f-SW-8)//34),2);tl=(f-SW-8-34*k)/10
        fr=blit(fr,PR[k],540,990,bounce(min(tl,1)),1.0)
    im=toim(fr)
    if f<SW+14:
        a=1-sm((f-SW)/10)
        im=overlay(im,cap1,540,480,a*min(1,(f+2)/5));im=overlay(im,cap2,540,585,a*min(1,max(f-4,0)/5))
        if f>=76: im=overlay(im,pay,540,1370,a,scale=bounce((f-76)/8))
    if f>=SW+8: im=overlay(im,punch,540,520,1.0,scale=bounce((f-SW-8)/9))
    if f>=SW+24: im=paste_c(im,cta,1440,min(1,(f-SW-24)/10))
    im=paste_c(im,V.LK,1520)
    p.stdin.write(back(im).tobytes())
p.stdin.close();p.wait();print('done')

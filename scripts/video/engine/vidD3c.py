#!/usr/bin/env python3
"""d3c: scenery tees on REAL scenery photos (bgmatch kind scenery) with 0.7 s crossfades. 8 scenes, one library background each (structurally different families), one tee cutout
(merch_lib) per scene, slow push-in, lockup on top, CTA on the last 2 scenes under the tee. usage: vidD3b.py OUT.mp4 MUSIC.mp3"""
import cv2,numpy as np,subprocess,sys
from PIL import Image,ImageDraw,ImageFont
R='/home/claude/alphadog-styles/';W,H=1080,1920;FPS=30;STEP=1.2;XF=0.7;SEC=STEP+XF
FP='/usr/share/fonts/truetype/google-fonts/Poppins-%s.ttf'
import json
SC=[(o[2],o[0]) for o in json.load(open(sys.argv[3]))]   # (real scenery photo file in out/bg, merch_lib key)
logo=Image.open(R+'store/logo.png').convert("RGBA").resize((92,92),Image.LANCZOS)
m=Image.new("L",(92,92),0);ImageDraw.Draw(m).ellipse((1,1,90,90),fill=255)
base=Image.new('RGBA',(92,92),(255,255,255,255));base.alpha_composite(logo.resize((72,72),Image.LANCZOS),(10,10));logo=base;logo.putalpha(m)
def lockup():
    f=ImageFont.truetype(FP%'Medium',40);txt="ALPHADOG STYLES";sp=5
    d0=ImageDraw.Draw(Image.new('L',(1,1)));tw=sum(d0.textlength(c,font=f)+sp for c in txt)-sp
    w=int(92+22+tw+44);h=112;im=Image.new("RGBA",(w,h),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,w-1,h-1),radius=56,fill=(14,14,18,170),outline=(255,255,255,70),width=2)
    im.alpha_composite(logo,(10,10));x=10+92+22
    for c in txt: d.text((x,h/2),c,font=f,fill=(255,255,255,255),anchor="lm");x+=d0.textlength(c,font=f)+sp
    return im
LK=lockup()
def cta(text):
    f=ImageFont.truetype(FP%'Bold',44);tw=ImageDraw.Draw(Image.new('L',(1,1))).textlength(text,font=f)
    w=int(tw+90);h=96;im=Image.new("RGBA",(w,h),(0,0,0,0));d=ImageDraw.Draw(im)
    d.rounded_rectangle((0,0,w-1,h-1),radius=48,fill=(255,255,255,245));d.text((w/2,h/2+1),text,font=f,fill=(20,20,24,255),anchor="mm");return im
def tee(key):
    im=Image.open(R+f'out/merch_lib/{key}.webp').convert("RGBA");bb=im.getbbox();im=im.crop(bb)
    sw=800;sh=int(im.height*sw/im.width)
    if sh>880: sh=880;sw=int(im.width*sh/im.height)
    return np.array(im.resize((sw,sh),Image.LANCZOS))
def bgimg(n):
    im=cv2.imread(R+f'out/bg/{n}');im=cv2.resize(im,(W,H),interpolation=cv2.INTER_AREA).astype(np.float32)
    yy,xx=np.mgrid[0:H,0:W];v=1-0.25*(((xx-W/2)/(W*0.75))**2+((yy-H*0.45)/(H*0.7))**2)
    return np.clip(im*v[...,None],0,255)
def frame(bg,s,t,ctatext):
    z=1.0+0.03*t;M=cv2.getRotationMatrix2D((W/2,H*0.5),0,z);b=cv2.warpAffine(bg,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    pop=0.93+0.07*(1-np.exp(-t*10));sw=int(s.shape[1]*pop);sh=int(s.shape[0]*pop);ss=cv2.resize(s,(sw,sh),interpolation=cv2.INTER_AREA)
    cx,cy=W//2,860;x0=cx-sw//2;y0=cy-sh//2
    A=np.zeros((H,W),np.float32);A[y0:y0+sh,x0:x0+sw]=ss[...,3]/255.
    sh1=cv2.GaussianBlur(np.roll(A,(30,0),(0,1)),(0,0),30)*0.45;sh2=cv2.GaussianBlur(np.roll(A,(6,0),(0,1)),(0,0),5)*0.3
    Fb=np.zeros((H,W,3),np.float32);Fb[y0:y0+sh,x0:x0+sw]=ss[...,[2,1,0]]
    out=b*(1-np.clip(sh1+sh2,0,0.7)[...,None]);out=out*(1-A[...,None])+Fb*A[...,None]
    im=Image.fromarray(cv2.cvtColor(np.clip(out,0,255).astype(np.uint8),cv2.COLOR_BGR2RGB)).convert("RGBA")
    im.alpha_composite(LK,((W-LK.width)//2,270))
    if ctatext: c=cta(ctatext);im.alpha_composite(c,((W-c.width)//2,1370))
    return cv2.cvtColor(np.array(im.convert("RGB")),cv2.COLOR_RGB2BGR)
def build(out,music):
    tmp=out+'.silent.mp4'
    p=subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-c:v","libx264","-preset","veryfast","-crf","17","-pix_fmt","yuv420p",tmp],stdin=subprocess.PIPE)
    n=len(SC);ASSET=[(bgimg(a),tee(k)) for a,k in SC];SL=int(FPS*SEC);ST=int(FPS*STEP);total=ST*n+int(FPS*XF)
    for f in range(total):
        i=min(f//ST,n-1);k=f-i*ST
        def fr(j,kk): return frame(ASSET[j][0],ASSET[j][1],kk/FPS,"alphadogstyles.com" if j>=n-2 else None).astype(np.float32)
        im=fr(i,k)
        if i>0 and k<int(FPS*XF):   # crossfade from previous scene (still on screen) into this one
            w=k/(FPS*XF);w=w*w*(3-2*w);im=fr(i-1,k+ST)*(1-w)+im*w
        p.stdin.write(np.clip(im,0,255).astype(np.uint8).tobytes())
    p.stdin.close();p.wait();tot=total/FPS
    subprocess.run(["ffmpeg","-y","-v","error","-i",tmp,"-ss","0","-i",music,"-filter_complex",f"[1:a]atrim=0:{tot},afade=t=in:d=0.4,afade=t=out:st={tot-1.2}:d=1.2,volume=0.8[a]","-map","0:v","-map","[a]","-t",str(tot),"-c:v","copy","-c:a","aac","-b:a","160k","-movflags","+faststart",out],check=True)
    import os;os.remove(tmp)
if __name__=="__main__": build(sys.argv[1],sys.argv[2])

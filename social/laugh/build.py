# Reusable "dogs laugh" template. usage: python3 social/laugh/build.py joke.json  -> out/laugh/<name>.mp4
import sys,json,math,subprocess,os
sys.path.insert(0,'/home/claude/alphadog-styles/scripts/video/engine');sys.argv=[sys.argv[0]]+sys.argv[1:]
import cv2,numpy as np
from PIL import Image,ImageDraw,ImageFont,ImageFilter
R='/home/claude/alphadog-styles/'
cfgf=sys.argv[1];J=json.load(open(cfgf))
import funny
W,H=1080,1920;FPS=30
FB=R+'out/footage/'
# dogs (fixed across all weekly videos): file, crop centre (1280x720 src), size, hold time, laugh start
DOGS=[('1552',(640,380),640,0.4,3.0),('50667',(690,330),600,5.5,0.0),('50652',(650,260),520,0.2,5.0),('45834',(680,290),470,0.3,5.0)]
LAUGH=2.3;SQ=440;GAP=26
def font(sz): return ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',sz)
def frames(f,c,sz,t0,n):
    cap=cv2.VideoCapture(FB+f+'.mp4');cap.set(cv2.CAP_PROP_POS_MSEC,t0*1000);out=[]
    for _ in range(n):
        ok,fr=cap.read()
        if not ok: fr=out[-1] if out else np.zeros((720,1280,3),np.uint8)
        else:
            x0=int(np.clip(c[0]-sz/2,0,1280-sz));y0=int(np.clip(c[1]-sz/2,0,720-sz));fr=cv2.resize(fr[y0:y0+sz,x0:x0+sz],(SQ,SQ),interpolation=cv2.INTER_AREA)
        out.append(fr)
    return out
NL=int(LAUGH*FPS)
HOLD=[];LF=[]
for f,c,sz,th,tl in DOGS:
    HOLD.append(frames(f,c,sz,th,1)[0]);LF.append(frames(f,c,sz,tl,NL))
def rmask(w,h,r):
    m=np.zeros((h,w),np.uint8);cv2.rectangle(m,(r,0),(w-r,h),255,-1);cv2.rectangle(m,(0,r),(w,h-r),255,-1)
    for x,y in((r,r),(w-r,r),(r,h-r),(w-r,h-r)): cv2.circle(m,(x,y),r,255,-1)
    return cv2.GaussianBlur(m,(0,0),0.8).astype(np.float32)/255
SM=rmask(SQ,SQ,40);BW=10;SMi=rmask(SQ-2*BW,SQ-2*BW,32)
bg=funny.paws(seed=J.get('seed',5)).astype(np.float32)
POS=[(W//2-SQ-GAP//2,H//2-SQ-GAP//2+30),(W//2+GAP//2,H//2-SQ-GAP//2+30),(W//2-SQ-GAP//2,H//2+GAP//2+30),(W//2+GAP//2,H//2+GAP//2+30)]
def sm(x): x=min(max(x,0),1);return x*x*(3-2*x)
def bounce(t):
    if t<=0: return 0.0
    if t>=1: return 1.0
    return 1+1.7*math.pow(t-1,3)+0.7*math.pow(t-1,2)
def wrap(txt,fn,maxw):
    d=ImageDraw.Draw(Image.new('RGB',(10,10)));ws=txt.split();lines=[];cur=''
    for w in ws:
        t=(cur+' '+w).strip()
        if d.textlength(t,font=fn)<=maxw: cur=t
        else: lines.append(cur);cur=w
    lines.append(cur);return lines
def textlayer(txt,sz,color=(255,255,255),maxw=940,stroke=(14,60,140),lh=1.18):
    fn=font(sz);lines=wrap(txt,fn,maxw);h=int(len(lines)*sz*lh)+40
    im=Image.new('RGBA',(W,h),(0,0,0,0));d=ImageDraw.Draw(im)
    for i,l in enumerate(lines):
        w=d.textlength(l,font=fn);y=20+int(i*sz*lh)
        d.text(((W-w)/2+4,y+6),l,font=fn,fill=(0,0,0,110),stroke_width=6,stroke_fill=(0,0,0,110))
        d.text(((W-w)/2,y),l,font=fn,fill=color+(255,),stroke_width=7,stroke_fill=stroke+(255,))
    return im
def paste(canvas,im,cx,cy,scale=1.0,alpha=1.0,rot=0):
    if alpha<=0 or scale<=0: return
    im=im.copy()
    if scale!=1 or rot:
        w,h=im.size;im=im.resize((max(1,int(w*scale)),max(1,int(h*scale))),Image.LANCZOS)
        if rot: im=im.rotate(rot,expand=True,resample=Image.BICUBIC)
    if alpha<1:
        a=im.split()[3].point(lambda v:int(v*alpha));im.putalpha(a)
    canvas.alpha_composite(im,(int(cx-im.width/2),int(cy-im.height/2))) if (0<=cx-im.width/2 and 0<=cy-im.height/2) else canvas.paste(im,(int(cx-im.width/2),int(cy-im.height/2)),im)
def tile(frame,badge):
    rgb=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB).astype(np.float32)
    out=np.zeros((SQ,SQ,4),np.float32);out[...,:3]=255;out[...,3]=SM*255
    inner=np.zeros((SQ,SQ),np.float32);inner[BW:SQ-BW,BW:SQ-BW]=SMi
    out[...,:3]=out[...,:3]*(1-inner[...,None])+rgb*inner[...,None]
    im=Image.fromarray(out.astype(np.uint8),'RGBA');d=ImageDraw.Draw(im)
    d.ellipse((12,12,92,92),fill=(255,214,10,255),outline=(255,255,255,255),width=5)
    f=font(52);w=d.textlength(str(badge),font=f);d.text((52-w/2,48),str(badge),font=f,fill=(30,40,70,255),anchor='lm')
    return im
def shadow(im,blur=22,off=16,op=0.45):
    a=im.split()[3];s=Image.new('RGBA',(im.width+120,im.height+120),(0,0,0,0))
    sh=Image.new('RGBA',a.size,(0,0,0,255));sh.putalpha(a.point(lambda v:int(v*op)))
    s.paste(sh,(60,60+off),sh);s=s.filter(ImageFilter.GaussianBlur(blur));s.alpha_composite(im,(60,60));return s
# merch
MERCH=[]
for k,(x,y,w,rot) in zip(J['merch'],[(330,570,520,-7),(700,720,620,6),(350,1180,610,5),(745,1270,640,-5),(540,935,570,-2)]):
    im=Image.open(R+'out/laugh/cut/'+k+'.png').convert('RGBA');im=im.resize((w,int(im.height*w/im.width)),Image.LANCZOS);MERCH.append((shadow(im),x,y,rot))
Q=textlayer(J['q'],J.get('qsize',74));A=textlayer(J['a'],J.get('asize',92),color=(255,226,60))
TOP=textlayer(J['top'],62);BOT=textlayer(J['bottom'],48,maxw=980)
# timeline
T_Q=2.6;T_FACE=T_Q;T_HOLD=T_FACE+1.3+2.6;T_LAUGH=T_HOLD;T_END=T_LAUGH+LAUGH;T_CLR=T_END+0.4;T_M=T_CLR+0.15;STEP=0.42;T_TOT=T_M+len(MERCH)*STEP+2.4
N=int(T_TOT*FPS)
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',R+'out/laugh/_v.mp4']
pr=subprocess.Popen(cmd,stdin=subprocess.PIPE)
tile_cache={}
for n in range(N):
    t=n/FPS;cv=Image.fromarray(np.clip(bg,0,255).astype(np.uint8)).convert('RGBA')
    clr=1-sm((t-T_END-0.05)/0.3) if t<T_CLR else 0  # fade/scale out of dog scene
    if t<T_CLR:
        # question: centred then moves up
        mv=sm((t-T_Q)/0.5);qy=H/2-80+(300-(H/2-80))*mv if False else (H/2-60)+((250)-(H/2-60))*mv
        qs=bounce(t/0.45)
        paste(cv,Q,W/2,qy,scale=max(qs,0.01)*(0.92+0.08*clr)+0.0,alpha=clr)
        for i in range(4):
            ti=T_FACE+i*0.3
            if t>=ti:
                if t>=T_LAUGH: fr=LF[i][min(int((t-T_LAUGH)*FPS),NL-1)]
                else: fr=HOLD[i]
                key=(i,id(fr))
                if key not in tile_cache: tile_cache[key]=tile(fr,i+1)
                tl=tile_cache[key];sc=bounce((t-ti)/0.4)
                x,y=POS[i];paste(cv,shadow(tl,blur=14,off=10,op=0.35) if False else tl,x+SQ/2,y+SQ/2,scale=max(sc,0.01)*(0.9+0.1*clr),alpha=clr)
        if t>=T_LAUGH:
            s=bounce((t-T_LAUGH)/0.35);paste(cv,A,W/2,1560,scale=max(s,0.01)*(0.9+0.1*clr),alpha=clr)
            # little shake while laughing
    else:
        paste(cv,TOP,W/2,150,alpha=sm((t-T_M)/0.4))
        for j,(im,x,y,rot) in enumerate(MERCH):
            ti=T_M+j*STEP
            if t>=ti:
                s=bounce((t-ti)/0.28);ox=(1-s)*(-1 if j%2 else 1)*160;paste(cv,im,x+ox,y,scale=max(0.4+0.6*s,0.05),alpha=min(1,(t-ti)/0.1),rot=rot)
        paste(cv,BOT,W/2,1770,alpha=sm((t-T_M-1.2)/0.5))
    pr.stdin.write(np.array(cv.convert('RGB')).tobytes())
pr.stdin.close();pr.wait()
# audio
name=J['name'];out=R+f'out/laugh/{name}.mp4'
L=R+'out/sfx/'+J.get('laugh','424')+'.mp3';M=R+'out/music2/'+J['music']
dl=int(T_LAUGH*1000)
subprocess.run(['ffmpeg','-y','-v','error','-i',R+'out/laugh/_v.mp4','-i',M,'-i',L,'-filter_complex',
 f'[1:a]atrim=0:{T_TOT},afade=t=in:d=0.6,afade=t=out:st={T_TOT-1.2}:d=1.2,volume=0.28[m];[2:a]atrim=0:{LAUGH+0.3},volume=1.7,adelay={dl}|{dl}[l];[m][l]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]',
 '-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(T_TOT),out],check=True)
print(out,T_TOT)

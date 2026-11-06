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
# dogs (fixed across all weekly videos): video, crop keyframes [(src_t,cx,cy)], crop size, mode f=forward r=reversed, laugh-onset (source seconds)
DOGS=[('out/footage2/7684117.mp4',[(0,650,330),(1.5,700,310),(3,650,320),(4.5,820,330),(5.5,660,370),(6.5,700,360),(7.5,780,380),(8.5,900,390)],640,4.75,5.75,3.8),
 ('out/footage2/7802455.mp4',[(4,500,330),(6,640,310),(7,700,420),(8,500,420),(9,690,400),(10,700,360),(11,840,390)],620,6.0,4.0,8.0),
 ('out/footage/1552.mp4',[(0,640,380),(9,640,380)],640,1.0,0.0,2.8),
 ('out/footage/50667.mp4',[(0,690,330),(9,690,330)],600,5.8,4.6,1.0)]   # (file, crop keyframes, size, calm_end, calm_far, laugh_peak) in source seconds
TR=0.28  # seconds the face takes to snap from serious to full laugh
ANSY=1375;LAUGH=3.5;SQ=380;GAP=36;CX=500  # phone-safe area: x 70-930, y 250-1500 (clear of app buttons/captions)
def font(sz): return ImageFont.truetype('/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf',sz)
def loadall(f,kf,sz):
    cap=cv2.VideoCapture(R+f);fps=cap.get(cv2.CAP_PROP_FPS) or 30;out=[];i=0
    kt=[k[0] for k in kf];kx=[k[1] for k in kf];ky=[k[2] for k in kf]
    while True:
        ok,fr=cap.read()
        if not ok: break
        t=i/fps;i+=1;H0,W0=fr.shape[:2];cx=np.interp(t,kt,kx);cy=np.interp(t,kt,ky)
        x0=int(np.clip(cx-sz/2,0,W0-sz));y0=int(np.clip(cy-sz/2,0,H0-sz));out.append(cv2.resize(fr[y0:y0+sz,x0:x0+sz],(SQ,SQ),interpolation=cv2.INTER_AREA))
    return out,fps
CLIPS=[loadall(f,kf,sz) for f,kf,sz,a_,b_,c_ in DOGS]
def tri(x,L):
    if L<=0: return 0.0
    x=x%(2*L);return x if x<=L else 2*L-x
def dogframe(i,p,lead):  # p = seconds since tile appeared; the serious->laugh snap starts at p=lead (all four dogs together)
    fr,fps=CLIPS[i];ce,cf,pk=DOGS[i][3],DOGS[i][4],DOGS[i][5];dur=len(fr)/fps
    q=p-lead;d=1 if pk>ce else -1
    if q<0: st=ce+(1 if cf>ce else -1)*tri(-q*0.6,abs(cf-ce))
    elif q<TR: st=ce+(pk-ce)*(q/TR)
    else: st=pk+d*(q-TR)
    st=tri(st,dur-1/fps)
    return fr[min(max(int(round(st*fps)),0),len(fr)-1)]
def rmask(w,h,r):
    m=np.zeros((h,w),np.uint8);cv2.rectangle(m,(r,0),(w-r,h),255,-1);cv2.rectangle(m,(0,r),(w,h-r),255,-1)
    for x,y in((r,r),(w-r,r),(r,h-r),(w-r,h-r)): cv2.circle(m,(x,y),r,255,-1)
    return cv2.GaussianBlur(m,(0,0),0.8).astype(np.float32)/255
SM=rmask(SQ,SQ,40);BW=10;SMi=rmask(SQ-2*BW,SQ-2*BW,32)
import bgs
bg=(bgs.make(J['bgstyle'],J.get('seed',5),*J['bgcols']) if 'bgstyle' in J else funny.paws(seed=J.get('seed',5))).astype(np.float32)
POS=[(CX-SQ-GAP//2,480),(CX+GAP//2,480),(CX-SQ-GAP//2,480+SQ+GAP),(CX+GAP//2,480+SQ+GAP)]
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
    return im
def shadow(im,blur=22,off=16,op=0.45):
    a=im.split()[3];s=Image.new('RGBA',(im.width+120,im.height+120),(0,0,0,0))
    sh=Image.new('RGBA',a.size,(0,0,0,255));sh.putalpha(a.point(lambda v:int(v*op)))
    s.paste(sh,(60,60+off),sh);s=s.filter(ImageFilter.GaussianBlur(blur));s.alpha_composite(im,(60,60));return s
# merch
MERCH=[]
POSM=[(300,650,430,-6),(700,660,430,5),(700,1110,420,-4),(300,1100,430,4),(500,880,400,2)]
sys.path.insert(0,R+'scripts/video');import merch_lib as ML
def ensure(k):
    o=R+'out/merch_lib/'+k+'.webp'
    if os.path.exists(o) or '/' not in k: return
    back=k.endswith('_back');rel=k[:-5] if back else k;f=ML.SRC+rel+'.jpg'
    r=ML.cut_back(f) if back else ML.cut(f);ML.save(r[0],o)
for k,(x,y,w,rot) in zip(J['merch'],POSM):
    ensure(k)
    im=Image.open(R+('out/merch_lib/'+k+'.webp' if '/' in k else 'out/laugh/cut/'+k+'.png')).convert('RGBA');im=im.crop(im.getbbox());im=im.resize((w,int(im.height*w/im.width)),Image.LANCZOS);MERCH.append((shadow(im),x,y,rot))
Q=textlayer(J['q'],J.get('qsize',70),maxw=820);A=textlayer(J['a'],J.get('asize',78),color=(255,226,60),maxw=840)
TOP=textlayer(J['top'],58,maxw=820);BOT=textlayer(J['bottom'],42,maxw=820)
# timeline
T_Q=0.3;T_FACE=2.6;T_HOLD=T_FACE+3.7;T_LAUGH=T_HOLD;T_END=T_LAUGH+LAUGH;T_CLR=T_END+0.5;T_M=T_CLR+0.2;STEP=0.6;T_TOT=T_M+len(MERCH)*STEP+2.2
N=int(T_TOT*FPS)
cmd=['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-an','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',R+'out/laugh/_v.mp4']
pr=subprocess.Popen(cmd,stdin=subprocess.PIPE)
tile_cache={}
for n in range(N):
    t=n/FPS;cv=Image.fromarray(np.clip(bg,0,255).astype(np.uint8)).convert('RGBA')
    clr=1-sm((t-T_END-0.05)/0.3) if t<T_CLR else 0  # fade/scale out of dog scene
    if t<T_CLR:
        # question: centred then moves up
        mv=1;qy=330
        qs=bounce((t-0.3)/0.45)
        paste(cv,Q,CX,qy,scale=max(qs,0.01)*(0.92+0.08*clr)+0.0,alpha=clr)
        for i in range(4):
            ti=T_FACE+i*0.4
            if t>=ti:
                fr=dogframe(i,t-ti,T_LAUGH-ti);tl=tile(fr,i+1);sc=bounce((t-ti)/0.4)
                pulse=1;rot=0
                if T_LAUGH<=t<T_END: q=t-T_LAUGH;pulse=1+0.05*abs(math.sin(2*math.pi*2.2*q));rot=3.0*math.sin(2*math.pi*4.4*q+i)
                x,y=POS[i];paste(cv,tl,x+SQ/2,y+SQ/2,scale=max(sc,0.01)*(0.9+0.1*clr)*pulse,alpha=clr,rot=rot)
        if t>=T_LAUGH:
            s=bounce((t-T_LAUGH)/0.35);paste(cv,A,CX,ANSY,scale=max(s,0.01)*(0.9+0.1*clr),alpha=clr)
            # little shake while laughing
    else:
        paste(cv,TOP,CX,300,alpha=sm((t-T_M)/0.4))
        for j,(im,x,y,rot) in enumerate(MERCH):
            ti=T_M+j*STEP
            if t>=ti:
                s=bounce((t-ti)/0.28);ox=(1-s)*(-1 if j%2 else 1)*160;paste(cv,im,x+ox,y,scale=max(0.4+0.6*s,0.05),alpha=min(1,(t-ti)/0.1),rot=rot)
        paste(cv,BOT,CX,1470,alpha=sm((t-T_M-1.2)/0.5))
    pr.stdin.write(np.array(cv.convert('RGB')).tobytes())
pr.stdin.close();pr.wait()
# audio
name=J['name'];out=R+f'out/laugh/{name}.mp4'
L=R+'out/sfx/'+J.get('laugh','424')+'.mp3';M=R+'out/music2/'+J['music']
dl=int(T_LAUGH*1000)
subprocess.run(['ffmpeg','-y','-v','error','-i',R+'out/laugh/_v.mp4','-i',M,'-i',L,'-filter_complex',
 f'[1:a]atrim=0:{T_TOT},afade=t=in:d=0.6,afade=t=out:st={T_TOT-1.2}:d=1.2,volume=0.28[m];[2:a]atrim=start={J.get('trim',0.4)}:end={LAUGH+0.9},asetpts=PTS-STARTPTS,volume=1.9,adelay={dl}|{dl}[l];[m][l]amix=inputs=2:normalize=0:duration=first,alimiter=limit=0.95[a]',
 '-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-t',str(T_TOT),out],check=True)
print(out,T_TOT)

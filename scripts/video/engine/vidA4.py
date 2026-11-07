#!/usr/bin/env python3
"""d4 'line art hoodies' re-creation (library based): line-draw animation of a breed's classic line art on a paper background,
then 3 hoodie reveals from out/merch_lib (different colour/design/view) on 300-library backgrounds.
usage: python3 vidA4.py cfg.json   cfg: {out,music,ss,breed,draw_bg,label,scenes:[{head,item,bg}],cta}
Layout phone-safe: logo pill y276, heading y436, art/merch y~600-1190, label y1212, CTA y1230 (final)."""
import sys, json, subprocess, glob, io
import numpy as np, cv2, cairosvg
from PIL import Image, ImageDraw, ImageFont
R='/home/claude/alphadog-styles/'; W,H,FPS=1080,1920,24
FB='/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf'; FM='/usr/share/fonts/truetype/google-fonts/Poppins-Medium.ttf'
cfg=json.load(open(sys.argv[1]))
def font(s,f=FB): return ImageFont.truetype(f,s)
def bg(i):
    f=glob.glob(R+f'out/backgrounds/bg_{i:03d}_*.jpg')[0]; return Image.open(f).convert('RGB').resize((W,H))
def pill(txt,size,logo=True,fill=(18,20,26,215)):
    f=font(size); d0=ImageDraw.Draw(Image.new('L',(1,1))); tw=int(d0.textlength(txt,font=f))+(size+18 if logo else 0)
    h=int(size*1.9); im=Image.new('RGBA',(tw+70,h),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,im.width-1,h-1],radius=h//2,fill=fill,outline=(255,255,255,70),width=2); x=32
    if logo:
        lg=Image.open(R+'store/logo.png').convert('RGBA'); lg.thumbnail((int(h*.72),int(h*.72)))
        d.ellipse([x-8,(h-lg.height)//2-2,x-6+lg.width+2,(h+lg.height)//2+2],fill=(255,255,255,255)); im.paste(lg,(x-6,(h-lg.height)//2),lg); x+=lg.width+14
    d.text((x,h//2),txt,font=f,fill=(255,255,255,255),anchor='lm'); return im
def head(txt,size,fill=(255,255,255,255),shadow=True,sp=6,f=FB):
    ft=font(size,f); d0=ImageDraw.Draw(Image.new('L',(1,1))); tw=int(sum(d0.textlength(c,font=ft)+sp for c in txt))
    im=Image.new('RGBA',(tw+40,size*2),(0,0,0,0)); d=ImageDraw.Draw(im); x=20
    for c in txt:
        if shadow: d.text((x+2,size+3),c,font=ft,fill=(0,0,0,140),anchor='lm')
        d.text((x,size),c,font=ft,fill=fill,anchor='lm'); x+=d.textlength(c,font=ft)+sp
    return im
def merch(code,box):
    p,b,c=code.split('/'); im=Image.open(R+f'out/merch_lib/{p}/{b}/{c}.webp').convert('RGBA')
    im=im.crop(im.getchannel('A').getbbox()); s=min(box[0]/im.width,box[1]/im.height); return im.resize((int(im.width*s),int(im.height*s)),Image.LANCZOS)
def shadow(m):
    a=np.array(m.getchannel('A')).astype(np.float32)/255; a=np.pad(a,90); s=cv2.GaussianBlur(a,(0,0),22)*0.55
    sh=Image.new('RGBA',(m.width+180,m.height+180),(0,0,0,0)); sh.putalpha(Image.fromarray((s*255).astype(np.uint8))); return sh
def paste_c(im,ov,cy,alpha=1.0):
    if alpha<=0: return im
    if alpha<1: ov=ov.copy(); ov.putalpha(ov.getchannel('A').point(lambda v:int(v*alpha)))
    im.alpha_composite(ov,((W-ov.width)//2,int(cy-ov.height/2))); return im
def lock(im): p=pill('ALPHADOG STYLES',30); return paste_c(im,p,276)
def tint_top(im):
    ov=np.zeros((H,W,4),np.uint8); yy=np.arange(H)[:,None]; a=(np.clip((560-yy)/330,0,1)*85).astype(np.uint8); ov[...,3]=np.repeat(a,W,1); im.alpha_composite(Image.fromarray(ov)); return im
# ---- line art draw-on data
png=cairosvg.svg2png(url=R+f"store/art/line_classic/{cfg['breed']}_back.svg",output_height=2000)
al=np.array(Image.open(io.BytesIO(png)).convert('RGBA'))[...,3]; yy,xx=np.nonzero(al>40); al=al[yy.min():yy.max()+1,xx.min():xx.max()+1]
AH=590; AW=int(al.shape[1]*AH/al.shape[0]); al=cv2.resize(al,(AW,AH),interpolation=cv2.INTER_AREA).astype(np.float32)/255
ink=(al>0.2).astype(np.uint8); n,lab,st,_=cv2.connectedComponentsWithStats(ink,connectivity=8)
arr=np.full(ink.shape,1e9,np.float32); reached=np.zeros_like(ink); pend=[]
for k,c in enumerate(sorted(range(1,n),key=lambda c:-st[c,4])):
    ys,xs=np.nonzero(lab==c); i=np.argmin(ys); pend.append((0 if k==0 else int(60+(ys[i]/AH)*900),xs[i],ys[i]))
ker=np.ones((3,3),np.uint8); s=0
while True:
    for d,x,y in pend:
        if d==s: reached[y,x]=1; arr[y,x]=s
    new=cv2.dilate(reached,ker)&ink&(1-reached); arr[new>0]=s; reached|=new; s+=1
    if s>max(d for d,_,_ in pend) and new.sum()==0: break
S=s; Y0=598; X0=(W-AW)//2
paper=np.array(bg(cfg['draw_bg']).convert('RGB'),np.float32)[:,:,::-1]
DR=cfg.get('draw_frames',90)
def draw_frame(f):
    t=min(f/float(DR),1.0); cur=S*t**0.85
    m=cv2.GaussianBlur((arr<=cur).astype(np.float32)*al,(0,0),0.6)
    L=np.zeros((H,W),np.float32); L[Y0:Y0+AH,X0:X0+AW]=m; G=np.zeros((H,W),np.float32)
    if t<1:
        tip=((arr<=cur)&(arr>cur-28)).astype(np.float32); G[Y0:Y0+AH,X0:X0+AW]=cv2.GaussianBlur(tip,(0,0),7)
    G=np.clip(G*5,0,1)
    out=paper*(1-L[...,None]*0.96)+np.array([38,34,30],np.float32)*L[...,None]*0.96+G[...,None]*np.array([40,120,215],np.float32)
    im=Image.fromarray(np.clip(out,0,255).astype(np.uint8)[:,:,::-1]).convert('RGBA')
    ink_c=(40,36,32,255)
    im=paste_c(im,head('DRAWN LINE BY LINE',50,ink_c,False),436,min(1,f/10))
    if f>=DR-8: im=paste_c(im,head(cfg['label'],44,ink_c,False,8,FM),1212,min(1,(f-DR+8)/10))
    return lock(im)
def merch_frame(sc,t,cta=None):
    im=bg(sc['bg']).convert('RGBA'); im=tint_top(im)
    pop=(0.94+0.06*(1-np.exp(-t*9)))*(1+0.06*t); m=merch(sc['item'],sc.get('box',(760,640)))
    m=m.resize((int(m.width*pop),int(m.height*pop)),Image.LANCZOS); x=(W-m.width)//2; y=840-m.height//2
    im.alpha_composite(shadow(m),(x+14-90,y+22-90)); im.alpha_composite(m,(x,y)); im=lock(im)
    im=paste_c(im,head(sc['head'],56),436,1)
    if cta:
        c=pill(cta,36,logo=False,fill=(255,255,255,240)); c2=Image.new('RGBA',c.size,(0,0,0,0)); d2=ImageDraw.Draw(c2)
        d2.rounded_rectangle([0,0,c.width-1,c.height-1],radius=c.height//2,fill=(255,255,255,240)); d2.text((c.width//2,c.height//2),cta,font=font(36),fill=(20,20,26,255),anchor='mm'); im=paste_c(im,c2,1250,1)
    return im
def arr_bgr(im): return np.array(im.convert('RGB'))[:,:,::-1]
sc=cfg['scenes']; DUR=cfg.get('dur',[36,36,60]); X=8
out_sil='/tmp/s/_a4_silent.mp4'
p=subprocess.Popen(['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','bgr24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-preset','veryfast','-crf','17','-pix_fmt','yuv420p',out_sil],stdin=subprocess.PIPE)
nd=DR+24; last=None
for f in range(nd): fr=arr_bgr(draw_frame(f)); last=fr; p.stdin.write(fr.tobytes())
for si,s_ in enumerate(sc):
    fin=si==len(sc)-1
    for f in range(DUR[si]):
        fr=arr_bgr(merch_frame(s_,f/24.,cfg['cta'] if (fin and f>=14) else None))
        if f<X: a=(f+1)/(X+1); fr=cv2.addWeighted(last,1-a,fr,a,0)
        p.stdin.write(fr.tobytes())
    last=arr_bgr(merch_frame(s_,99,cfg['cta'] if fin else None))
p.stdin.close(); p.wait()
T=(nd+sum(DUR))/FPS
subprocess.run(['ffmpeg','-y','-v','error','-i',out_sil,'-ss',str(cfg.get('ss',0)),'-i',R+'out/music2/'+cfg['music'],
 '-filter_complex',f'[1:a]atrim=0:{T:.2f},afade=t=in:d=0.4,afade=t=out:st={T-1.2:.2f}:d=1.2,volume=0.7[a]','-map','0:v','-map','[a]','-c:v','copy','-c:a','aac','-b:a','160k','-t',f'{T:.2f}','-movflags','+faststart',R+cfg['out']],check=True)
print('BUILT',cfg['out'],T)

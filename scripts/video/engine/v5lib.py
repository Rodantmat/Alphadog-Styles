import cv2,numpy as np,subprocess,sys,io,cairosvg
sys.path.insert(0,'/tmp/kl')
import video3 as V,cut,hood,cut3,cut4,qa
from PIL import Image,ImageDraw,ImageFont
W,H=1080,1920;FP=V.FP;M='/home/claude/alphadog-styles/store/mk/'
def font(w,s): return ImageFont.truetype(FP%w,s)
def text_img(txt,size,w='Bold',fill=(255,255,255,255),sp=0,shadow=True):
    f=font(w,size);d0=ImageDraw.Draw(Image.new('L',(1,1)));tw=int(sum(d0.textlength(c,font=f)+sp for c in txt)-sp)+8
    im=Image.new("RGBA",(tw+40,size*2),(0,0,0,0));d=ImageDraw.Draw(im);x=20
    for c in txt:
        if shadow: d.text((x+2,size+3),c,font=f,fill=(0,0,0,120),anchor="lm")
        d.text((x,size),c,font=f,fill=fill,anchor="lm");x+=d.textlength(c,font=f)+sp
    return im
def paste_c(im,ov,cy,alpha=1.0):          # centred vertically on cy
    if alpha<=0: return im
    if alpha<1: ov=ov.copy();ov.putalpha(ov.getchannel('A').point(lambda v:int(v*alpha)))
    im.alpha_composite(ov,((W-ov.width)//2,int(cy-ov.height/2)));return im
def bgc(name): return cv2.imread(f'/tmp/kl/bgc/{name}.png').astype(np.float32)
fit=cut3.fit
def item_on(bg,s,t,cy,pop=True,zoom=0.0):
    p=(0.94+0.06*(1-np.exp(-t*9)) if pop else 1.0)*(1+zoom*t)
    sw=int(s.shape[1]*p);shh=int(s.shape[0]*p);ss=cut3.rs(s,(sw,shh))
    x0=W//2-sw//2;y0=int(cy-shh//2)
    A=np.zeros((H,W),np.float32);F=np.zeros((H,W,3),np.float32)
    yy0,yy1=max(y0,0),min(y0+shh,H);A[yy0:yy1,x0:x0+sw]=ss[yy0-y0:yy1-y0,:,3]/255.;F[yy0:yy1,x0:x0+sw]=ss[yy0-y0:yy1-y0,:,:3]
    sh=np.clip(cv2.GaussianBlur(np.roll(A,(30,0),(0,1)),(0,0),30)*0.5+cv2.GaussianBlur(np.roll(A,(6,0),(0,1)),(0,0),5)*0.35,0,0.7)
    yy=np.arange(H,dtype=np.float32)[:,None];tg=np.clip((560-yy)/330,0,1)*0.34
    out=bg*(1-tg[...,None])*(1-sh[...,None]);return out*(1-A[...,None])+F*A[...,None]
def toim(a): return Image.fromarray(cv2.cvtColor(np.clip(a,0,255).astype(np.uint8),cv2.COLOR_BGR2RGB)).convert("RGBA")
def back(im): return cv2.cvtColor(np.array(im.convert("RGB")),cv2.COLOR_RGB2BGR)
LKY=276
def lock(im): return paste_c(im,V.LK,LKY+V.LK.height/2)
def enc(out): return subprocess.Popen(["ffmpeg","-y","-v","error","-f","rawvideo","-pix_fmt","bgr24","-s",f"{W}x{H}","-r","24","-i","-","-c:v","libx264","-preset","veryfast","-crf","17","-pix_fmt","yuv420p",out],stdin=subprocess.PIPE)
def apparel(kind,breed,code,box=(700,640)):
    kw={}
    if kind.startswith('cap'): kw=dict(wthr=60,sat=True)
    im=cv2.imread(f'{M}{kind}/{breed}/{code}.jpg')
    if kind.startswith('cap'):
        r=cut4.cap(im);q=qa.qa(im,qa.canvas(r),kind+breed+code,bottom_exempt=0.2,colour_tol=4000)
        assert q['PASS'],q
    else: r=cut4.safe_matte(im,kind+breed+code,verbose=False)
    return fit(r,*box)

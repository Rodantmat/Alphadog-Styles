from funny import *
import os
PX='/home/claude/alphadog-styles/out/pexels/'
BG=bgc('sea_sunset')
CWD,CHT=490,640
_m={}
def cm(w,h):
    if (w,h) not in _m:
        m=rmask(w,h,34);_m[(w,h)]=(m,m-cv2.erode(m,np.ones((11,11),np.uint8)))
    return _m[(w,h)]
def card(frame,img,cx,cy,s=1.0,al=1.0,rot=0.0):
    h0,w0=img.shape[:2];w,h=int(w0*s),int(h0*s)
    if w<10 or al<=0: return frame
    im=cv2.resize(img,(w,h),interpolation=cv2.INTER_AREA);m,rg=cm(w0,h0);m=cv2.resize(m,(w,h));rg=cv2.resize(rg,(w,h))
    im=im*(1-rg[...,None])+255*rg[...,None];a=m
    if rot:
        M=cv2.getRotationMatrix2D((w/2,h/2),rot,1.0);im=cv2.warpAffine(im,M,(w,h),borderValue=0);a=cv2.warpAffine(a,M,(w,h),borderValue=0)
    x0,y0=int(cx-w/2),int(cy-h/2);xa,xb,ya,yb=max(x0,0),min(x0+w,W),max(y0,0),min(y0+h,H)
    A=np.zeros((H,W),np.float32);A[ya:yb,xa:xb]=a[ya-y0:yb-y0,xa-x0:xb-x0]
    sh=np.clip(cv2.GaussianBlur(np.roll(A,(24,0),(0,1)),(0,0),24)*0.55,0,0.6)*al;fr=frame*(1-sh[...,None])
    F=np.zeros((H,W,3),np.float32);F[ya:yb,xa:xb]=im[ya-y0:yb-y0,xa-x0:xb-x0];A=A*al
    return fr*(1-A[...,None])+F*A[...,None]
def photo(id_,fx,fy,chf):
    im=cv2.imread(f'{PX}{id_}.jpg');h,w=im.shape[:2];ch=h*chf;cw=ch*CWD/CHT
    if cw>w: cw=w;ch=cw*CHT/CWD
    x0=min(max(fx*w-cw/2,0),w-cw);y0=min(max(fy*h-ch/2,0),h-ch)
    c=im[int(y0):int(y0+ch),int(x0):int(x0+cw)];r=cv2.resize(c,(CWD,CHT),interpolation=cv2.INTER_LANCZOS4).astype(np.float32)
    bl=cv2.GaussianBlur(r,(0,0),1.2);return np.clip(r+0.35*(r-bl),0,255)
# id, breed, name, face fx,fy, crop-height frac
S=[('4588005','shiba_inu','SHIBA INU',.47,.60,.52),
   ('14160090','german_shepherd','GERMAN SHEPHERD',.40,.42,.55),
   ('13867936','siberian_husky','HUSKY',.44,.45,.58),
   ('17742008','french_bulldog','FRENCH BULLDOG',.50,.42,.55),
   ('31280056','yorkshire_terrier','YORKIE',.62,.55,.50),
   ('17613872','pembroke_welsh_corgi','CORGI',.50,.38,1.0),
   ('36762252','golden_retriever','GOLDEN RETRIEVER',.48,.40,.55),
   ('18124743','doberman_pinscher','DOBERMAN',.52,.38,.50)]
END=['dachshund','pomeranian','border_collie']
USED=set()
def cands(breed,prev,kinds):
    for k in kinds:
        d=f'/home/claude/alphadog-styles/store/mk/{k}/{breed}'
        if not os.path.isdir(d): continue
        for c in sorted(os.listdir(d)):
            c=c[:-4]
            if c[0] in '25' and c[1:] not in ('WH','AS') and c[1:] not in USED and (not prev or (c[0]!=prev[2][0] and c[1:]!=prev[2][1:] and k!=prev[0])): yield (k,breed,c)
def build(breed,prev,box,start):
    kinds=['tee','hoodie','tank','cap_dad','polo','wtank']
    order=kinds[start:]+kinds[:start]
    for r in cands(breed,prev,order):
        try: m=apparel(*r,box);USED.add(r[2][1:]);return r,m
        except BaseException as e: print('skip',r,repr(e)[:60])
    raise RuntimeError(breed)
sel=[];MP=[];prev=None
for i,s in enumerate(S):
    r,m=build(s[1],prev,(430,520),i%6);sel.append(r);MP.append(m);prev=r
print(sel)
EP=[]
for i,b in enumerate(END):
    r,m=build(b,prev,(330,430),(i+2)%6);EP.append(m);prev=r;print('end',r)
PH=[photo(s[0],*s[3:]) for s in S]
TINT=[(236,225,255),(214,236,255),(222,246,226),(255,236,214),(240,255,255),(226,232,255),(212,243,255),(235,226,250)]
def mcard(item,tint):
    c=np.zeros((CHT,CWD,3),np.float32);yy=np.linspace(0,1,CHT)[:,None,None];t=np.array(tint[::-1],np.float32)
    c[:]=t*(0.96+0.04*yy)+8;return c
cur=[chip(s[2],54,fg=(255,255,255,255),bg=(20,20,20,255)) for s in S]
realc=chip("REAL",34,fg=(20,20,20,255),bg=(255,255,255,255),padx=22,pady=8);oursc=chip("OURS",34,fg=(255,255,255,255),bg=(236,72,60,255),padx=22,pady=8)
eq=Image.new('RGBA',(120,120),(0,0,0,0));d=ImageDraw.Draw(eq);d.ellipse([0,0,119,119],fill=(255,255,255,255));d.rectangle([30,38,90,50],fill=(20,20,20,255));d.rectangle([30,70,90,82],fill=(20,20,20,255))
endchip=chip("SAME SHADES. SAME VIBE.",50,fg=(255,255,255,255),bg=(20,20,20,255));cta=V.cta(CTA_TXT)
CF=29;NC=len(S);TOT=CF*NC+84;p=enc('/tmp/kl/vS1_silent.mp4')
LX,RX,CY=285,795,860
for f in range(TOT):
    fr=BG.copy()
    if f<CF*NC:
        k=f//CF;l=f%CF
        a=sm(l/7);b=sm((l-3)/7)
        fr=card(fr,PH[k],LX-380*(1-a),CY,1.0,min(1,a*1.5),rot=-2.2*(1-a))
        fr=card(fr,mcard(None,TINT[k]),RX+380*(1-b),CY,1.0,min(1,b*1.5),rot=2.2*(1-b))
        fr=blit(fr,MP[k],RX,CY+10,bounce((l-8)/9),min(1,b*2))
        fr=wipe(fr,(l-CF+5)/5 if l>=CF-5 else 0)
        im=toim(fr)
        im=overlay(im,cur[k],540,455,min(1,l/4),scale=bounce(l/7))
        im=overlay(im,realc,LX-150,CY-CHT/2+36,min(1,max(l-5,0)/4));im=overlay(im,oursc,RX+150,CY-CHT/2+36,min(1,max(l-5,0)/4))
        im=overlay(im,eq,540,CY,min(1,max(l-9,0)/3),scale=0.62*bounce((l-9)/7))
    else:
        l=f-CF*NC
        fr=spot(fr,540,900,560,0.2)
        for j,(cx,cy) in enumerate(((200,900),(540,860),(880,900))):
            fr=blit(fr,EP[j],cx,cy,bounce((l-8-7*j)/9),1.0,rot=(-5,0,5)[j])
        im=toim(fr);im=overlay(im,endchip,540,480,1.0,scale=bounce(l/9))
        if l>=20: im=paste_c(im,cta,1262,min(1,(l-20)/10))
    im=paste_c(im,V.LK,300)
    p.stdin.write(back(im).tobytes())
p.stdin.close();p.wait();print('done')

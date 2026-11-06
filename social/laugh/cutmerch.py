# cut merch pieces from store/mk mockups -> out/laugh/cut/<cat>_<code>.png ; usage: cutmerch.py breed cat:code ...
import sys,cv2,numpy as np
sys.path.insert(0,'/home/claude/alphadog-styles/scripts/video/engine')
from rembg import new_session,remove
S=new_session('isnet-general-use');R='/home/claude/alphadog-styles/'
breed=sys.argv[1]
for it in sys.argv[2:]:
    cat,code=it.split(':');im=cv2.imread(f'{R}store/mk/{cat}/{breed}/{code}.jpg');h,w=im.shape[:2]
    if cat!='cap_dad' and code[0] in '134569' and not code[0]=='2':
        pass
    # inset (back view) at fixed rect -> rebuild by mirroring the garment's left half
    g=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY);hasinset=(g[670:1170,670:1170]>=0).all() and (cv2.Canny(g,50,150)[664:668,700:1100].mean()>5 or code[0]!='2') and cat!='cap_dad'
    if cat!='cap_dad' and code[0]!='2':
        d=np.abs(im.astype(np.float32)-255).sum(2);mk=(d>40).astype(np.uint8);mk[640:,640:]=0
        axs=[]
        for y in range(380,640,5):
            xs=np.where(mk[y,:640+0]>0)[0];xs2=np.where(mk[y]>0)[0]
            if len(xs2)>50: axs.append((xs2.min()+xs2.max())/2)
        ax=float(np.median(axs));print(it,'axis',ax)
        out=im.copy()
        for y in range(655,1185):
            for x in range(655,1185):
                xm=int(round(2*ax-x))
                if 0<=xm<655: out[y,x]=im[y,xm]
        im=out;inset=True
    else: inset=False
    # contrast copy (pale garments on white) for the matte
    d=np.abs(im.astype(np.float32)-255).sum(2);a0=np.clip(cv2.GaussianBlur(d,(0,0),1.0)/55.,0,1)[...,None]
    cm=(im*a0+np.array([70,40,30],np.float32)*(1-a0)).astype(np.uint8)
    rgb=cv2.cvtColor(cm,cv2.COLOR_BGR2RGB)
    a=np.array(remove(rgb,session=S,only_mask=True,alpha_matting=True,alpha_matting_foreground_threshold=235,alpha_matting_background_threshold=15,alpha_matting_erode_size=8)).astype(np.float32)/255
    dd=cv2.GaussianBlur(np.abs(im.astype(np.float32)-255).sum(2),(0,0),1.0)
    hard=((a>0.5)&(dd>45)).astype(np.uint8);hard=cv2.morphologyEx(hard,cv2.MORPH_CLOSE,np.ones((7,7),np.uint8));n,l,st,_=cv2.connectedComponentsWithStats(hard);hard=(l==1+np.argmax(st[1:,4])).astype(np.uint8)
    inv=(1-hard).astype(np.uint8);n,l,st,_=cv2.connectedComponentsWithStats(inv);hard=(l!=l[0,0]).astype(np.uint8)
    hard=cv2.erode(hard,np.ones((5,5),np.uint8))
    a=cv2.GaussianBlur(hard.astype(np.float32),(0,0),1.1)
    a=np.clip((a-0.3)/0.5,0,1)
    # remove white spill on edge pixels
    col=im.astype(np.float32);aa=np.maximum(a[...,None],0.35);edge=((a>0)&(a<0.98))[...,None]
    dec=np.clip((col-(1-aa)*255)/aa,0,255);col=np.where(edge,dec,col)
    ys,xs=np.where(a>0.05);y0,y1,x0,x1=ys.min(),ys.max(),xs.min(),xs.max()
    out=np.dstack([col.astype(np.uint8),(a*255).astype(np.uint8)])[y0:y1+1,x0:x1+1]
    cv2.imwrite(f'{R}out/laugh/cut/{cat}_{code}.png',out);print(it,out.shape)
    bgc=np.full(out.shape[:2]+(3,),(120,120,120),np.float32);al=out[...,3:]/255.
    cv2.imwrite(f'{R}out/laugh/cut/_chk_{cat}_{code}.jpg',(out[...,:3]*al+bgc*(1-al)).astype(np.uint8))

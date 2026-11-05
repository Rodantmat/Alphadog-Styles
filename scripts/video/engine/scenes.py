import numpy as np,cv2,math
from PIL import Image,ImageDraw,ImageFilter
from bgtex import finish,grad,W,H
def lerp(a,b,t): return np.array(a,np.float32)*(1-t)+np.array(b,np.float32)*t
def ridge(seed,base,amp,rough=1.0,x=None):
    rs=np.random.RandomState(seed);x=np.arange(W,dtype=np.float32)
    y=np.zeros(W,np.float32)
    for k,(f,a) in enumerate([(1.0,1),(2.3,.55),(5.1,.28),(11.7,.13),(26,.06)]):
        y+=a*np.sin(x/W*2*math.pi*f*rough+rs.rand()*6.28)
    return base+amp*y/1.6
def mountains(sky_top,sky_bot,sun,sun_xy,far,near,layers=5,seed=0,haze=0.55,base0=1040,pines=True,stars=0):
    img=grad(sky_top,sky_bot,90)
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    if sun is not None:
        d=np.sqrt((xx-sun_xy[0])**2+(yy-sun_xy[1])**2)
        glow=np.exp(-(d/260)**2)[...,None]*0.55+np.exp(-(d/90)**2)[...,None]*0.5
        img=img*(1-glow)+np.array(sun,np.float32)*glow
        disc=(d<62).astype(np.float32)[...,None];disc=cv2.GaussianBlur(disc,(0,0),1.5)[...,None] if disc.ndim==3 else disc
    rs=np.random.RandomState(seed+99)
    if stars:
        for _ in range(stars):
            x,y=rs.randint(0,W),rs.randint(0,int(H*0.55));r=rs.choice([1,1,1,2]);cv2.circle(img,(x,y),r,(255,250,235),-1,cv2.LINE_AA)
        img=cv2.GaussianBlur(img,(0,0),0.6)
    for i in range(layers):
        t=i/(layers-1);col=lerp(far,near,t)
        base=base0+i*120+ (0 if i==0 else 0);amp=70+i*18
        y=ridge(seed+i*7,base,amp,0.8+0.25*i)
        mask=(yy>y[None,:].repeat(H,0)).astype(np.float32)
        mask=cv2.GaussianBlur(mask,(0,0),1.2)[...,None]
        fog=np.clip(1-(yy-y[None,:].repeat(H,0))/260,0,1)[...,None]*haze*(1-t)    # mist at ridge tops
        layer=col*(1-fog)+lerp(sky_bot,far,0.25)*fog
        img=img*(1-mask)+layer*mask
    if pines:
        im=Image.fromarray(np.clip(img,0,255).astype(np.uint8));d=ImageDraw.Draw(im);rs=np.random.RandomState(seed+5)
        pc=tuple(int(v) for v in lerp(near,(0,0,0),0.55))
        for _ in range(34):
            x=rs.randint(-30,W+30);h=rs.randint(260,520);bw=h*0.32;yb=H+20-int((rs.rand()**2)*160)
            for j in range(5):
                top=yb-h+j*h*0.19;w=bw*(0.35+0.2*j)
                d.polygon([(x,top),(x-w,top+h*0.28),(x+w,top+h*0.28)],fill=pc)
            d.rectangle([x-6,yb-h*0.18,x+6,yb],fill=pc)
        img=np.array(im,np.float32)
    return finish(img,seed,0.28,2.5)
def sea_sunset(sky_top,sky_mid,sky_bot,sun,water_top,water_bot,seed=0):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);hz=1050
    t=np.clip(yy/hz,0,1)[...,None];sky=np.where(t<0.6,lerp(sky_top,sky_mid,t/0.6),lerp(sky_mid,sky_bot,(t-0.6)/0.4)) if False else None
    sky=np.zeros((H,W,3),np.float32)
    for y in range(H):
        u=min(y/hz,1.0);sky[y,:]=lerp(sky_top,sky_mid,u/0.55) if u<0.55 else lerp(sky_mid,sky_bot,(u-0.55)/0.45)
    d=np.sqrt((xx-W*0.5)**2+(yy-(hz-70))**2);glow=np.exp(-(d/340)**2)[...,None]*0.6+np.exp(-(d/105)**2)[...,None]*0.9
    sky=sky*(1-np.clip(glow,0,1))+np.array(sun,np.float32)*np.clip(glow,0,1)
    water=np.zeros((H,W,3),np.float32)
    for y in range(hz,H): water[y,:]=lerp(water_top,water_bot,min((y-hz)/(H-hz),1.0))
    ph=(yy-hz)/60.0;wav=np.sin(ph*math.pi*2+np.sin(xx/140.+yy/220.)*2.0)
    stripe=np.clip(wav,0,1)*np.exp(-((xx-W*0.5)/(120+(yy-hz)*0.55))**2)*np.clip((yy-hz)/40,0,1)
    water=water+stripe[...,None]*np.array(sun,np.float32)*0.5*(yy>hz)[...,None]
    img=np.where((yy>hz)[...,None],water,sky);img=cv2.GaussianBlur(img,(0,0),0.8)
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8))
    img=np.array(im,np.float32);return finish(img,seed,0.3,2.5)
def bokeh(c1,c2,cols,seed=0,n=70):
    img=grad(c1,c2,90);rs=np.random.RandomState(seed);L=np.zeros((H,W,3),np.float32)
    for _ in range(n):
        x,y=rs.randint(0,W),rs.randint(0,H);r=rs.randint(30,110);c=np.array(cols[rs.randint(len(cols))],np.float32);a=rs.uniform(0.18,0.5)
        o=np.zeros((H,W),np.float32);cv2.circle(o,(x,y),r,1.0,-1,cv2.LINE_AA);o=cv2.GaussianBlur(o,(0,0),3)
        ring=np.zeros((H,W),np.float32);cv2.circle(ring,(x,y),r,1.0,3,cv2.LINE_AA);ring=cv2.GaussianBlur(ring,(0,0),2)
        L+=((o*a*0.7+ring*a*0.6)[...,None])*c
    img=img+L;return finish(np.clip(img,0,255),seed,0.34,3.0)
def gift(paper,motif,ribbon,seed=0,style='dots'):
    img=np.zeros((H,W,3),np.float32);img[:]=np.array(paper,np.float32)
    im=Image.fromarray(img.astype(np.uint8));d=ImageDraw.Draw(im);rs=np.random.RandomState(seed)
    step=96
    for j,y in enumerate(range(-step,H+step,step)):
        for i,x in enumerate(range(-step,W+step,step)):
            xx=x+(step//2 if j%2 else 0)
            if style=='dots': d.ellipse([xx-9,y-9,xx+9,y+9],fill=tuple(motif))
            elif style=='stars':
                pts=[(xx+ (20 if k%2==0 else 8)*math.cos(math.pi/5*k-math.pi/2), y+(20 if k%2==0 else 8)*math.sin(math.pi/5*k-math.pi/2)) for k in range(10)];d.polygon(pts,fill=tuple(motif))
            elif style=='paws':
                d.ellipse([xx-14,y-4,xx+14,y+20],fill=tuple(motif))
                for dx,dy in ((-18,-14),(-6,-24),(8,-24),(20,-14)): d.ellipse([xx+dx-6,y+dy-6,xx+dx+6,y+dy+6],fill=tuple(motif))
    # vertical ribbon + horizontal ribbon
    rb=tuple(ribbon);d.rectangle([W//2-70,0,W//2+70,H],fill=rb);d.rectangle([0,1480,W,1620],fill=rb)
    pre=np.array(im,np.float32).copy()
    # bow at the crossing
    for sgn in (-1,1):
        d.ellipse([W//2+sgn*150-130,1550-95,W//2+sgn*150+130,1550+95],outline=rb,width=46)
    d.ellipse([W//2-55,1495,W//2+55,1605],fill=tuple(int(c*0.8) for c in rb))
    img=np.array(im.filter(ImageFilter.GaussianBlur(0.6)),np.float32)
    # taper the vertical ribbon into the paper behind the headline zone
    base=np.zeros((H,W,3),np.float32);base[:]=np.array(paper,np.float32)
    yy0,xx0=np.mgrid[0:H,0:W].astype(np.float32);fade=np.clip((yy0-480)/260,0,1)[...,None];inv=((np.abs(xx0-W/2)<72)&(yy0<1450))[...,None]
    img=np.where(inv,base*(1-fade)+img*fade,img)
    # ribbon sheen
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);sheen=np.exp(-((xx-W/2)/30)**2)[...,None]*0.18*255
    img=img+sheen*(np.abs(xx-W/2)<70)[...,None]*0.5
    return finish(np.clip(img,0,255),seed,0.32,2.0)
def lake(sky_top,sky_bot,water,hill,seed=0):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);hz=1000
    img=np.zeros((H,W,3),np.float32)
    for y in range(H):
        img[y,:]=lerp(sky_top,sky_bot,y/hz) if y<hz else lerp(water,np.array(water)*0.55,(y-hz)/(H-hz))
    y=ridge(seed,hz-70,60,0.9);m=(yy>y[None,:].repeat(H,0))&(yy<hz);img[m]=np.array(hill,np.float32)
    ref=cv2.flip(img[hz-300:hz],0);rip=np.sin(yy[hz:hz+300]/9+np.sin(xx[hz:hz+300]/60)*3)*0.5+0.5
    img[hz:hz+300]=img[hz:hz+300]*0.55+ref*0.45*(0.75+0.25*rip[...,None])
    return finish(cv2.GaussianBlur(img,(0,0),0.9),seed,0.3,2.5)
def forest(c1,c2,trunk,seed=0):
    img=grad(c1,c2,90);rs=np.random.RandomState(seed)
    for depth,(al,wmin,wmax,n,bl) in enumerate([(0.18,26,46,10,12),(0.3,36,64,8,6),(0.5,54,96,6,2)]):
        L=np.zeros((H,W),np.float32)
        for _ in range(n):
            x=rs.randint(-20,W+20);w=rs.randint(wmin,wmax);lean=rs.uniform(-0.04,0.04)
            pts=np.array([[x-w/2,0],[x+w/2,0],[x+w/2+lean*H,H],[x-w/2+lean*H,H]],np.int32);cv2.fillPoly(L,[pts],1.0)
        L=cv2.GaussianBlur(L,(0,0),bl)*al;img=img*(1-L[...,None])+np.array(trunk,np.float32)*L[...,None]
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32);rays=np.clip(np.sin((xx+yy*0.55)/95)*0.5+0.5,0,1)**6*0.16
    img=img+rays[...,None]*np.array([200,230,255],np.float32)*(1-yy/H*0.7)[...,None]
    return finish(np.clip(img,0,255),seed,0.34,2.5)
def meadow(sky_top,sky_bot,grass,flowers,seed=0):
    img=grad(sky_top,sky_bot,90);yy,xx=np.mgrid[0:H,0:W].astype(np.float32);rs=np.random.RandomState(seed)
    for k,(base,amp,col) in enumerate([(1000,50,lerp(grass,(255,255,255),0.25)),(1120,60,grass),(1260,70,np.array(grass)*0.75)]):
        y=ridge(seed+k,base,amp,0.9);m=(yy>y[None,:].repeat(H,0)).astype(np.float32)[...,None];img=img*(1-m)+np.array(col,np.float32)*m
    im=Image.fromarray(np.clip(img,0,255).astype(np.uint8));d=ImageDraw.Draw(im)
    for _ in range(520):
        y=rs.randint(1060,H);s=0.4+(y-1060)/860*1.6;x=rs.randint(0,W);c=tuple(flowers[rs.randint(len(flowers))]);r=int(5*s)+2
        for a in range(5): d.ellipse([x+math.cos(a*1.256)*r*1.2-r,y+math.sin(a*1.256)*r*1.2-r,x+math.cos(a*1.256)*r*1.2+r,y+math.sin(a*1.256)*r*1.2+r],fill=c)
        d.ellipse([x-r*0.6,y-r*0.6,x+r*0.6,y+r*0.6],fill=(250,220,90))
    img=cv2.GaussianBlur(np.array(im,np.float32),(0,0),0.9);return finish(img,seed,0.28,2.5)
if __name__=="__main__":
    S={}
    S['mtn_dawn']=mountains((46,32,90),(255,150,110),(255,205,130),(780,880),(200,120,150),(36,28,58),seed=1)
    S['mtn_noon']=mountains((70,150,235),(190,225,250),(255,255,235),(300,300),(150,190,225),(28,70,60),seed=2,haze=0.7)
    S['mtn_dusk']=mountains((22,24,70),(235,110,120),(255,170,120),(300,960),(150,90,140),(18,20,46),seed=3)
    S['camp_night']=mountains((6,10,30),(30,48,90),None,(0,0),(30,44,84),(8,14,28),seed=4,haze=0.35,stars=380,base0=1090)
    S['sea_sunset']=sea_sunset((60,40,110),(220,100,120),(255,170,110),(255,225,150),(120,70,120),(26,22,60),seed=5)
    S['bokeh_cafe']=bokeh((24,38,58),(10,16,28),[(255,190,110),(255,150,80),(255,220,160),(230,120,70)],seed=6)
    S['bokeh_snow']=bokeh((18,34,70),(10,16,40),[(255,255,255),(200,225,255),(255,210,150),(160,200,255)],seed=7,n=90)
    S['gift_red']=gift((150,24,38),(215,70,70),(245,235,230),seed=8,style='dots')
    S['gift_green']=gift((34,92,52),(90,170,110),(235,190,70),seed=9,style='stars')
    S['gift_blue']=gift((28,58,118),(90,130,190),(250,205,120),seed=10,style='paws')
    S['gift_plum']=gift((80,34,88),(140,90,150),(245,215,150),seed=11,style='stars')
    S['lake_dusk']=lake((60,45,110),(245,170,140),(110,80,130),(30,28,60),seed=12)
    S['forest_mist']=forest((70,105,80),(20,42,32),(10,26,18),seed=13)
    S['meadow']=meadow((235,190,120),(250,230,190),(70,150,80),[(255,255,255),(110,140,255),(130,200,255),(210,160,255)],seed=14)
    for k,v in S.items(): cv2.imwrite(f'/tmp/kl/bgc/{k}.png',v.astype(np.uint8))
    ks=list(S);t=[cv2.resize(S[k].astype(np.uint8),(270,480)) for k in ks]
    cv2.imwrite('/tmp/kl/scn/sheet.jpg',np.vstack([np.hstack(t[:7]),np.hstack(t[7:])]));print(ks)

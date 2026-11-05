from funny import *
BG=bgc('bokeh_cafe')
clip=Clip('1212',2.0,cx=0.60)
items=[('tee','boston_terrier','2CR'),('hoodie','boston_terrier','5LB'),('cap_dad','boston_terrier','2DP')]
PR=[apparel(k,b,c,(700,600)) for k,b,c in items]
assert all(items[i][0]!=items[i+1][0] and items[i][2][0]!=items[i+1][2][0] and items[i][2][1:]!=items[i+1][2][1:] for i in range(2))
cap1=chip("ME WHEN I HEAR THE",46);cap2=chip("SNACK DRAWER OPEN",46)
pay=chip("EVERY. SINGLE. TIME.",54,fg=(255,255,255,255),bg=(236,72,60,255))
punch=chip("BOSTON TERRIER MOOD",64,fg=(255,255,255,255),bg=(20,20,20,255))
cta=V.cta(CTA_TXT)
T=276;SW=144;p=enc('/tmp/kl/vF1_silent.mp4')
for f in range(T):
    fr=BG.copy()
    if f<SW+22:
        t=f/24;tt=sm((f-SW)/22)
        s=(0.88+0.12*bounce(f/9)) if f<9 else 1.0
        s=s*(1-0.55*tt);cy=1020-440*tt;al=1-tt
        fr=put_window(fr,clip.win(t,punch=0.05*t/6),540,cy,s,al)
    if f>=SW+8:
        k=min((f-SW-8)//34,2) if f<SW+8+34*3 else 2
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

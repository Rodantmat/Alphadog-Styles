from funny import *
BG=paws()
cuts=[ # clip id, start, cx, caption, breed chip, merch
 ('45843',0.15,0.5,"ME WHEN SOMEONE SAYS 'WALK'","PUG",('tee','pug','5LB')),
 ('15933',3.6,0.5,"LEAVING THE POOL LIKE","CHIHUAHUA",('hoodie','chihuahua','2SA')),
 ('34922',6.9,0.45,"HI. I'M THE BABY.","ROTTWEILER",('tank','rottweiler','5HE')),
 ('50672',3.0,0.45,"CATCHING FEELINGS","PIT BULL",('cap_dad','american_pit_bull_terrier','2DB')),
 ('45834',1.0,0.5,"AFTER ONE (1) ZOOMIE","HUSKY",('tee','siberian_husky','5CR')),
 ('45868',0.5,0.5,"BALL IS LIFE","CORGI",('hoodie','pembroke_welsh_corgi','2GR')),
]
for i in range(len(cuts)-1):
    a,b=cuts[i][5],cuts[i+1][5]
    assert a[0]!=b[0] and a[2][0]!=b[2][0] and a[2][1:]!=b[2][1:],(a,b)
clips=[Clip(c[0],c[1],c[2]) for c in cuts]
PR=[apparel(*c[5],(420,420)) for c in cuts]
caps=[chip(c[3],46) for c in cuts];bchips=[chip(c[4],42,fg=(255,255,255,255),bg=(236,72,60,255)) for c in cuts]
END=[('tee','boston_terrier','2CR'),('hoodie','german_shepherd','5LB'),('tank','border_collie','2HE')]
EP=[apparel(k,b,c,(330,430)) for k,b,c in END]
endchip=chip("WHICH ONE IS YOURS?",62,fg=(255,255,255,255),bg=(20,20,20,255));cta=V.cta(CTA_TXT)
CF=34;NC=len(cuts);TOT=CF*NC+84;p=enc('/tmp/kl/vF2_silent.mp4')
for f in range(TOT):
    fr=BG.copy();im=None
    if f<CF*NC:
        k=f//CF;l=f%CF;t=l/24
        fr=put_window(fr,clips[k].win(t,punch=0.06*l/CF),540,1020,1.0,1.0)
        fr=blit(fr,PR[k],790,1245,bounce((l-7)/9),1.0,rot=-7)
        fr=wipe(fr,(l-CF+5)/5 if l>=CF-5 else 0)
        if k>0 and l<5: fr=wipe(fr,0.5+l/10.0) if False else fr
        im=toim(fr)
        im=overlay(im,caps[k],540,455,min(1,l/4),scale=bounce(l/7))
        im=overlay(im,bchips[k],330,1330,min(1,max(l-3,0)/4),scale=bounce((l-3)/7))
    else:
        l=f-CF*NC
        for j,(cx,cy) in enumerate(((200,920),(540,880),(880,920))):
            fr=blit(fr,EP[j],cx,cy,bounce((l-8-7*j)/9),1.0,rot=(-5,0,5)[j])
        im=toim(fr)
        im=overlay(im,endchip,540,470,1.0,scale=bounce(l/9))
        if l>=20: im=paste_c(im,cta,1262,min(1,(l-20)/10))
    im=paste_c(im,V.LK,300)
    p.stdin.write(back(im).tobytes())
p.stdin.close();p.wait();print('done')

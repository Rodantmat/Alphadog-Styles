from v5lib import *
def render(out,scenes,cta_text,total=240,xf=4):
    """scenes: list of dict(bg,item=(kind,breed,code,box),head,hs,lines,ls,cy,start,end,cta)"""
    cache={}
    for s in scenes:
        k=s['item']
        if k not in cache: cache[k]=apparel(*k)
    p=enc(out);last=None;first_f={}
    for f in range(total):
        sc=[s for s in scenes if s['start']<=f<s['end']][0]
        t=min((f-sc.get('t0',sc['start']))/24.,1.5);bg=bgc(sc['bg'])
        im=lock(toim(item_on(bg,cache[sc['item']],t,sc.get('cy',905),zoom=sc.get('zoom',0.05))))
        for (f0,f1,tx,hs) in sc['texts']:
            if f0<=f<f1:
                tl=tx if isinstance(tx,list) else [tx]
                for i,h in enumerate(tl): im=paste_c(im,text_img(h,hs,'Bold',sp=6),436+i*(hs+14),min(1,(f-f0)/6))
        for i,l in enumerate(sc.get('lines',[])): im=paste_c(im,text_img(l,sc.get('ls',46),'Bold',sp=2),sc.get('ly',560)+i*62,min(1,max(0,(f-sc['start']-6)/8)))
        if sc.get('cta') and f>=sc.get('cta_f',sc['start']): im=paste_c(im,V.cta(cta_text),1190,min(1,(f-sc.get('cta_f',sc['start']))/8))
        fr=back(im)
        if last is not None and f==sc['start']:
            pass
        if last is not None and f-sc['start']<xf and sc['start']>0:
            a=(f-sc['start']+1)/(xf+1.);fr=cv2.addWeighted(last,1-a,fr,a,0)
        p.stdin.write(fr.tobytes());
        if f==sc['end']-1: last=back(im)
    p.stdin.close();p.wait()

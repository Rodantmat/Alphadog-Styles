import cv2,numpy as np,json,os,glob,sys
TH=sys.argv[1] if len(sys.argv)>1 else 'line'
r=json.load(open('out/eyes/merged_line.json' if TH=='line' else 'out/eyes/merged_geo_sets.json')); OD='out/eye_comp' if TH=='line' else 'out/eye_comp_geo'; os.makedirs(OD,exist_ok=True)
def boxes(n,W,H):
    k=[x for x in r if x.endswith(n+'.jpg')][0]; o=[]
    for e in r[k]:
        if 'box_2d' not in e: e={'box_2d':json.loads(e['box'])}
        y0,x0,y1,x1=e['box_2d']; o.append((x0*W/1000,y0*H/1000,x1*W/1000,y1*H/1000))
    return o
A='all' if TH=='line' else 'geo'
log={}
for f in sorted(glob.glob(f'out/sets/{TH}_p*/*.jpg')):
    n=os.path.basename(f)[:-4]; s,v=n.split('__')
    if v=='cool': continue
    o=cv2.imread(f,0); H,W=o.shape; mask=np.zeros((H,W),np.uint8)
    for x0,y0,x1,y1 in boxes(n,W,H):
        p=max(6,0.35*max(x1-x0,y1-y0)); mask[max(0,int(y0-p)):int(y1+p),max(0,int(x0-p)):int(x1+p)]=1
    best=None
    for c in 'abcd':
        p=[q for q in (f'out/eye_{A}_0/E_{s}_{v}__{c}.jpg',f'out/eye_{A}_1/E_{s}_{v}__{c}.jpg') if os.path.exists(q)]
        if not p: continue
        g=cv2.imread(p[0],0)
        if g.shape!=o.shape: g=cv2.resize(g,(W,H),interpolation=cv2.INTER_AREA)
        ob=(o<128); gb=(g<128); out_=(ob!=gb)&(mask==0)
        drift=out_.sum()/max(1,ob.sum())
        inside=((ob!=gb)&(mask>0)).sum()
        if best is None or drift<best[0]: best=(drift,c,g,inside)
    if best is None: log[n]='nocand'; continue
    d,c,g,ins=best
    out=o.copy(); out[mask>0]=g[mask>0]
    cv2.imwrite(f'{OD}/{n}.jpg',out,[cv2.IMWRITE_JPEG_QUALITY,95]); log[n]=(c,round(float(d),4),int(ins))
json.dump(log,open(f'{OD}/log.json','w'),indent=0)
import statistics
print(len(log), statistics.median([v[1] for v in log.values() if v!='nocand']), max(v[1] for v in log.values() if v!='nocand'))
for k,v in sorted(log.items(), key=lambda kv: -kv[1][1])[:8]: print(k,v)

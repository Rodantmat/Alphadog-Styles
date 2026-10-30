import cv2,numpy as np,json,sys,glob,os
D=sys.argv[1]; side=sys.argv[2]; out=sys.argv[3]
r=json.load(open('out/eyes/merged_line.json' if 'geo' not in D else 'out/eyes/merged_geo_sets.json'))
files=sorted(glob.glob(f'{D}/*.jpg')); tiles=[]
for f in files:
    n=os.path.basename(f)[:-4]; g=cv2.imread(f); H,W=g.shape[:2]
    k=[x for x in r if x.endswith(n+'.jpg')][0]; bs=[]
    for e in r[k]:
        if 'box_2d' not in e: e={'box_2d':json.loads(e['box'])}
        y0,x0,y1,x1=e['box_2d']; bs.append((x0*W/1000,y0*H/1000,x1*W/1000,y1*H/1000))
    bs=[b for b in bs if (b[0]+b[2])/2 < W*(0.5 if side=='front' else 2)] if side=='front' else [b for b in bs if (b[0]+b[2])/2 >= W*0.5]
    if not bs: tiles.append(np.full((150,360,3),200,np.uint8)); continue
    x0=min(b[0] for b in bs)-12;x1=max(b[2] for b in bs)+12;y0=min(b[1] for b in bs)-12;y1=max(b[3] for b in bs)+12
    c=g[max(0,int(y0)):int(y1),max(0,int(x0)):int(x1)]; sc=min(360/c.shape[1],150/c.shape[0])
    c=cv2.resize(c,None,fx=sc,fy=sc,interpolation=cv2.INTER_CUBIC); t=np.full((150,360,3),255,np.uint8); t[:c.shape[0],:c.shape[1]]=c
    cv2.putText(t,n[:22],(2,146),cv2.FONT_HERSHEY_SIMPLEX,0.38,(0,0,200),1); cv2.rectangle(t,(0,0),(359,149),(180,180,180),1); tiles.append(t)
while len(tiles)%5: tiles.append(np.full((150,360,3),255,np.uint8))
rows=[np.hstack(tiles[i:i+5]) for i in range(0,len(tiles),5)]
h=len(rows)//2
cv2.imwrite(out+'_1.png',np.vstack(rows[:h])); cv2.imwrite(out+'_2.png',np.vstack(rows[h:]))

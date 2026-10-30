import cv2,numpy as np,json,sys
r=json.load(open('out/eyes/merged_line.json')); D=sys.argv[1]; out=sys.argv[2]
rows=[]
for n in sys.argv[3:]:
    g=cv2.imread(f'{D}/{n}.jpg'); H,W=g.shape[:2]; o=[]
    k=[x for x in r if x.endswith(n+'.jpg')][0]
    for e in r[k]:
        if 'box_2d' not in e: e={'box_2d':json.loads(e['box'])}
        y0,x0,y1,x1=e['box_2d']; cx,cy=(x0+x1)/2*W/1000,(y0+y1)/2*H/1000
        c=g[max(0,int(cy-30)):int(cy+30),max(0,int(cx-30)):int(cx+30)]; o.append(cv2.resize(c,(200,200),interpolation=cv2.INTER_CUBIC))
    rows.append(np.hstack(o))
cv2.imwrite(out,np.vstack(rows))

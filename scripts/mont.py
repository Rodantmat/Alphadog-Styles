import cv2,sys,numpy as np
# usage: mont.py out.png img1 img2 ... (2 columns, 632 wide)
out=sys.argv[1]; fs=sys.argv[2:]
t=[cv2.putText(cv2.resize(cv2.imread(f),(632,424)),f.split('/')[-1][:-4],(8,22),cv2.FONT_HERSHEY_SIMPLEX,.6,(0,0,200),2) for f in fs]
if len(t)%2: t.append(np.full_like(t[0],255))
rows=[np.hstack(t[i:i+2]) for i in range(0,len(t),2)]
cv2.imwrite(out,np.vstack(rows))

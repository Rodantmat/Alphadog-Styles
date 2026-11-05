import cv2,numpy as np,cut3,cut4
HD='/home/claude/alphadog-styles/store/mk/hoodie/'
def back(breed,code,f=2.3):
    im=cv2.imread(f'{HD}{breed}/{code}.jpg');h,w=im.shape[:2]
    c=im[int(h*0.565):int(h*0.975),int(w*0.565):int(w*0.975)].copy()
    r=cut4.safe_matte(c,'hoodback'+breed+code,verbose=True)
    rgb=cv2.resize(r[...,:3],None,fx=f,fy=f,interpolation=cv2.INTER_LANCZOS4)
    rgb=cv2.addWeighted(rgb,1.45,cv2.GaussianBlur(rgb,(0,0),1.5),-0.45,0)
    a=cv2.resize(r[...,3],None,fx=f,fy=f,interpolation=cv2.INTER_CUBIC).astype(np.float32)/255
    a=cv2.GaussianBlur(a,(0,0),1.8);a=np.clip((a-0.42)/0.22,0,1);a=cv2.GaussianBlur(a,(0,0),0.9)
    return np.dstack([rgb,(a*255).astype(np.uint8)])

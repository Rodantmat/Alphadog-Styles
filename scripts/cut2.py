import sys,os,numpy as np,cv2
from rembg import remove,new_session
from PIL import Image
s=new_session("isnet-general-use")
def cutout(f):
    im=Image.open(f).convert("RGB"); a=np.asarray(im)
    ai=np.asarray(remove(im,session=s,post_process_mask=True))[...,3].astype(np.float32)/255
    h,w=a.shape[:2]
    border=np.concatenate([a[0],a[-1],a[:,0],a[:,-1]])
    white_bg=(border.min(axis=1)>=250).mean()>0.9
    if not white_bg: return im,ai,False
    near=(a.min(axis=2)>=249).astype(np.uint8)
    n,lab=cv2.connectedComponents(near,connectivity=4)
    edge=set(lab[0])|set(lab[-1])|set(lab[:,0])|set(lab[:,-1]); edge.discard(0)
    bg=np.isin(lab,list(edge))
    prod=(~bg).astype(np.float32)
    prod=cv2.GaussianBlur(prod,(0,0),0.8)
    k=cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(41,41))
    near_ai=cv2.dilate((ai>0.3).astype(np.uint8),k).astype(np.float32)
    # drop pale shadow: product pixels far from isnet foreground
    prod=prod*near_ai
    alpha=np.maximum(ai,prod)
    # remove tiny specks
    m=(alpha>0.5).astype(np.uint8); n,l,st,_=cv2.connectedComponentsWithStats(m,connectivity=8)
    keep=np.zeros(n,bool); 
    if n>1:
        big=st[1:,4].max(); keep[1:]=st[1:,4]>=0.02*big
    alpha=alpha*keep[l]
    return im,alpha,True
def save(f,out):
    im,al,wb=cutout(f)
    rgba=np.dstack([np.asarray(im),(al*255).astype(np.uint8)])
    Image.fromarray(rgba,"RGBA").save(out); return wb
if __name__=="__main__":
    for f in sys.argv[1:]:
        o="/tmp/cut/h_"+f.split('/')[-2]+"_"+os.path.basename(f)[:-4]+".png"; save(f,o)
        r=Image.open(o);bg=Image.new("RGB",r.size,(0,0,0));bg.paste(r,mask=r.split()[3]);bg.save(o[:-4]+"_blk.jpg")

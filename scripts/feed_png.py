"""Pack a feed file (CSV/XLSX) into a lossless PNG (gzip bytes in RGB pixels, 4-byte length header) so a marketplace page whose
CSP blocks fetch() can still load it as a CORS image and rebuild the exact file in the browser. Usage: feed_png.py FILE..."""
import gzip,struct,sys,math
from PIL import Image
for f in sys.argv[1:]:
    raw=gzip.compress(open(f,"rb").read(),9,mtime=0); data=struct.pack(">I",len(raw))+raw
    w=1024; px=math.ceil(len(data)/3); h=math.ceil(px/w); data+=b"\0"*(w*h*3-len(data))
    Image.frombytes("RGB",(w,h),data).save(f+".png",optimize=True); print(f+".png",w,h,len(raw))

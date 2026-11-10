#!/usr/bin/env python3
"""ptrans - THE way to get a trimmed (transparent-background) Printify picture. Owner-approved 2026-11-09. Never use AI background removal for Printify pictures.
Printify's own image server returns the exact cut-out (real alpha: hair, mesh holes, hat brims) when asked for a PNG with transparent_background=true. No login needed.
  url = https://images.printify.com/mockup/{pid}/{variant}/{camera}/x.png?camera_label=front&t={ms}&s={size}&transparent_background=true&use_cache=false
Camera ids per product + what each shows (flat/person/scene/chart): docs/printify_cameras.json. Camera ids are valid for every colour (variant) of the product.
Scene pictures (plants, couch, chair, flat-lay) come back WITHOUT transparency: post them as-is (cover_crop) or skip. Size charts / blanks are never used.
Network: images.printify.com is reachable only from GitHub Actions runners (not the Claude sandbox)."""
import io,time,json,urllib.request,os
from PIL import Image
CAMS=None
def cams():
    global CAMS
    if CAMS is None: CAMS=json.load(open(os.path.join(os.path.dirname(__file__),"../../docs/printify_cameras.json")))
    return CAMS
def url(pid,variant,cam,size=2048):
    return f"https://images.printify.com/mockup/{pid}/{variant}/{cam}/x.png?camera_label=front&t={int(time.time()*1000)}&s={size}&transparent_background=true&use_cache=false"
def fetch(pid,variant,cam,size=2048,tries=3):
    """returns (PIL RGBA tight-cropped, transparent_fraction) ; transparent_fraction<0.08 => scene/uncut picture"""
    for k in range(tries):
        try:
            b=urllib.request.urlopen(urllib.request.Request(url(pid,variant,cam,size),headers={"User-Agent":"Mozilla/5.0"}),timeout=60).read()
            im=Image.open(io.BytesIO(b)).convert("RGBA"); a=im.getchannel("A")
            small=a.resize((96,96)); tr=sum(1 for v in small.getdata() if v<10)/9216
            bb=a.point(lambda v:255 if v>6 else 0).getbbox()
            return (im.crop(bb) if bb else im),tr
        except Exception as e:
            err=e; time.sleep(1.5*(k+1))
    raise err
def usable(product,cam):
    k=cams().get(product,{}).get(str(cam),{}).get("kind"); return k not in (None,"chart","blank")

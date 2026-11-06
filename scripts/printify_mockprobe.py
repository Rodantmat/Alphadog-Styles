import urllib.request,urllib.error,concurrent.futures as cf
base="https://images.printify.com/mockup/6aed2ee9e7be4e1ecd0985e1/18102/%d/x.jpg?camera_label=%s"
labels=["front","front-1","front-2","front-3","back","back-1","back-2","folded","hanging-1","hanging-2","size-chart","person-1","person-2","person-3","person-4","person-1-front","person-2-front","model-1","model-2","lifestyle-1","lifestyle-2","context-1","context-2","context-3","context-4","on-model-1","women-1","men-1","man-1","woman-1","close-up","detail","flat-lay","mannequin","ghost","side","right","left","front-4","front-5","back-3","hanging-3"]
def t(a):
    i,l=a
    try:
        r=urllib.request.urlopen(urllib.request.Request(base%(i,l),headers={"User-Agent":"Mozilla/5.0"}),timeout=20)
        n=len(r.read()); return (i,l,r.status,n)
    except urllib.error.HTTPError as e: return (i,l,e.code,0)
    except Exception as e: return (i,l,"ERR",0)
jobs=[(i,l) for i in range(102000,102080) for l in labels]
with cf.ThreadPoolExecutor(24) as ex:
    for r in ex.map(t,jobs):
        if r[2]==200: print("OK",r)
print("DONE",len(jobs))

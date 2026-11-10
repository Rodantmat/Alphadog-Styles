import json,sys,os,time
sys.path.insert(0,'scripts/video'); import ptrans
S=json.load(open('out/ptrans_test_in.json')); C=ptrans.cams(); out=[]
for prod,pid,col,var in S:
    for cam,m in C[prod].items():
        if m['kind'] in('chart','blank'): continue
        try:
            im,tr=ptrans.fetch(pid,var,cam,size=1024,tries=2)
            out.append((prod,col,cam,m['kind'],round(tr,2),im.size)); print(prod,col,cam,m['kind'],round(tr,2),im.size,flush=True)
        except Exception as e: print(prod,col,cam,'FAIL',e,flush=True)
        time.sleep(.2)

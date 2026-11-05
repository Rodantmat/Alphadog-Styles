import re,sys,json,os,urllib.request,subprocess
UA={'User-Agent':'Mozilla/5.0'}
def get(u,b=False):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read();return r if b else r.decode('utf8','ignore')
mode=sys.argv[1];os.makedirs('out/footage',exist_ok=True)
if mode=='list':
    out={}
    for cat in ['dog','pug','french-bulldog','husky','puppy','corgi','golden-retriever','labrador','dachshund','poodle','chihuahua','beagle','bulldog']:
        for pg in range(1,25):
            try: h=get(f'https://mixkit.co/free-stock-video/{cat}/?page={pg}')
            except Exception as e: break
            f=re.findall(r'href="/free-stock-video/([a-z0-9\-]+?)-(\d+)/"',h)
            if not f: break
            for s,i in f: out[i]=s.replace('-',' ')
    json.dump(out,open('out/footage/manifest.json','w'),indent=0);print(len(out),'clips')
else:
    ids=sys.argv[2].split(',')
    for i in ids:
        for q in ('720','1080','360'):
            try:
                b=get(f'https://assets.mixkit.co/videos/{i}/{i}-{q}.mp4',True);open(f'/tmp/{i}.mp4','wb').write(b);subprocess.run(['ffmpeg','-y','-v','error','-i',f'/tmp/{i}.mp4','-t','9','-vf','scale=-2:720','-an','-c:v','libx264','-crf','23',f'out/footage/{i}.mp4']);print(i,q,len(b),os.path.getsize(f'out/footage/{i}.mp4'));break
            except Exception as e: print(i,q,'ERR',repr(e)[:120])
        else: print(i,'FAILED')

import urllib.request,sys,os,subprocess
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Referer':'https://www.pexels.com/'}
os.makedirs('out/footage2',exist_ok=True)
for it in sys.argv[1].split(','):
    i=it.split(':')[0]
    urls=[f'https://www.pexels.com/download/video/{i}/?fps=30.0&h=720&w=1280',f'https://www.pexels.com/download/video/{i}/',f'https://videos.pexels.com/video-files/{i}/{it.split(":")[1]}' if ':' in it else None]
    ok=False
    for u in [x for x in urls if x]:
        try:
            r=urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=90);b=r.read()
            if len(b)<20000: print(i,'small',u,len(b));continue
            open(f'/tmp/{i}.mp4','wb').write(b)
            subprocess.run(['ffmpeg','-y','-v','error','-i',f'/tmp/{i}.mp4','-t','12','-vf','scale=-2:720','-an','-c:v','libx264','-crf','24',f'out/footage2/{i}.mp4']);print(i,'OK',u,len(b));ok=True;break
        except Exception as e: print(i,'ERR',u,repr(e)[:80])

import urllib.request,os,sys
H={'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 Chrome/124 Safari/537.36'}
os.makedirs('out/pexels',exist_ok=True)
for i in sys.argv[1].split(','):
    for u in (f'https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?auto=compress&cs=tinysrgb&w=1600',f'https://images.pexels.com/photos/{i}/pexels-photo-{i}.jpeg?auto=compress&cs=tinysrgb&w=1200'):
        try: b=urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=60).read();open(f'out/pexels/{i}.jpg','wb').write(b);print(i,len(b));break
        except Exception as e: print(i,'ERR',repr(e)[:80])

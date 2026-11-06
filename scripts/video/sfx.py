import re,os,json,urllib.request
UA={'User-Agent':'Mozilla/5.0'}
def get(u,b=False):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=60).read();return r if b else r.decode('utf8','ignore')
os.makedirs('out/sfx',exist_ok=True);meta={}
for pg in (1,2):
    h=get('https://mixkit.co/free-sound-effects/laugh/'+('' if pg==1 else '?page=2'))
    urls=re.findall(r'https://assets\.mixkit\.co/active_storage/sfx/(\d+)/\1-preview\.mp3',h)
    titles=re.findall(r'item-grid-card__title[^>]*>\s*([^<]+?)\s*<',h) or re.findall(r'<h2[^>]*>\s*([^<]+?)\s*<',h)
    for i,u in enumerate(dict.fromkeys(urls)):
        t=titles[i] if i<len(titles) else ''
        meta[u]=t
for u,t in meta.items():
    try: open(f'out/sfx/{u}.mp3','wb').write(get(f'https://assets.mixkit.co/active_storage/sfx/{u}/{u}-preview.mp3',True))
    except Exception as e: print(u,'ERR',e)
json.dump(meta,open('out/sfx/list.json','w'),indent=0);print(len(meta),meta)

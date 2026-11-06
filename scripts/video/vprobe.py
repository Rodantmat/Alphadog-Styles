import urllib.request,re,json,sys,os
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Accept':'text/html,application/json','Accept-Language':'en-US,en;q=0.9'}
os.makedirs('out/vprobe',exist_ok=True);res={}
def g(u):
    r=urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40);return r.read().decode('utf8','ignore')
qs=['smiling dog','laughing dog','dog smile','happy dog teeth','funny dog smile']
for q in qs:
    qq=q.replace(' ','%20')
    for name,u,pat in [('pexels',f'https://www.pexels.com/search/videos/{qq}/',r'/video/[a-z0-9\-]*?(\d{5,9})/'),
        ('pixabay',f'https://pixabay.com/videos/search/{qq}/',r'/videos/[a-z0-9\-]*?(\d{4,7})/'),
        ('vecteezy',f'https://www.vecteezy.com/free-videos/{q.replace(" ","-")}',r'/video/(\d+)-[a-z0-9\-]+'),
        ('coverr',f'https://coverr.co/s?q={qq}',r'/videos/([a-z0-9\-]+)')]:
        try:
            b=g(u);ids=list(dict.fromkeys(re.findall(pat,b)));res[f'{name}:{q}']=ids[:40];print('OK',name,q,len(b),len(ids),ids[:12])
        except Exception as e: print('FAIL',name,q,repr(e)[:90])
json.dump(res,open('out/vprobe/res.json','w'))

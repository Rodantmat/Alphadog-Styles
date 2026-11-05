import urllib.request,re,json
H={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36','Accept':'text/html,application/json','Accept-Language':'en-US,en;q=0.9'}
for u in ['https://pixabay.com/images/search/dog%20sunglasses/','https://www.pexels.com/search/dog%20sunglasses/','https://unsplash.com/s/photos/dog-sunglasses','https://www.pexels.com/api/v3/search/photos?query=dog%20sunglasses&per_page=10','https://pixabay.com/api/?key=x&q=dog']:
    try:
        r=urllib.request.urlopen(urllib.request.Request(u,headers=H),timeout=40);b=r.read().decode('utf8','ignore')
        print('OK',u,r.status,len(b),len(re.findall(r'images\.pexels\.com/photos/\d+|cdn\.pixabay\.com/photo/[^"\' ]+|images\.unsplash\.com/photo-[\w-]+',b)))
    except Exception as e: print('FAIL',u,repr(e)[:100])

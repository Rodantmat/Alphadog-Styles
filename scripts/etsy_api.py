"""Small Etsy Open API v3 client. Tokens live in the store DB (kv 'etsy_token', set by /api/market/etsy/connect)
and are refreshed here (Etsy rotates refresh tokens, so the new one is saved back every time).
Env: ETSY_KEYSTRING, ETSY_SHARED_SECRET, STORE_ADMIN_TOKEN."""
import os,json,time,urllib.request,urllib.error,urllib.parse,uuid
KEY=os.environ.get("ETSY_KEYSTRING","").strip(); SEC=os.environ.get("ETSY_SHARED_SECRET","").strip()
ADM=os.environ["STORE_ADMIN_TOKEN"].strip(); STORE="https://alphadogstyles.com"; API="https://api.etsy.com/v3/application"
def store(m,p,b=None):
    r=urllib.request.Request(STORE+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"x-admin-token":ADM,"content-type":"application/json","User-Agent":"alphadog"})
    return json.load(urllib.request.urlopen(r,timeout=60))
_tok=None; _xkey=[f"{KEY}:{SEC}" if SEC else KEY, KEY]
def token():
    global _tok
    if _tok and _tok["exp"]>time.time()+120: return _tok["access_token"]
    t=store("GET","/api/internal/kv/etsy_token")["v"]
    if not t: raise SystemExit("Etsy not connected yet: open https://alphadogstyles.com/api/market/etsy/connect?t=<admin token>")
    if t.get("exp",0)>time.time()+120: _tok=t; return t["access_token"]
    body=urllib.parse.urlencode({"grant_type":"refresh_token","client_id":KEY,"refresh_token":t["refresh_token"]}).encode()
    r=json.load(urllib.request.urlopen(urllib.request.Request("https://api.etsy.com/v3/public/oauth/token",data=body,method="POST",headers={"content-type":"application/x-www-form-urlencoded","User-Agent":"alphadog"}),timeout=60))
    t={**t,**r,"exp":time.time()+int(r.get("expires_in",3600))}; store("POST","/api/internal/kv/etsy_token",{"v":t}); _tok=t
    return t["access_token"]
def call(m,p,body=None,form=None,files=None,q=None,raw=False):
    url=API+p+("?"+urllib.parse.urlencode(q,doseq=True) if q else "")
    for a in range(6):
        h={"x-api-key":_xkey[0],"Authorization":"Bearer "+token(),"User-Agent":"alphadog"}; data=None
        if files:
            bd=uuid.uuid4().hex; parts=[]
            for k,v in (form or {}).items(): parts.append(f'--{bd}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode())
            for k,(fn,content,ct) in files.items(): parts.append(f'--{bd}\r\nContent-Disposition: form-data; name="{k}"; filename="{fn}"\r\nContent-Type: {ct}\r\n\r\n'.encode()+content+b"\r\n")
            data=b"".join(parts)+f"--{bd}--\r\n".encode(); h["content-type"]="multipart/form-data; boundary="+bd
        elif form is not None: data=urllib.parse.urlencode(form,doseq=True).encode(); h["content-type"]="application/x-www-form-urlencoded"
        elif body is not None: data=json.dumps(body).encode(); h["content-type"]="application/json"
        try:
            x=urllib.request.urlopen(urllib.request.Request(url,data=data,method=m,headers=h),timeout=120).read()
            return x if raw else (json.loads(x) if x else {})
        except urllib.error.HTTPError as e:
            msg=e.read().decode()[:600]
            if e.code in(401,403) and "api key" in msg.lower() and len(_xkey)>1: _xkey.pop(0); continue
            if e.code==429 or e.code>=500: time.sleep(5*(a+1)); continue
            return {"_err":e.code,"msg":msg}
    return {"_err":"retries"}
_me=None
def shop_id():
    global _me
    if not _me: _me=call("GET","/users/me")
    return _me["shop_id"]
def listings(state="active"):
    out=[]; off=0
    while True:
        r=call("GET",f"/shops/{shop_id()}/listings",q={"state":state,"limit":100,"offset":off})
        out+=r.get("results",[]); off+=100
        if off>=r.get("count",0): return out

"""Create (once) a Cloudflare Hyperdrive config for the DigitalOcean Postgres (private CA, so Workers' direct TLS fails).
Env: DATABASE_URL (store db), CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID. Prints HYPERDRIVE_ID=<id> or HYPERDRIVE_FAILED=<why>."""
import os,re,ssl,socket,json,urllib.request,urllib.error,urllib.parse,subprocess,sys
U=urllib.parse.urlsplit(os.environ["DATABASE_URL"].strip()); TOK=os.environ["CLOUDFLARE_API_TOKEN"].strip(); ACC=os.environ["CLOUDFLARE_ACCOUNT_ID"].strip()
NAME="alphadog-store-db"
def cf(m,p,b=None):
    r=urllib.request.Request(f"https://api.cloudflare.com/client/v4/accounts/{ACC}{p}",data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+TOK,"Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(r,timeout=60))
    except urllib.error.HTTPError as e: return {"success":False,"errors":[{"message":f"HTTP {e.code} {e.read().decode()[:300]}"}]}
try:
    l=cf("GET","/hyperdrive/configs")
    if not l.get("success"): print("HYPERDRIVE_FAILED=list: "+json.dumps(l.get("errors"))); sys.exit(0)
    ex=[c for c in l["result"] if c["name"]==NAME]
    if ex: print("HYPERDRIVE_ID="+ex[0]["id"]); sys.exit(0)
    out=subprocess.run(["openssl","s_client","-starttls","postgres","-connect",f"{U.hostname}:{U.port}","-showcerts"],input=b"",capture_output=True,timeout=60).stdout.decode()
    pems=re.findall(r"-----BEGIN CERTIFICATE-----.*?-----END CERTIFICATE-----",out,re.S)
    if len(pems)<2: print("HYPERDRIVE_FAILED=no CA in TLS chain"); sys.exit(0)
    ca=pems[-1]+"\n"
    c=cf("POST","/mtls_certificates",{"ca":True,"certificates":ca,"name":"do-project-ca"})
    if not c.get("success"):
        # maybe already uploaded
        ls=cf("GET","/mtls_certificates"); m=[x for x in (ls.get("result") or []) if x.get("name")=="do-project-ca"]
        if not m: print("HYPERDRIVE_FAILED=cert upload: "+json.dumps(c.get("errors"))); sys.exit(0)
        cid=m[0]["id"]
    else: cid=c["result"]["id"]
    h=cf("POST","/hyperdrive/configs",{"name":NAME,"origin":{"scheme":"postgres","host":U.hostname,"port":U.port,"database":U.path.lstrip("/"),"user":urllib.parse.unquote(U.username),"password":urllib.parse.unquote(U.password)},"caching":{"disabled":True},"mtls":{"ca_certificate_id":cid,"sslmode":"verify-ca"}})
    if not h.get("success"): print("HYPERDRIVE_FAILED=create: "+json.dumps(h.get("errors"))); sys.exit(0)
    print("HYPERDRIVE_ID="+h["result"]["id"])
except Exception as e: print("HYPERDRIVE_FAILED="+str(e)[:300])

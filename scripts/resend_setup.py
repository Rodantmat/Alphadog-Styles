"""Idempotent: register the sending domain at Resend, publish its DNS records in Cloudflare, ask Resend to verify.
Env: RESEND_API_KEY, CLOUDFLARE_API_TOKEN. Prints RESEND_STATUS=<...>."""
import os,json,urllib.request,urllib.error
DOM="alphadogstyles.com"; RK=os.environ.get("RESEND_API_KEY","").strip(); CT=os.environ.get("CLOUDFLARE_API_TOKEN","").strip()
def http(url,tok,m="GET",b=None):
    r=urllib.request.Request(url,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+tok,"Content-Type":"application/json","User-Agent":"alphadog-setup/1.0"})
    try: return json.load(urllib.request.urlopen(r,timeout=60))
    except urllib.error.HTTPError as e:
        try: return {"_err":e.code,"body":json.loads(e.read().decode())}
        except Exception: return {"_err":e.code}
if not RK: print("RESEND_STATUS=no RESEND_API_KEY"); raise SystemExit
rs=lambda p,m="GET",b=None: http("https://api.resend.com"+p,RK,m,b)
cf=lambda p,m="GET",b=None: http("https://api.cloudflare.com/client/v4"+p,CT,m,b)
l=rs("/domains")
if l.get("_err"): print("RESEND_STATUS=list failed",l); raise SystemExit
d=next((x for x in l.get("data",[]) if x["name"]==DOM),None)
if not d:
    d=rs("/domains","POST",{"name":DOM})
    if d.get("_err") or not d.get("id"): print("RESEND_STATUS=create failed",json.dumps(d)[:300]); raise SystemExit
info=rs("/domains/"+d["id"]); recs=info.get("records",[])
z=cf("/zones?name="+DOM); zid=(z.get("result") or [{}])[0].get("id")
if not zid: print("RESEND_STATUS=zone lookup failed",json.dumps(z)[:200]); raise SystemExit
made=0
for r in recs:
    name=r["name"]; full=DOM if name in("@","") else f"{name}.{DOM}" if not name.endswith(DOM) else name
    typ=r["type"]; val=r["value"]
    ex=cf(f"/zones/{zid}/dns_records?type={typ}&name={full}").get("result") or []
    if typ=="TXT" and any(val.strip('"') in (e["content"] or "").strip('"') for e in ex): continue
    if typ!="TXT" and any(e["content"].rstrip(".")==val.rstrip(".") for e in ex): continue
    body={"type":typ,"name":full,"content":val,"ttl":1,"proxied":False}
    if typ=="MX": body["priority"]=int(r.get("priority") or 10)
    c=cf(f"/zones/{zid}/dns_records","POST",body)
    if c.get("success"): made+=1
    else: print("DNS add failed",typ,full,json.dumps(c)[:200])
v=rs("/domains/"+d["id"]+"/verify","POST")
info=rs("/domains/"+d["id"])
print("RESEND_STATUS=domain",info.get("status"),"records_added",made,"statuses",[(r["record"],r.get("status")) for r in info.get("records",[])])

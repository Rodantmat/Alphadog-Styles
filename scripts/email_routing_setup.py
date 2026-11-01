"""Idempotent: Cloudflare Email Routing for alphadogstyles.com -> support@ and customization@ go to the alphadog-store Worker
(which files them in the support inbox and forwards a copy to the owner once the owner verifies the destination address).
Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID, OWNER_EMAIL. Prints EMAIL_ROUTING=..."""
import os,json,urllib.request,urllib.error
DOM="alphadogstyles.com"; T=os.environ["CLOUDFLARE_API_TOKEN"].strip(); ACC=os.environ["CLOUDFLARE_ACCOUNT_ID"].strip(); OWNER=os.environ.get("OWNER_EMAIL","rodolfoaamattos@gmail.com")
def cf(m,p,b=None):
    r=urllib.request.Request("https://api.cloudflare.com/client/v4"+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+T,"Content-Type":"application/json"})
    try: return json.load(urllib.request.urlopen(r,timeout=60))
    except urllib.error.HTTPError as e:
        try: return {"success":False,"code":e.code,"errors":json.loads(e.read().decode()).get("errors")}
        except Exception: return {"success":False,"code":e.code}
z=cf("GET","/zones?name="+DOM); zid=(z.get("result") or [{}])[0].get("id")
if not zid: print("EMAIL_ROUTING=zone lookup failed"); raise SystemExit
s=cf("GET",f"/zones/{zid}/email/routing")
if not s.get("success"): print("EMAIL_ROUTING=no permission (add Zone > Email Routing Rules > Edit and Account > Email Routing Addresses > Edit to the API token)",s.get("errors")); raise SystemExit
if not s["result"].get("enabled"):
    e=cf("POST",f"/zones/{zid}/email/routing/enable",{}); print("enable:",e.get("success"),e.get("errors"))
a=cf("GET",f"/accounts/{ACC}/email/routing/addresses")
if a.get("success") and not any(x["email"].lower()==OWNER.lower() for x in a["result"]):
    c=cf("POST",f"/accounts/{ACC}/email/routing/addresses",{"email":OWNER}); print("destination added (owner must click the verification email):",c.get("success"),c.get("errors"))
rules=cf("GET",f"/zones/{zid}/email/routing/rules").get("result") or []
for box in ("support","customization"):
    addr=f"{box}@{DOM}"
    if any(any(mt.get("value")==addr for mt in r.get("matchers",[])) for r in rules): continue
    c=cf("POST",f"/zones/{zid}/email/routing/rules",{"name":f"{box} to store worker","enabled":True,"matchers":[{"type":"literal","field":"to","value":addr}],"actions":[{"type":"worker","value":["alphadog-store"]}]})
    print("rule",addr,c.get("success"),c.get("errors"))
v=[x for x in (cf("GET",f"/accounts/{ACC}/email/routing/addresses").get("result") or []) if x["email"].lower()==OWNER.lower()]
print("EMAIL_ROUTING=ok","owner_verified" if v and v[0].get("verified") else "owner_not_verified_yet")

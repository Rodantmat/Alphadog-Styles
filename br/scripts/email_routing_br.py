"""Idempotent: Cloudflare Email Routing rules suporte@ / customiza@ / pedidos@ -> the alphadog-store Worker (files them in support_inbox as br_suporte / br_custom / br_pedidos).
Same pattern as scripts/email_routing_setup.py. Env: CLOUDFLARE_API_TOKEN, CLOUDFLARE_ACCOUNT_ID. Domain: BR_MAILBOX_DOMAIN (default alphadogstyles.com).
NOTE: if the three addresses are instead hosted on the own mail server (mail-server.yml mode=add), do NOT also route them here - pick ONE (see br/plan.md section 7)."""
import os, json, urllib.request, urllib.error
DOM = os.environ.get("BR_MAILBOX_DOMAIN", "alphadogstyles.com"); T = os.environ["CLOUDFLARE_API_TOKEN"].strip()
def cf(m, p, b=None):
    r = urllib.request.Request("https://api.cloudflare.com/client/v4" + p, data=json.dumps(b).encode() if b is not None else None, method=m, headers={"Authorization": "Bearer " + T, "Content-Type": "application/json"})
    try: return json.load(urllib.request.urlopen(r, timeout=60))
    except urllib.error.HTTPError as e:
        try: return {"success": False, "code": e.code, "errors": json.loads(e.read().decode()).get("errors")}
        except Exception: return {"success": False, "code": e.code}
if os.environ.get("BR_EMAIL_ROUTING", "worker") != "worker": print("BR_EMAIL_ROUTING=skipped (addresses hosted elsewhere)"); raise SystemExit
z = cf("GET", "/zones?name=" + DOM); zid = (z.get("result") or [{}])[0].get("id")
if not zid: print("BR_EMAIL_ROUTING=zone lookup failed"); raise SystemExit
rules = (cf("GET", f"/zones/{zid}/email/routing/rules").get("result") or [])
for pri, box in ((30, "suporte"), (40, "customiza"), (50, "pedidos")):
    addr = f"{box}@{DOM}"
    if any(any(mt.get("value") == addr for mt in r.get("matchers", [])) for r in rules): print("exists", addr); continue
    c = cf("POST", f"/zones/{zid}/email/routing/rules", {"name": f"{box} (BR) to store worker", "enabled": True, "priority": pri, "matchers": [{"type": "literal", "field": "to", "value": addr}], "actions": [{"type": "worker", "value": ["alphadog-store"]}]})
    print("rule", addr, c.get("success"), c.get("errors"))
print("BR_EMAIL_ROUTING=ok")

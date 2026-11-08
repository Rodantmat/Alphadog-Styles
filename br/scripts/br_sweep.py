"""Retry sweep for the Brazilian arm (run by .github/workflows/store-fulfill-br.yml every 10 min):
 - br_paid / br_wallet_low orders -> create + pay the Gubo order (idempotent, key br-create-<id>)
 - awaiting_payment orders -> reconcile with Mercado Pago (lost webhooks)
 - Gubo orders updated since the last poll -> sync status/tracking (lost webhooks)
Env: STORE_ADMIN_TOKEN, STORE_URL. Never prints secrets."""
import os, json, urllib.request
U = os.environ.get("STORE_URL", "https://alphadogstyles.com"); H = {"x-admin-token": os.environ["STORE_ADMIN_TOKEN"], "content-type": "application/json", "User-Agent": "br-sweep"}
r = urllib.request.Request(U + "/api/internal/br/sweep", data=b"{}", method="POST", headers=H)
out = json.load(urllib.request.urlopen(r, timeout=120)); print(json.dumps(out)[:4000])
if out.get("errors"): raise SystemExit(1)

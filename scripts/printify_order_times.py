"""READ-ONLY: list Printify orders, print production/shipping timing per product type. Prints to job log only."""
import os, json, urllib.request, datetime as dt
T = os.environ["PRINTIFY_TOKEN"].strip(); H = {"Authorization": "Bearer " + T, "User-Agent": "a"}
def g(p):
    return json.loads(urllib.request.urlopen(urllib.request.Request("https://api.printify.com" + p, headers=H), timeout=60).read())
P = lambda s: dt.datetime.fromisoformat(s.replace("Z", "+00:00")) if s else None
for sh in g("/v1/shops.json"):
    sid = sh["id"]; print("SHOP", sid, sh.get("title"), sh.get("sales_channel"))
    page, rows = 1, []
    while True:
        d = g(f"/v1/shops/{sid}/orders.json?limit=50&page={page}")
        rows += d.get("data", [])
        if page >= d.get("last_page", 1): break
        page += 1
    print(" orders:", len(rows))
    for o in rows:
        its = o.get("line_items", [])
        kinds = "; ".join(f"{i.get('metadata',{}).get('title','?')[:40]}" for i in its)
        cr = P(o.get("created_at")); sent = P(o.get("sent_to_production_at")); ful = None
        shp = o.get("shipments") or []
        ship = P(shp[0].get("shipped_at")) if shp and shp[0].get("shipped_at") else None
        dlv = P(shp[0].get("delivered_at")) if shp and shp[0].get("delivered_at") else None
        days = lambda a, b: round((b - a).total_seconds() / 86400, 1) if a and b else None
        print(f" {o.get('id')} {o.get('status'):16} {kinds[:60]:60} created->prod {days(cr,sent)}d  created->shipped {days(cr,ship)}d  created->delivered {days(cr,dlv)}d")

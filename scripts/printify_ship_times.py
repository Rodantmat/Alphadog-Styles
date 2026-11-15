"""READ-ONLY: Printify catalog shipping/handling info for the blueprints we sell. Prints to job log."""
import os, json, urllib.request
T = os.environ["PRINTIFY_TOKEN"].strip(); H = {"Authorization": "Bearer " + T, "User-Agent": "a"}
def g(p):
    try: return json.loads(urllib.request.urlopen(urllib.request.Request("https://api.printify.com" + p, headers=H), timeout=60).read())
    except Exception as e: return {"error": str(e)[:120]}
print("PROVIDER 99:", json.dumps(g("/v1/catalog/print_providers/99.json"))[:900])
for bp in (12, 77, 18, 39, 1402, 1447, 1735, 1734):
    b = g(f"/v1/catalog/blueprints/{bp}.json"); print("\nBP", bp, b.get("title"))
    for pr in g(f"/v1/catalog/blueprints/{bp}/print_providers.json") if isinstance(g(f"/v1/catalog/blueprints/{bp}/print_providers.json"), list) else []:
        print("  provider", pr.get("id"), pr.get("title"))
    s = g(f"/v1/catalog/blueprints/{bp}/print_providers/99/shipping.json")
    print("  handling_time:", s.get("handling_time"))
    for p in s.get("profiles", [])[:3]:
        print("  profile:", p.get("countries"), "first", p.get("first_item"), "add", p.get("additional_items"))
    print("  raw keys:", list(s)[:8], str(s)[:300] if "error" in s else "")

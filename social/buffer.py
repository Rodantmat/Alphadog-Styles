#!/usr/bin/env python3
"""Buffer GraphQL helper. env KEY. usage: buffer.py channels | types NAME... | posts | plan PLAN.json [--dry]"""
import json, os, sys, urllib.request, urllib.error
KEY = os.environ["KEY"].strip()
def gql(q, v=None):
    r = urllib.request.Request("https://api.buffer.com", data=json.dumps({"query": q, "variables": v or {}}).encode(),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {KEY}"}, method="POST")
    try:
        with urllib.request.urlopen(r, timeout=120) as x: o = json.loads(x.read())
    except urllib.error.HTTPError as e: raise SystemExit(f"HTTP {e.code}: {e.read().decode()[:800]}")
    if o.get("errors"): print("GRAPHQL_ERRORS", json.dumps(o["errors"])[:1500])
    return o.get("data") or {}
def org(): return gql("query{account{organizations{id}}}")["account"]["organizations"][0]["id"]
def channels(): return gql('query($o:OrganizationId!){channels(input:{organizationId:$o}){id name service}}', {"o": org()}).get("channels") or []
c = sys.argv[1]
if c == "channels": print(json.dumps(channels()))
elif c == "types":
    for n in sys.argv[2:]:
        print("TYPE", n, json.dumps(gql('query($n:String!){__type(name:$n){kind enumValues{name} inputFields{name type{name kind ofType{name kind ofType{name kind}}}}}}', {"n": n})))
elif c == "posts":
    q = 'query($o:OrganizationId!){posts(input:{organizationId:$o},first:100){edges{node{id status dueAt channelService text}}}}'
    for e in (gql(q, {"o": org()}).get("posts") or {}).get("edges") or []:
        n = e["node"]; print("POST", n["id"], n["status"], n["dueAt"], n["channelService"], repr((n["text"] or "")[:50]))
elif c == "delete":
    ids=sys.argv[2:]
    if ids==["ALL"]:
        q = 'query($o:OrganizationId!){posts(input:{organizationId:$o},first:100){edges{node{id status}}}}'
        ids=[e["node"]["id"] for e in (gql(q, {"o": org()}).get("posts") or {}).get("edges") or [] if e["node"]["status"] in ("scheduled","draft")]
    for i in ids: print("DELETE", i, json.dumps(gql("mutation($i:DeletePostInput!){deletePost(input:$i){__typename ... on MutationError{message}}}", {"i": {"id": i}})))
elif c == "plan":
    plan = json.load(open(sys.argv[2])); dry = "--dry" in sys.argv
    ch = {x["service"].lower(): x["id"] for x in channels()}
    for p in plan:
        svc = p["service"]
        if svc not in ch: print("SKIP no channel", svc); continue
        inp = {"text": p["text"], "channelId": ch[svc], "schedulingType": "automatic", "mode": "customScheduled", "dueAt": p["due"],
               "assets": ([{"video": {"url": p["url"], "metadata": {"thumbnailOffset": 1200}}}] if p["url"].endswith(".mp4") else [{"image": {"url": u}} for u in p["url"].split("|")])}
        if p.get("metadata"): inp["metadata"] = p["metadata"]
        if dry: print("DRY", json.dumps(inp)[:300]); continue
        d = gql("mutation($input:CreatePostInput!){createPost(input:$input){... on PostActionSuccess{post{id dueAt status}} ... on MutationError{message}}}", {"input": inp})
        print("RESULT", svc, p["due"], json.dumps(d))

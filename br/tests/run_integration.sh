#!/usr/bin/env bash
# Applies br/ + patch onto a scratch copy of the real worker files and exercises the PATCHED store/worker/index.js (region routing, /api/br, inbound mailbox mapping).
# Needs store/worker/node_modules (pg, postal-mime) and Node >= 22. Does not touch the repo tree.
set -euo pipefail
R="$(cd "$(dirname "$0")/../.." && pwd)"; S="$(mktemp -d)"
mkdir -p "$S/store/worker" "$S/store/data" "$S/store/js" "$S/scripts" "$S/.github/workflows"
cp "$R/store/worker/"{index.js,wrangler.toml,db.js} "$S/store/worker/"; cp "$R/store/index.html" "$S/store/"; cp "$R/store/data/"{catalog,market_plan}.json "$S/store/data/"; cp "$R/store/js/placement.js" "$S/store/js/"
cp "$R/scripts/mail_bridge.py" "$S/scripts/"; cp "$R/.github/workflows/store-deploy.yml" "$S/.github/workflows/"; cp -r "$R/br" "$S/br"
ln -s "$R/store/worker/node_modules" "$S/store/worker/node_modules"; echo '{"type":"module"}' > "$S/store/worker/package.json"
(cd "$S" && git init -q . && BR_ROOT="$S" bash br/apply.sh >/dev/null)
python3 - "$S" <<'P'
import re,sys
for f in ["store/worker/index.js","store/worker/br/br.js"]:
    p=sys.argv[1]+"/"+f; s=open(p).read(); open(p,"w").write(re.sub(r'^(import [A-Za-z]+ from "[^"]+\.json");',r'\1 with {type:"json"};',s,flags=re.M))
P
cp "$R/br/tests/integration_patched_worker.mjs" "$S/t.mjs"; (cd "$S" && node t.mjs 2>&1 | grep -v -i "warning\|reparsing\|eliminate\|trace-warn")

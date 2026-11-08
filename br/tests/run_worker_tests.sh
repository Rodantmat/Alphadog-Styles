#!/usr/bin/env bash
# Runs worker.test.mjs against br/worker/br.js with Node >=22 (JSON imports need an attribute outside wrangler/esbuild, so we stage a patched copy).
set -euo pipefail
R="$(cd "$(dirname "$0")/.." && pwd)"; T="$(mktemp -d)"
mkdir -p "$T/worker/br" "$T/br/data" "$T/br/config"
cp "$R/site/data/catalog_br.json" "$T/br/data/"; cp "$R/config/br_config.json" "$T/br/config/"
sed -E 's#^(import [A-Z]+ from "[^"]+\.json");#\1 with { type: "json" };#' "$R/worker/br.js" > "$T/worker/br/br.js"
cp "$R/tests/worker.test.mjs" "$T/worker.test.mjs"
(cd "$T" && node worker.test.mjs)

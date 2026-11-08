#!/usr/bin/env bash
# Installs the Brazilian arm into the live store tree. Run from the repo root ON A BRANCH/PR, never by hand on main without review.
# WARNING: store-deploy.yml deploys on every push that touches store/** (any branch) - after this script, pushing deploys to PRODUCTION.
# Steps are idempotent; the patch is applied only once.   usage: br/apply.sh [--no-workflows]
set -euo pipefail
ROOT="${BR_ROOT:-$(git rev-parse --show-toplevel)}"; cd "$ROOT"
[ -f store/worker/br/br.js ] && echo "already installed (store/worker/br/br.js exists) - refreshing files only" || git apply br/patches/br-integration.patch
mkdir -p store/worker/br store/br/js store/br/css store/br/data store/br/config
cp br/worker/br.js store/worker/br/br.js
cp br/site/index.html store/br/index.html
cp br/site/js/*.js store/br/js/; cp br/site/css/*.css store/br/css/; cp br/site/data/catalog_br.json store/br/data/
cp br/config/br_config.json store/br/config/
if [ "${1:-}" != "--no-workflows" ]; then cp br/workflows/*.yml .github/workflows/; fi
echo "installed. Next: br/tests/run_worker_tests.sh, then open a PR; merging deploys."

# br/ - AlphaDog Styles Brasil (pt-BR)
Staged OUTSIDE `store/` on purpose: `store-deploy.yml` deploys production on pushes touching `store/**`. Nothing here is live until `br/apply.sh` is run and the result is merged.
Read `br/docs/plan.md` (architecture + owner checklist) and `br/docs/status.md` (what is done / not done) first.

| Path | What |
|---|---|
| `worker/br.js` | Worker module: region routing, `/api/br/*`, Gubo + Mercado Pago, mailbox mapping |
| `site/` | pt-BR storefront (installed to `store/br/`) |
| `config/br_config.json` | prices, shipping policy, mailboxes, payment slots, every TODO-verify |
| `scripts/` | catalog builder, Gubo read-only pull, retry sweep, email routing |
| `workflows/` | `store-fulfill-br.yml`, `br-catalog-sync.yml` (inert until repo variable `BR_ENABLED=1`) |
| `patches/br-integration.patch` | the only edits to existing files (worker index, wrangler routes, US index hreflang, mail_bridge, store-deploy secrets + branch filter) |
| `automation/support_assistant_br.md` | prompt for the pt-BR support scheduled task |
| `tests/` | `run_worker_tests.sh`, `run_integration.sh`, `test_catalog.py`, `smoke_site.mjs` |

Secrets used (none exist yet except the Gubo test key): `GUBO_API_KEY`, `GUBO_WEBHOOK_SECRET`, `MP_ACCESS_TOKEN`, `MP_WEBHOOK_SECRET`. Worker vars optional: `BR_DEV_MODE`, `FORWARD_BR_SUPORTE|CUSTOM|PEDIDOS`, `BR_MAILBOX_DOMAIN`.

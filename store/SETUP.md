# AlphaDog store - setup (everything else is already built)

Repo secrets/variables to add (Settings > Secrets and variables > Actions). Nothing is needed to just preview the site.

1. Go live: CLOUDFLARE_API_TOKEN (Workers + D1 edit), CLOUDFLARE_ACCOUNT_ID, STORE_ADMIN_TOKEN (any long random string). Then run workflow "store-deploy".
2. Email codes/receipts: RESEND_API_KEY and variable MAIL_FROM (needs a sending domain), or use Google sign-in only.
3. Sign in with Google / Facebook / Apple (optional, each independent): GOOGLE_CLIENT_ID/SECRET, FACEBOOK_APP_ID/SECRET, APPLE_CLIENT_ID/TEAM_ID/KEY_ID/PRIVATE_KEY. Redirect URL for each: https://<store-url>/api/auth/oauth/<google|facebook|apple>/callback
4. Fulfilment: variable STORE_URL, secret PRINTIFY_API_SHOP_ID (a Printify shop of type API). Paid orders then print and ship automatically.
5. Payments (last): Stripe webhook sets order status "paid" via POST /api/internal/orders/<id> {"status":"paid"}.

# Passive Income Ventures — Research & Decisions Log

Owner: Rodo · Started: 2026-10-28 · Status: research done, plan drafted, build not started

## Owner requirements (as stated)
- Fully automated after setup; occasional human touch is OK (target ≤10–15 min/week).
- Minimal start cost; free tools, self-built pipelines (GitHub Actions / Cloudflare Workers). Stay inside the current Cloudflare $5 and GitHub $4 plans; no surprise overages.
- Goal: any amount helps ($200/mo is a win); grow over time.
- **Hard rule: zero risk to the existing Amazon seller account** (5 yrs, ~$250k/yr). If separation can't be guaranteed, don't do it on Amazon.
- Idea 1 (print-on-demand) starts first. AI-generated art, any product type the market rewards.
- Design QA = automated "analyzer": trademark check, look-alike/similarity search, multi-persona AI critics.
- Social: already posting to IG/FB/TikTok/YouTube via APIs for other projects; only reach matters, no comment handling needed. TikTok via Buffer.

## Key findings (round 3, 2026-10-28)

### Amazon risk — why Amazon POD is out (for now)
- Amazon can deactivate *related* accounts when one linked account is deactivated; links come from shared bank, address, tax ID, devices. A second seller account under the same owner is linked by definition.
- Merch on Demand sits on the same Amazon identity; a forum answer states Merch requires a Professional seller account and a deactivated seller account affects Merch. Merch terminations happen with no explanation and no due process (IP strikes are the usual cause).
- Conclusion: neither Merch on Demand nor a second seller account can be made *zero-risk* to the main account. → POD moves **off Amazon**. Merch stays parked as an owner decision (see options table in plan).

### Off-Amazon POD channels
| Channel | Start cost | Ongoing | Per-sale (tee) | Automation | Notes |
|---|---|---|---|---|---|
| Etsy + Printify (free plan) | $0 (+ possible one-time Etsy setup fee) | $0.20/listing (renews every 4 mo) | ~$9–11 net at $25–27 | Full: Printify API publishes to Etsy | 6.5% transaction + ~3%+$0.25 processing; 2026 rules require AI disclosure + production-partner disclosure; suspensions for AI/reused designs rising |
| TeePublic | $0 | $0 | $4 full / $2 sale (half on Apprentice tier) | Manual upload (no API) | No seller fees; needs first 5–10 outside sales to unlock internal traffic |
| Redbubble | $0 | Account fees on Standard tier | ~$4 at 20% markup, minus fees | Manual | Fees + declining traffic → low priority |
| Amazon Merch | $0 | $0 | $2.44 tee (Creator tier) | Semi (owner clicks publish) | **Parked — linked to main Amazon identity** |
| Printify → own Amazon seller acct | $0 extra (acct is Pro) | — | ~$2.50–4.50 | Full | **Rejected — risk to main account** |

### Products the market rewards (2026)
- Hoodies: ~50% higher price for ~30% higher cost → best $ per sale (Q4 heavy).
- Mugs/tumblers: 55–70% gross margin, gift demand. Hats: good margin for short text/icons.
- Premium blanks beat budget ones (45–60% vs 20–30% margin). Avoid blankets/shower curtains early (cost + returns).
- Text/icon designs → tees/hoodies/caps; detailed art/patterns → totes, phone cases, mugs.

### Free tooling verified
- Image gen: Cloudflare Workers AI, 10,000 free Neurons/day (≈100–170 FLUX schnell images/day). On the paid Workers plan overage is billed at $0.011/1k Neurons → pipeline must hard-cap daily usage.
- Trademark: USPTO trademark search + TSDR API are free (TSDR needs a free key).
- Look-alike search: TinEye API is paid ($50/mo) → use Google Cloud Vision free monthly quota (web detection) + perceptual hashing against scraped competitor thumbnails.
- Critics: Gemini (already available via AlphaDog bridge) + Workers AI vision models, persona prompts.
- TikTok: Buffer free plan = 3 channels, 10 queued posts per channel; free plan includes 1 API key (24h API limit raised 100→250). Buffer's TikTok app is already audited → public posts.

### Affiliate (Idea 2) — unchanged constraints
- Amazon Associates April 14, 2026: content must add commentary/analysis/transformation; halo commissions removed.
- Instagram/Facebook remove repost-heavy accounts from recommendations.
- Creators API needs 10 qualifying sales in 30 days; links can be built without it until then.
- Rates: kitchen 4.5%, apparel 4%, home/beauty/toys 3% → ~$1 per $30 sale.

## Round 4 (2026-10-28 evening) — reach comparison & store paths
- Owner concern: Etsy reach is much lower than Amazon. Confirmed: Similarweb lists amazon.com ~2.33B monthly visits, ebay.com ~493M, walmart.com ~428M, etsy.com ~231M (page updated May 2026, data month not stated). Etsy ≈ 1/10 of Amazon.
- Printify sales channels: Etsy, TikTok Shop (US only), eBay, Amazon, Shopify, WooCommerce, Wix, Squarespace, Big Cartel, PrestaShop, BigCommerce, free Pop-Up Store. Walmart not listed.
- TikTok Shop US referral fee: TikTok's table (May 2026) shows mostly 6%; independent guides report 8% from Aug 4, 2026 — confirm in Seller Center. No monthly fee.
- eBay: 50–200 free listings/month (country dependent); average seller pays ~12–14% total fees.
- Owner decision: image-based designs (not text-only).
- New strategy: one design pipeline → multiple Printify stores (Etsy + eBay + TikTok Shop) to stack reach without Amazon risk.

## Decisions
- D1 (2026-10-28): Idea 1 first. POD runs on Etsy + Printify (free) as primary, TeePublic as secondary manual channel. No Amazon POD while zero-risk rule stands.
- D2: Owner keeps a weekly approve/publish click (≤10 min) for the first months; removed only after the automated analyzer proves it matches his calls (measured agreement).
- D3: All infra on GitHub Actions + Cloudflare free allocations, with hard daily caps.
- D4 (2026-10-28): Image-first designs (AI art). Text-only track dropped as a primary track.
- D5 (pending owner OK): Store path = Printify multi-channel (Etsy + eBay + TikTok Shop), Amazon excluded.

## Open questions for owner
- Q1: Confirm Merch on Demand stays parked (or accept small risk — see plan options).
- Q2: Brand/shop name and first niches (we will propose ~50 candidates and test).
- Q3: GitHub repo name + access (pending).

## Round 5 (2026-10-28) — Amazon vs off-Amazon, grounded
- Traffic: Amazon ~10x Etsy visits, but conversion is also cited higher (Amazon 10-15% vs Etsy 1-3%, vendor-sourced, Merch Titans Apr 2026).
- Etsy FY2025: ~$11.92B GMS / ~5.6M active sellers = ~$177/month GROSS per seller (mean; typical shop is below). Source: EarnFacts Jul 2026 from Etsy results.
- Etsy categories: Home & Living ~34% of GMS; apparel is one of six categories making ~87-88% (Printful, Jan 2026).
- Key constraint: Amazon Merch traffic advantage is capped early by tiers (10 -> 25 -> 100 -> 500 slots) and the $2.44 Creator-tier royalty.
- TikTok Shop: Content Posting API post_info has no product/shop fields; products are linked in Creator Center (video <=30 days old, audio only from Commercial Music Library, links can't be edited after). Native in-app scheduling of shoppable videos: 30 min-30 days ahead, max 50 queued. => Buffer can post, but product linking is a manual step (~30 s/video) unless a paid third-party tool is used.
- Projection table (estimates, not measured) lives in 02_ATTACK_PLAN.md "Channel comparison".
- D6 (2026-10-28): Phase 1 = off-Amazon only (Etsy + eBay + TikTok Shop via Printify). Amazon Merch reconsidered as Phase 2 after a few months, using only designs with proven sales and clean IP history; still subject to the zero-risk rule (owner decides then).

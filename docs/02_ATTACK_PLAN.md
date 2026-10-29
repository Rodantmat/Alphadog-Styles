# Attack Plan — Idea 1: AI Print-on-Demand (off Amazon)

## v2 update (2026-10-28) — store path
Image-first AI designs. One pipeline publishes each approved design through Printify to three stores:
| Store | Reach (monthly visits) | Fixed cost | Per-sale fees | Traffic source |
|---|---|---|---|---|
| eBay | ~493M | $0 (free listing quota) | ~12–14% | eBay search |
| Etsy | ~231M | $0.20/listing | ~10% + $0.25 | Etsy search (gift/art buyers) |
| TikTok Shop (US) | n/a (in-app) | $0 | ~6–8% referral | Our own videos + TikTok affiliate creators |
Combined reach ≈ eBay + Etsy + TikTok without touching Amazon. Text-only track below is superseded by image-first (D4).

Status: draft v1 · 2026-10-28 · Owner approval needed on the 3 open questions in 01_RESEARCH_AND_DECISIONS.md

## Architecture (all free tiers)
```
[1 Niche finder] -> [2 Design generator] -> [3 Analyzer] -> [4 Weekly approval page] -> [5 Publisher] -> [6 Traffic] -> [7 Feedback loop]
```
1. **Niche finder** (GitHub Action, weekly): demand signals from Etsy search/listings, seasonal calendar, trend lists; scores niches (demand vs competition). Owner seeds are expanded to ~50 candidates per batch.
2. **Design generator**: two tracks
   - Text/icon designs rendered by code (SVG→PNG) at any print size (e.g., 4500×5400) — zero upscaling, lowest trademark risk.
   - AI art via Cloudflare Workers AI FLUX (hard cap ≈100 images/day, stays in free allocation) + free upscaler run in Actions.
3. **Analyzer** (the "human job"):
   - Trademark: every word/phrase in design + title/tags vs USPTO (free).
   - Look-alike: Google Cloud Vision web detection (free quota) + perceptual hash vs scraped top-seller thumbnails per niche.
   - Quality: resolution, transparency, print-area fit, artifact detection (hands, garbled text).
   - Critic panel: 6–10 personas (e.g., dog-mom millennial, Gen-Z buyer, art lover, gift shopper, niche hobbyist, skeptic) via Gemini + Workers AI vision; each scores "would buy / looks AI-fake / feels unoriginal". Pass = threshold + no hard fails.
   - Output: pass/fail + reasons; failures get regenerated with critic feedback (layered AI).
4. **Weekly approval page**: one page listing the week's passed designs with mockups; owner taps approve/reject (≤10 min). Rejections + reasons train the analyzer thresholds. Removed once analyzer–owner agreement is high for several weeks.
5. **Publisher**: Printify API → Etsy (listing copy, tags, AI + production-partner disclosure built in). TeePublic: system prepares files + copy; owner uploads in the same weekly window (optional).
6. **Traffic**: reuse existing posting setup — Pinterest pins (POD-friendly, long shelf life), IG/FB Reels, TikTok via Buffer API. Original mockup/lifestyle videos only.
7. **Feedback loop**: sales + views per design → winners get more product types/colors; zero-view listings older than ~4 months are not renewed (saves listing fees).

## Phases & timeline
| Phase | When | Deliverable | Owner time |
|---|---|---|---|
| 0. Accounts | This week | Etsy shop (new brand), Printify free account linked to Etsy, TeePublic account; one ~$30 sample order | ~1–2 h once |
| 1. Pipeline core | Weeks 1–2 | Repo, niche finder, text-design track, analyzer v1, approval page | 0 (review results) |
| 2. First launch | Weeks 2–3 | 20–30 listings across 2–3 niches; hoodie, tee, cap, mug, tote | 10 min |
| 3. AI art + critics | Weeks 3–6 | FLUX track + full critic panel + similarity search | 10 min/wk |
| 4. Traffic layer | Weeks 4–8 | Auto Pinterest + Reels + Buffer TikTok from approved designs | 0–10 min/wk |
| 5. Scale & prune | Month 3+ | Weekly batch of 10–20 new listings, double down on winners | 10 min/wk |

Kill/pivot rule: by end of month 3, fewer than 10 total sales → change niches/product mix before adding volume.

## Money — conservative
**Start:** ~$30 (one sample order) + possible small one-time Etsy setup fee. **Monthly:** Etsy listing fees only, ≈$2–8/mo (100–300 listings renewed every 4 months, only renewing ones with views). Cloudflare/GitHub stay inside current plans. Optional later: Printify Premium $39/mo only if volume justifies (cheaper base costs).

Per-sale net on Etsy ≈ $9–11 (tee/hoodie mix, after Printify cost + Etsy fees; Etsy Offsite Ads can take a cut on ad-driven sales).

| Period | Expected sales | Profit / month | Owner time |
|---|---|---|---|
| Week 1 | 0 | -$30 (sample) | 1–2 h setup |
| Month 1 | 0–3 | $0–25 | 10 min/wk |
| Month 2 | 2–6 | $15–60 | 10 min/wk |
| Month 3 | 4–10 | $35–100 | 10 min/wk |
| Month 6 | 8–20 | $75–200 | 10 min/wk |
| Month 12 | 15–45 | $140–450 | ≤10 min/wk |

## Owner decision — Amazon Merch on Demand (parked)
| Option | Extra $/mo at month 12 (est.) | Risk to main seller account |
|---|---|---|
| A. Stay off Amazon (recommended) | $0 | None from this project |
| B. Merch on Demand, owner clicks publish, text-only designs | +$30–150 | Low but **not zero** (same Amazon identity; IP strikes are the common termination cause) |
| C. Printify → main seller account | +$50–200 | Direct exposure — not recommended |

---

# Idea 2 — Affiliate social accounts (after Idea 1 Phase 3)
- Same pipeline pieces reused: generator, critics, posting, Buffer for TikTok (public posts, free plan 3 channels / 10 queued each).
- Content must be original (commentary/transformation) to satisfy Amazon Associates' 2026 rules and IG/FB originality ranking.
- Cost $0. Conservative: month 3 $5–40/mo, month 6 $30–150/mo, month 12 $100–300/mo. Owner time ≈10 min/wk.
- Bonus: the same accounts can drive traffic to the POD designs (Etsy), so both ideas share the audience.

## Channel comparison — conservative profit/month (estimates; owner decision pending)
Assumptions: image designs, ~10/week approved; profit/sale ≈ $9–11 Etsy, $8 eBay, $10 TikTok Shop, $2.44–4.88 Merch. Upper ends of different channels rarely happen together.
| Month | Amazon Merch only | Etsy | eBay | TikTok Shop | Off-Amazon combined |
|---|---|---|---|---|---|
| 1 | $0–10 (10 slots) | $0–15 | $0 | $0–10 | $0–20 |
| 3 | $5–40 (25 slots) | $20–55 | $0–15 | $0–30 | $20–90 |
| 6 | $25–120 (100 slots) | $45–140 | $8–40 | $20–100 | $70–280 |
| 12 | $60–300 (500 slots) | $95–300 | $25–80 | $50–250 | $150–550 |
Owner time: Merch ~10 min/wk; Etsy/eBay ~0 after approval; TikTok Shop +~30 s per video to link product.

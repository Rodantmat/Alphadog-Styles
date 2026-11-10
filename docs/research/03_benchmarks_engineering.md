# 03 - Benchmarks and recommender-engineering research (wording/writing for short-form video)

**Pages fetched: 59** successfully returned (counting 2 that returned a 404 or an empty shell, #14 and #33, which are marked "no data"). Not fetched (allowlist block or client error, excluded from the count): dashsocial.com blog, two dashsocial benchmark PDFs, socialpilot.co/blog/instagram-reels-algorithm. Reddit skipped. Research date: 2026-11-10. Source types: (5) engineering/recommender, (6) benchmark reports.

Reliability key: H = large first-party dataset with method stated; M = dataset stated but secondary/summary or internal inconsistencies; L = marketing page, no method, or self-reported anecdote.

## (a) Log of every fetched page

| # | URL | Type | Date | Dataset / method | Key numbers | Rel. |
|---|---|---|---|---|---|---|
| 1 | socialinsider.io/blog/social-media-caption-length-best-practices/ | 6 | Oct 2026 (data Jan-Sep 2026) | 9.66M TikTok, 28.6M IG, 38.5M FB posts; brands 1K-1M followers | TikTok ER by caption words: <30w 4.9%, 30-60 4.5%, 60-90 4.3%, 90+ 3.9%. IG Reels: <30 0.20%, 30-60 0.25%, 60-90 0.25%, 90+ 0.20%. FB Reels: 30-60w best 0.28% | H (follower-size inconsistency) |
| 2 | socialinsider.io/blog/tiktok-hashtags-stats/ (TikTok benchmarks) | 6 | Apr 2026 (figures are 2025) | 40.7M videos, ~257K accounts | TikTok ER by views 4.20% (3.85% in 2024); small accounts 1-5K 4.40%; no hashtag/caption data on page | M (date inconsistency) |
| 3 | socialinsider.io/blog/instagram-reels-length/ | 6 | Jul 2026 (Jan-Jun 2026) | ~9.77M Reels, ~295K profiles | ER by length: 0-30s 0.28%, 30-45 0.30, 45-60 0.35 (best), 60-90 0.30, 180+ 0.15. Median views 1-30s 4,700; 45-60s 10,374 | H |
| 4 | socialpilot.co/reports/tiktok-hook-analysis | 6 | 2026 | ~1.5M TikTok posts (Q1 2025); gated | Caption sweet spot 101-200 chars; 31-60s linked to loyalty/comments. No hook data on the page despite title | L |
| 5 | metricool.com/press-release-tiktok-study-2026/ | 6 | May 2026 | 2,314,756 TikTok posts, 92K+ accounts, Jan-Feb 2025 vs 2026 | Views -31%; any hashtag +5% views, +9% interactions; question in caption +26.19% comments; peak 6-9pm, 8pm top; 96% of reach in 10 days | H |
| 6 | metricool.com/press-release-instagram-study-2026/ | 6 | Jun 2026 | 24,364,803 IG posts, 375,118 accounts | Question in caption +36.7% comments; comment CTA +202.78% comments; hashtags -31.7% views, -33.9% interactions; Reels 8.5s avg watch time; carousel 9x saves | H (correlational) |
| 7 | metricool.com/how-many-hashtags-to-use/ | 6 | 2026 | IG number from 24M study; others are recommendations only | Recommends 3-5 IG/TikTok; notes hashtag penalty is correlation | M |
| 8 | arxiv.org/pdf/2209.07663 (Monolith) | 5 | 2022 | ByteDance paper; Criteo + live ads A/B | Real-time training; ID-based features only; no text/caption features described; online AUC gain ~14-18% in ads A/B | H (not confirmed as TikTok production) |
| 9 | medium.com/pinterest-engineering/building-pinterests-video-platform | 5 | ~2019 | Engineering blog | Video content analysed (objects/topics) feeds rec and search; ~10B recs/day; no text-signal detail | M |
| 10 | medium.com/pinterest-engineering/understanding-pins-through-keyword-extraction | 5 | ~2018 | Engineering blog; XGBoost on crowd labels | Text fields used: pin title, description, URL, board name/description, page title/desc, search queries, objects detected in image; keywords found in multiple fields scored higher | H |
| 11 | socialmediatoday.com/news/instagram-shares-algorithm-insights-2025/738034/ | 5/6 | Jan 22 2025 | Mosseri statements | Top signals: watch time, likes, sends; likes per reach (followers), sends per reach (non-followers) | M-H (official statement) |
| 12 | thenewstack.io/what-makes-tiktoks-algorithms-so-effective/ | 5 | ~2023 | Secondary writeup of Monolith + NYT | Likes, comments, watch time; diversification; Monolith unconfirmed for TikTok | M |
| 13 | socialinsider.io/blog/instagram-reels-statistics/ | 6 | Jun 2026 (upd. Nov 2026) | 9,771,822 Reels | Reach rate by length: 30-60s 5.60%, <30s 5.20%, 60-90s 5.30%, 90-120s 4.30%, >120s 3.50%. E-commerce Reels ER lowest listed at 0.05%. Reels/month: 8 (1-5K accts) to 20 (100K-1M) | H |
| 14 | socialinsider.io/press-releases/tiktok-performance-data.html | 6 | - | 404 page | No data | n/a |
| 15 | quso.ai/research/social-media-engagement-rate-benchmarks | 6 | 2026 | 219K+ matured posts (also says 508K, 1,900 creators) | Median ER TikTok 2.26%, IG 1.39%, YT 1.14%, FB 0.99%; "captioned content outperforms" with no number | M |
| 16 | posteverywhere.ai/blog/social-media-benchmark-report | 6 | 2026 | Compilation of Socialinsider/Hootsuite/Sprout/Buffer | IG caption 138-150 chars; front-load first 125 chars; TikTok 1-5 tags (+5% views); skip #fyp; TikTok completion best 21-34s; Shorts 40s+ +33%; replies to comments +21% IG; own table internally conflicts | L-M |
| 17 | socialpilot.co/reports/tiktok-strategy-insights | 6 | 2025 | ~1.5M TikTok posts Q1 2025 | Same as #4: 101-200 chars; 31-60s | L-M |
| 18 | insights.ttsvibes.com/?p=780 | 6 | 2025-26 | No named dataset or method | Captions +23% likes; <100 chars +21% ER; question +44% comments; CTA +32% comments; caption hook +21% watch duration; 1-3 emojis best; 3-6 hashtags; product-review captions 100-200 chars. Internal math errors | L |
| 19 | buffer.com/resources/instagram-algorithms/ | 6 | Oct 23 2026 | Cites Buffer 4M, 9.6M, 100K-user studies | Mosseri: ~half of IG video watched without sound so on-screen text matters; hashtags don't help reach; reply to comments +21% ER; reposters limited since Apr 2026; Reels reach 36% > carousels | M-H |
| 20 | socialmediatoday.com/news/pinterest-outlines-recent-improvements-to-feed-ranking... | 5 | Sep 2020 | Pinterest blog summary | Positive video label = view >10 s; video distribution +40%; video pin topic tags not hashtags | M-H (dated) |
| 21 | sproutsocial.com/insights/pinterest-algorithm/ | 6 | 2026 | Guide, no dataset | Keywords in title/description/board; 2-3 keyword phrases in description; clear text overlays on static pins; 5-10 fresh pins/day claim | M |
| 22 | alphaxiv.org/abs/2603.03544 (PinCLIP) | 5 | Mar 2026 | Pinterest paper, ~890M pins, online A/B | Text (title, description, synthetic caption, keyword/query text) fused with image; surface repins +0.91% home, +1.84% related, +0.96% search; fresh repins +5% to +15%; ads CTR +5.02% | H |
| 23 | think.resoneo.com/pinterest/ | 5/6 | Jun 2026 | Independent reverse engineering, 263 signals; author tests | OCR text in image read and indexed; alt text indexed; saves > likes; outbound click 5s+ = good, 120s+ strong; no numeric text weights | M-L |
| 24 | medium.com/pinterest-engineering/building-pin-cohesion | 5 | ~2019 | Engineering blog | OCR on pin images; BM25 on page text; title+description carry main topic | H |
| 25 | socialmediatoday.com/news/content-diversification-is-key-to-engagement-on-pinterest/816906/ | 5 | Apr 7 2026 | Summary of Pinterest engineering post | Visually repetitive content less engaging; feed diversity optimised; visual+text embeddings | M-H |
| 26 | medium.com/pinterest-engineering/taste-graph-part-1 | 5 | ~2018 | Engineering blog; LR on crowd labels | Text from title, description, board, link, alt text; ~3M interest dictionary; top 25 per pin; precision 71%->79% | H |
| 27 | buffer.com/resources/data-best-content-format-social-media/ | 6 | Mar 19 2026 | 45M+ posts | TikTok video ER 3.39% vs photo/carousel 1.92%; Pinterest video 5.75% vs images 3.15% (+83%); IG reels ER 3.3%; no length/caption data | H |
| 28 | buffer.com/resources/how-often-to-post-on-instagram/ | 6 | Aug 13 2025 | 2.1M IG posts, ~102K accounts | 3-5 posts/week sweet spot; reach per post +12% (3-5), +18% (6-9), +24% (10+) vs 1-2; zero-post week penalty | H |
| 29 | buffer.com/resources/instagram-reach-engagement-analysis/ | 6 | Oct 23 2024 | 4M+ posts, 2022-24 | Reels reach +36% vs carousels, +125% vs images; carousels engagement +12% vs Reels | H |
| 30 | quid.com 2026 social media industry benchmark report (Rival IQ) | 6 | Mar 5 2026 | 150 companies x industry, "millions of posts" | TikTok median ER 2.01%, IG 0.30%; IG 3.69 posts/wk, TikTok 1.98 videos/wk | H |
| 31 | get.rivaliq.com 2025 benchmark PDF | 6 | 2025 | 2,100 companies; ~410K TikToks, 925K IG posts | TikTok median ER 1.73%; IG 0.36%; Retail TikTok 1.28%, 2.59 videos/wk; Retail IG 0.160%; hashtags #giveaway/#win lead retail IG; holiday tags top | H |
| 32 | engineering.fb.com Facebook Reels UTIS (Jan 14 2026) | 5 | Jan 2026 | Meta; survey responses; A/B >10M users | Interest match goes beyond topic: audio, production style, mood, motivation; precision 48.3%->63.2%; high survey ratings +5.4%, total engagement +5.2% | H |
| 33 | transparency.meta.com Facebook Reels page | 5 | - | Page returned empty shell | No data | n/a |
| 34 | ai.meta.com/blog/ai-unconnected-content-recommendations/ | 5 | 2023 | Meta AI blog | Models extract text, classify topic/genre, predict hashtags, fall back to visual/audio when captions incomplete | M-H |
| 35 | blog.acolyer.org Deep Neural Networks for YouTube Recs | 5 | 2016 | Covington et al. summary | Objective = expected watch time via weighted logistic regression; clicks alone promote clickbait | H (old) |
| 36 | wersm.com quintly TikTok study | 6 | ~2020 | 32.8K videos from top 50 TikTok accounts, 21 months | Shorter descriptions had higher ER; branded-hashtag challenge videos did better; top videos often had no hashtags | M (dated, celebrity accounts) |
| 37 | ppc.land Emplifi Reels study | 6 | Dec 2023 | "Thousands" of brand accounts | Reels 6x story reach; >90s Reels >2x TikTok median views | M |
| 38 | posteverywhere.ai/social-media-terms/hook-rate | 6 | - | Glossary page without data | No hook-rate numbers | n/a |
| 39 | dev.to/bulkdl hook engineering | 6 | Jun 2026 | Author's own 120 videos + 847 "viral shorts"; self-reported | Scroll window TikTok 1.7s, Reels 1.4s; 68% TikTok views start muted; text overlays on weak-hook videos improved 2.1x; curiosity+pattern interrupt +47% retention vs single | L |
| 40 | brands.joinstatus.com/tiktok-reels-length | 6 | 2024 | 2,000 creator videos (May-Jul 2024) | TikTok <60s most views; Reels 60-80s +71% views vs <60s; <=20s second | M |
| 41 | metricool.com/instagram-research-study/ | 6 | 2026 | 24,364,803 posts | Report gated; carousel 9x saves; Reels watch time doubled | M |
| 42 | metricool.com/tiktok-strategy | 6 | 2026 | Cites 2.3M study | Comment CTA +14% comments; like CTA -60% likes; question +26% comments; tag friend small accts +46% comments; first second decides (advice not data); search ~4% impressions | M-H |
| 43 | metricool.com/press-release-metricool-ecommerce-report/ | 6 | Aug 2026 data | 3,234 posts, 72 US ecommerce brands (incl. pet category) | 36% of captions have a CTA; CTA vs no-CTA performed the same within brand; explicit promo posts only 3.2% and worst performers; community/tutorial slightly above average; TikTok Shop tag in 1.8% | H for ecommerce, small n |
| 44 | netinfluencer.com TikTok volume +80% | 6 | 2026 | Metricool 2.31M posts | Avg views per post 32,895; FYP 73% of views, hashtags 10%, search 4%; any hashtag +5% views +10% interactions; comment CTA +14%; like CTA -60% | H |
| 45 | emarketer.com carousels and questions | 6 | 2026 | Metricool 24.4M | Question +37% comments; 70% of views in 3 days | M-H |
| 46 | shno.co content performance stats | 6 | 2026 | Aggregator listing 17 sources | No numbers on captions/hooks; TikTok best length 15-60s; FB >1 min best | L |
| 47 | shortsintel.com engagement benchmarks | 6 | 2026 | Aggregator | Shorts median views 268 (2025) vs 86 (2024); YT median ER 0.21%; no title/length data | L-M |
| 48 | postplanify.com engagement benchmarks | 6 | Oct-Nov 2026 | 19,007 posts, 414 accounts + cited sources | TikTok ER by view: 4.20% (Socialinsider) vs 0.74% (own) - definition dependent; IG 3-5 posts/wk ~2x reach vs 1-2 | M |
| 49 | clipspeed.ai Reels hooks | 6 | 2026 | 2,421 TikTok hook posts (stratified by follower band) | Scenario hooks ("POV", "When you") 3.0-5.9x plays vs question hooks; questions worst at 100K+ (0.60x); speech helped in every band; on-screen text alone added nothing >1K followers; hook length ~noise | M |
| 50 | truefuturemedia.com two-step hook test | 6 | Sep 2025 | No data | 5-10 word hook, 1-3s on screen, test 3 variants | L |
| 51 | nestscale.com increase hook rate | 6 | 2026 | Cites Motion; mostly unsourced | Hook rate (3s views / impressions): <20% below avg, 20-35% avg, 35-50% good, >50% excellent; text overlay + motion up to +50% 3s retention | L-M |
| 52 | paraschopra.github.io Reels explainer | 5 | ~2024 | Explainer; weights illustrative | Watch duration strongest; replays, shares, saves > likes; NLP reads captions and comments; audio and hashtags are item features | M |
| 53 | metricool.com/tiktok-trends-going-viral/ | 6 | 2026 | Metricool 2.3M | 1-5 descriptive hashtags, skip #fyp; no hook/caption-length data | M |
| 54 | netinfluencer.com Instagram views +27% | 6 | 2026 | Metricool 24.36M | Reel avg watch time 4s -> 8.5s; comment request +203%; save request +92%; like request -5%; question +37%; hashtag -32% views | H |
| 55 | marketing4ecommerce.net what works on IG 2026 | 6 | 2026 | Metricool 24M summary | Instagram now indexes captions for keyword search; 1-2 relevant hashtags; Reels 65% of views in 3 days | M |
| 56 | socialmediatoday.com Emplifi Reels report | 6 | Dec 19 2023 | 1,300+ brand profiles | Reels <30s median views 6,145; 30-90s 7,830 | M |
| 57 | ppc.land Meta UTIS | 5 | 2026 | Secondary on Meta paper | Survey-based interest model; content attributes audio/style/mood | M |
| 58 | hackernoon Monolith | 5 | 2023 | Secondary | Streaming Kafka/Flink loop, minute-level sync; feedback in near real time | M |
| 59 | dev.to YouTube recommendation | 5 | ~2019 | Secondary on Covington paper | Weighted LR on watch time; video length not directly ranked; ~50 recent watches/searches | M |

## (b) Consolidated findings by theme (with conflicts)

### 1. What the recommenders actually optimise (engineering sources)
- Instagram (Mosseri, #11, #19): watch time, likes, sends are the top three; likes per reach matter slightly more for followers, sends per reach slightly more for non-followers. About half of IG video is watched without sound, so on-screen text matters (#19).
- Reels item features include topic, audio, hashtags, video age; NLP reads captions and comments (#52, illustrative weights only). Meta's unconnected-content system extracts text, predicts hashtags, and uses visual/audio when captions are thin (#34).
- Meta Facebook Reels (#32, #57): interest match is not just topic; audio, production style, mood and motivation count. Survey-aligned ranking raised total engagement +5.2% in a >10M-user test.
- YouTube (Covington, #35, #59): objective is watch time, deliberately not CTR, because clicks reward clickbait. Implication: a hook that over-promises and loses viewers in 2 seconds is penalised.
- ByteDance Monolith (#8, #12, #58): the published paper uses ID features and real-time feedback only; it describes no text/caption features. Do not infer TikTok caption weights from it. Unconfirmed as TikTok production.
- Pinterest (#10, #22-26): text is explicitly used. Title, description, board name/description, linked page text, OCR from the image, search queries tied to saves, and auto alt text feed interest assignment and PinCLIP (text+image fused; online repin lifts +1% to +15%). Keywords present in several fields score higher. Video "good view" = >10 s; saves outrank likes (#23, independent source). Visual repetition is penalised at feed level (#25).
- No source documents a hook-text weight in any recommender. Gap stated honestly: the link from wording to ranking is via watch/rewatch/send behaviour, plus classification (keywords, OCR).

### 2. Caption length
- Socialinsider (#1, 9.7M TikToks): shorter is better on TikTok, <30 words 4.9% vs 90+ 3.9%. Instagram Reels flat: 30-90 words 0.25% vs 0.20% at the extremes. Facebook Reels best at 30-60 words.
- CONFLICT: SocialPilot (#4, #17, 1.5M TikToks) says 101-200 characters is the sweet spot; ttsvibes (#18, unsourced) says <100 characters. Quintly (#36, 2020) says shorter. Reconcile: roughly 100-200 characters (about 15-35 words) sits where both land; the <30-word bucket is the best in the biggest dataset.
- Instagram: front-load the first 125 characters (#16, aggregator).

### 3. Hashtags
- Metricool 24M Instagram (#6): any hashtag -32% views, -34% interactions (correlational). TikTok 2.3M (#5, #44): any hashtag +5% views, +9-10% interactions; hashtag traffic 10% of views, search 4%.
- CONFLICT between platforms, and Mosseri says hashtags do not help reach (#19). Consensus: 1-5, specific, no #fyp/#viral. Rival IQ (#31) lists #giveaway/#win/holiday tags as top retail engagement tags, which are contest and seasonal tags, not product-descriptive ones.
- Pinterest video pins use topic tags and keywords in title/description, not hashtags (#20, #21).

### 4. Questions and CTAs
- Metricool 24M IG (#6, #45, #54): caption question +37% comments; comment-request CTA +203% comments; save request +92% saves; like request -5% likes.
- Metricool 2.3M TikTok (#5, #42, #44): question +26% comments; comment CTA +14% comments; like CTA -60% likes. Direction is consistent: ask for comments or saves, never likes.
- CONFLICT: Metricool ecommerce (#43, 72 brands, n=3,234): CTA and no-CTA captions performed the same within a brand; 36% of captions had a CTA. Explicit promotional posts were the worst performers. Comments are not the goal for a shop, so the CTA lift may not convert to sales.
- Question HOOKS (first line on video) are a different thing from question CAPTIONS: ClipSpeed (#49, 2,421 TikToks) found question hooks weakest and scenario hooks ("POV", "When you...") strongest; moderate evidence.
- Replying to comments: +21% engagement IG (Buffer, #19, #48), correlational.

### 5. Hooks and on-screen text
- Mosseri: half of IG video is muted, so on-screen text matters (#19). Self-reported claims: 68% TikTok views start muted (#39, unnamed source).
- ClipSpeed (#49): spoken hook helped in every follower band; on-screen text alone added nothing above 1K followers after controlling for size. For a silent slideshow reel this means text should be paired with a strong first image and music, not relied on alone. Small, business-heavy sample.
- Hook rate benchmarks (#51): <20% weak, 20-35% average, 35-50% good, >50% excellent; Motion ads average 25-30%. Low reliability.
- Scroll decision window 1.4-2.3 s (#39, unsourced). Hook text 5-10 words (#50, #51, no data).
- Weak evidence overall for any specific hook wording. The one dataset-backed pattern: scenario/POV beats question. Everything else is practitioner advice.

### 6. Video length
- Socialinsider IG (#3, #13, 9.77M): best ER and median views at 45-60s; <30s has the lowest median views (4,700 vs 10,374); reach rate peaks 30-60s (5.6%) and <30s is close (5.2%).
- Statusphere (#40, 2,000 videos): Reels 60-80s +71% views vs <60s; TikTok <60s best.
- Emplifi 2023 (#56, #37): longer Reels get more median views; <30s 6,145 vs 30-90s 7,830.
- CONFLICT with quso/postEverywhere (#16): TikTok completion best 21-34s; Reels 15-30s for entertainment. Reconcile: longer wins on views and absolute reach in brand datasets; shorter wins on completion rate. A 10s slideshow is in the weakest bracket for median views on IG in the large datasets but strongest for completion; the Pinterest signal is >10s view, so 10s sits exactly at the boundary (#20).
- No source measured a 10s product slideshow specifically.

### 7. Formats and e-commerce context
- Video beats photo/carousel on TikTok (5.6x views, 7.8x interactions, #44; ER 3.39% vs 1.92%, #27). Carousels beat Reels on IG engagement/saves (Buffer #27, Metricool #6); Reels win on reach. Pinterest video ER 5.75% vs images 3.15% (#27).
- E-commerce Reels ER is the lowest listed industry (0.05%, #13). Retail TikTok median ER 1.28% (2025), 2.59 videos/week (#31). Pet category included in Metricool's ecommerce set (#43) but no pet-specific number was published on the page.
- Posting frequency: IG 3-5/wk doubles reach vs 1-2 (#28, #48); more is better up to 10+ for reach (+24%). TikTok brand median ~2/wk (#30, #31). Metricool: 96% of TikTok reach in 10 days; 70% of IG views in 3 days (#5, #6) so each post has a short life and needs volume. Posting time: 6-9pm TikTok peak, 7-9pm IG (#6, #44), which fits the existing 8-9pm PT evening slot for volume posts.

### 8. Search / keyword wording
- Instagram now indexes captions for keyword search (#55); Mosseri: naming topic in captions and on-screen text helps "Your Algorithm" matching (#19). TikTok search ~4% of impressions (#42). Pinterest relies most on text (#10, #21, #22, #26). So breed names and product nouns must appear literally.

## (c) Concrete wording implications for a dog-apparel brand

These are inferences, labelled by strength.
1. Put the literal breed + product in the caption and on-screen text (e.g. "Golden Retriever line art hoodie"). Strong support: Pinterest text pipeline (#10, #22, #26), Instagram caption indexing (#55), Mosseri topic matching (#19). Repeat the same breed term in title, description and on the image/overlay for Pinterest (multi-field agreement scores higher, #10).
2. Keep captions short: about 100-200 characters (15-35 words) on TikTok/Reels; put the breed and key hook in the first 125 characters. Moderate support (#1, #4, #18); conflicts exist.
3. Hashtags: 1-5 specific ones (#goldenretriever, #dogmom, #dogloverGifts style niche tags), none generic (#fyp, #viral). Expect hashtags to help TikTok a little (+5% views) and not help IG reach (#5, #6, #19). On Pinterest use keyword phrases in title/description, not hashtags.
4. End with a comment or save prompt tailored to dog owners ("Which breed should we draw next?" / "Save for a dog-mom gift") and never ask for likes. Direction consistent across both Metricool datasets (#5, #6); caveat: it lifts comments/saves, and ecommerce CTA tests showed no overall difference (#43). Use one question per caption.
5. Opening on-screen text: use a scenario/POV line ("POV: you finally found a hoodie of your dog", "When your dog has its own merch") over a question ("Does your dog need a hoodie?"). Moderate-low support (#49, TikTok only, business-heavy sample). 5-10 words, shown in the first 1-3 seconds. Do not rely on text alone; pair it with a strong first image and music, since text-only added nothing in #49.
6. Avoid explicit hard-sell wording ("Buy now", "50% off") as the lead; explicit promo posts were the worst performers relative to brand average in ecommerce data (#43). Lead with identity or gift framing and put the product link in the profile/last frame.
7. Prefer community/story lines (dog-owner identity, naming the breed fans) over product specs; community and tutorial-type content was slightly above average (#43).
8. Length decision for the 10s slideshow: big datasets favour 30-60s on IG for views, but 10s sits at the Pinterest 10-second "good view" threshold and maximises completion. Do not change the hook wording based on length data; instead consider testing a 15-20s variant. Not tested by any source.
9. Since reach lives within 3 days (IG) / 10 days (TikTok), plan volume; wording needs variety across posts (Pinterest explicitly penalises visual repetition, #25). Vary breeds and phrasing rather than repeating the same line.
10. Gaps: no benchmark isolates pet apparel, slideshow reels, or hook wording as a causal variable. All text/engagement numbers above are correlations from brand datasets, so A/B test the first 5-10 words on the brand's own posts and measure 3s hold and sends/saves.

# Engagement + reach research, 2026-11-22 (owner: "deep research, implement all")
~35 sources read (full pages, not snippets). Findings were checked against our own Instagram numbers (Windsor, 30 days: 33 reels, median ~25 views, reach 8-52, shares 0-2, skip rate 0.38-1.00, avg watch 1.7-10 s, new v5 reels Nov 21-22 reached 38-52 accounts vs ~13-25 before; n is tiny).

## What the sources agree on (acted on)
- Sends/shares per reach is the top signal for reaching NON-followers; watch time + likes per reach complete the top three (Mosseri, Buffer IG algorithm guide, Keywords Everywhere timeline, uppbeat). -> keep one "send this to a <breed> owner" ask (done in rule 16).
- Originality: Meta/IG demote reposts and low-value edits (Apr 30 2026 extended to photos/carousels). Ours is original; no third-party watermarks. -> keep.
- Keywords in caption/on-screen text beat hashtags for discovery: IG (search bar text is the top search signal), TikTok (first line of caption, on-screen text in first 3 s, spoken words), Pinterest (title, description, image text, board names). Hashtags: IG hard cap 5 (Dec 2025); Mosseri says no reach benefit; Metricool (24M posts) found tagged posts with fewer views (confounded); Metricool TikTok SEO says 1-2 tags +5% views. -> 3 descriptive tags everywhere (not 0: sources conflict).
- Comment prompts: questions +36.7% comments, comment CTAs +202.8% (Metricool 24M posts); replying to comments +21% IG engagement, ~63% of profiles better (Buffer 52M posts); TikTok: reply in first 15 min. -> added "What is your <breed>'s name?" line.
- Hooks: first 1-3 s decide; pet/shoppable TikTok data (Virlo, 7,785 videos, Oct-Nov 2026): shock/bold-claim hook 37.7% beat 2x usual views; call-out hooks highest medians among shoppable pet videos; motion in the first frame 44% beat 2x (3.2% of videos use it); "relatable scenario" weakest (21%). -> hook rotation (below); all our shots already zoom/move.
- Seamless loop: Emplifi (10,110 FB Reels): loops on videos up to 7 s gave replays +18.7%, reach +23.6%, engagement +16.1%; longer videos rarely reach the loop point. We loop but run 10.1 s (owner ideal 8-10 s) -> OPTION below.
- Vertical +20.9% reach (Emplifi), text overlay +5% 3-s retention on music videos, speech in first 3 s +24.7% 10-s retention but replays -10.6%, person visible 1 s in first 3 s +10% 10-s retention (we open Post B with a person shot already).
- Holiday: Pinterest says gifting activity starts early and runs through "Q5" (Dec 26-Jan); ~45-90 days lead for seasonal pins. -> gift wording in captions/pins from Nov 15 to Dec 24.
- Pinterest: ~10 distinct fresh pins per product each with its OWN URL; keyword-first titles 40-100 chars, descriptions 100-500 chars, 2-3 hashtags, text on image <=40%; video pins engage 5.75% vs images 3.15% (Buffer); results take 3-6 months; claim the website; Rich Pins. -> unique breed deep link + UTM per pin; domain claim is an owner item.
- Timing (Buffer 7M TikTok posts, IG data): IG best 6-9 pm weekdays, Thu 9 am; TikTok best Sat, Sun 9 am, evenings 6-11 pm; FB 8-11 am weekdays. Our 9:00/10:00 PT + 20:00 PT slots already match. No change.
- Frequency: 3-5 Reels/week is "enough" per marketing guides, but Buffer's 2.1M-post study shows 10+ posts/week = 5.5x the follower growth of 1-2 and reach per post did not fall. We post 14/week/app: keep.

## Conflicts / weak claims (NOT adopted)
- "Sends weigh 3-5x likes", watch-time thresholds, skip-rate updates: Instagram never published them (Keywords Everywhere debunk list).
- "Post at :15/:45", "2-4 AM EST off-peak", "60-180 s gets preferential TikTok distribution": single-vendor, unsourced.
- Trial Reels need 1,000+ followers (we have 43): not available.
- Instagram carousels: Buffer says carousels get 2.09x engagement rate but Reels 1.36x the reach; Metricool says carousels 9x saves. Mixed, and see cap below.

## Implemented 2026-11-22 (rule 16h-k)
1. Hook rotation in postc2_build (4 call-out hooks; id in meta.json hook_id) so the 24 h/72 h comparison can tell which wording works.
2. Caption v6: breed keyword first, share ask, comment question, seasonal gift line (Nov 15-Dec 24), 3 descriptive tags; "a/an" fixed.
3. Pinterest pin.json: unique per-breed URL `https://alphadogstyles.com/?utm_source=pinterest&utm_medium=social&utm_campaign=<id>#/design?breed=<slug>` (the store reads #/design?breed=<slug>; checked) - also a candidate fix for the intermittent "doesn't allow you to save Pins" rejection (every pin used the same bare homepage URL). 3 hashtags.
4. scripts/video/recaption.py re-captioned the unscheduled c39, c40, c41.

## Needs an owner decision (numbers in the chat reply)
- Account bios/names with keywords (IG name field, TikTok, Pinterest profile) and Pinterest domain claim + Rich Pins (account settings).
- Store head tags: product og:image instead of logo.png, keyword title/description, p:domain_verify (live site change).
- More Pinterest pins / IG carousels: blocked by Buffer's 10 scheduled posts per channel (free plan) - every channel is already full.
- <=7 s seamless-loop reels vs the 8-10 s ideal; voice-over in the first 3 s (needs TTS).

## Sources (pages read)
buffer.com/resources/state-of-social-media-engagement-2026 ; buffer.com/resources/instagram-algorithms ; buffer.com/resources/best-time-to-post-on-tiktok ; buffer.com/resources/how-often-to-post-on-instagram ; about.fb.com/news/2026/03/rewarding-original-creators ; socialmediaexaminer.com/facebooks-2026-rules-for-reach-relevance ; dropified.com/blog/pinterest-ecommerce-hacks ; pingroupie.com/blog/pinterest-seo-guide-2026 ; business.pinterest.com holiday-2026-starts-now ; dev.to/fermainpariz Reels strategy 2026 + carousel guide ; opus.pro/blog/tiktoks-new-algorithm-2026 ; socialmediatoday.com Metricool 2026 Instagram study (24.4M posts) ; ecommercefastlane.com POD TikTok ideas ; dev.to/getkoro_app pet brands TikTok ; keywordseverywhere.com/news/instagram-algorithm-updates ; metricool.com/tiktok-seo ; socialsamosa.com trial reels ; socialpilot.co Reels algorithm ; uppbeat.io Mosseri carousels+sends ; socialmediatoday.com Emplifi speech/presence Reels study ; vimeo.com loop post ; emplifi.io/resources/facebook-reels-data ; virlo.ai/tiktok-ideas/pets and /data/tiktok-shop-videos/pets ; influencermarketinghub.com instagram-video-sizes (no numbers) ; alphadogstyles.com (store HTML, deep link test).

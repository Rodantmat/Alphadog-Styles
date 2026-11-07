# AlphaDog Styles social production runbook (READ FIRST in every scheduled run)

## Rules (always apply; details in docs/VIDEO_RULES.md, docs/video_rotation.md)
- 2 posts per app per day on TikTok, Instagram, Facebook, Pinterest. Post A = creative video (9:00 PT weekdays, 10:00 PT weekends). Post B = Printify-mockup reel (20:00 PT).
- Mon = 4-dog laugh (social/laugh/build.py), Thu = 2-dog laugh (build2.py), new joke/background/music/laugh track each week; other days rotate models d1-d7 with new background, music, merch. Never same style/colour/product/design back-to-back. Backgrounds and music never repeat within 2 months (music: never repeat). Merch mixed by product, colour, design and view. Text never covers merch; phone-safe area; 8-10 s ideal.
- Post B: full-screen Printify mockups, people views, popular breeds, dark shades varied (Navy, Forest, Maroon, Asphalt, Dark Grey Heather, Red), never yorkshire_terrier, pomeranian, shih_tzu, havanese, pug, mini_poodle, bichon_frise, maltese.
- Always look at the final frame(s) before publishing. Log every post: docs/style_registry.json, docs/music_log.md, social/POSTLOG.md, docs/schedule.json.

## Access
- Repo Rodantmat/Alphadog-Styles (use gh REST only; GraphQL and releases are blocked). Buffer runs only through workflow buffer-run.yml (inputs account 1 = IG+TikTok, 2 = FB+Pinterest; args: posts | plan FILE | delete IDS). Secrets BUFFER_API_KEY / BUFFER_API_KEY_2 live in GitHub; never print them.
- Buffer limit: 10 scheduled posts per channel. Pinterest board serviceId 1133710974888199746; pin entries need metadata.pinterest {boardServiceId,title,url}.
- Run workflows yourself; never ask the owner to run anything.

## Sources / storage
- Code and catalogs: main branch (scripts/video, social/, docs/). Heavy libraries (not in main): branch prod-assets (split zips). Restore:
  git clone --depth 1 -b prod-assets https://github.com/Rodantmat/Alphadog-Styles.git /tmp/assets
  cd /tmp/assets && for z in merch_lib backgrounds kl_engine media_extra; do cat $z.zip.part_* > /tmp/$z.zip; done
  cd /home/claude/alphadog-styles/out && for z in merch_lib backgrounds media_extra; do unzip -qo /tmp/$z.zip; done
  cd /tmp && unzip -qo /tmp/kl_engine.zip   # creates /tmp/kl
  The engine scripts hardcode /home/claude/alphadog-styles: the repo MUST be cloned at exactly that path. (Restore verified 2026-11-06: all zips pass integrity test.)
- Owner's copy: D:\Rodo\Projects\AlphaDog Styles\merch_library\ (merch_lib_v2.zip, backgrounds_300.zip, catalogs). Catalogs in git: docs/merch_lib_catalog.json, docs/backgrounds_catalog.json.
- Finished videos: social/videos/*.mp4 and out/postb2/bNN/{reel.mp4,caption.txt} (committed; Buffer reads raw.githubusercontent URLs). Music out/music2 (titles in list.json), laugh tracks out/sfx.
- Source mockups: out/pmk/<breed>/<type>/<colour>/<id>.jpg, out/mockget2.

## Cleanup (do at end of each run)
- Delete scratch: /tmp/kl/*.mp4 and *.jpg, out/laugh/_v.mp4 and *.png/*.jpg check images, out/postb2 temp files. Never commit out/backgrounds, out/merch_lib, out/footage (big libraries).
- Keep in git only: final mp4s for days not yet aired plus the last 14 days; older finals may stay (they are the history). Never delete anything already posted or scheduled; never touch published posts.
- Commit with git add on specific paths (docs social scripts out/postb2/<new>), never `git add -A`.

## Music supply (never repeat music)
- Tracks: out/music2/mNN.mp3, titles in out/music2/list.json (now 90, m00-m89; restored from prod-assets plus git for the new ones). Used tracks are in docs/music_log.md.
- When fewer than 10 unused tracks remain: dispatch workflow music3.yml (inputs count=60) via gh REST; it appends new Mixkit tracks to out/music2 and commits them (cloud sandbox cannot reach Mixkit directly, GitHub Actions can). git pull afterwards.
- If the generator reports "all tracks used", this is the fix; never reuse a track.

## Generator log
- social/GENLOG.md: every generator run appends start / restore / built / finish lines (or the exact error). Check it when a day is missing.

## Music library (300 tracks, themed) - supersedes the 60-track top-up above
- out/music2/mNNN.mp3 (m00-m89 older 2-digit names, m090-m299 new), catalog out/music2/list.json with fields title, artist, theme, tag, bpm, energy, file. Built by scripts/video/music4.py (workflow music4.yml, input target; energy/tempo-filtered, theme-balanced, Mixkit licence = free commercial use, no attribution).
- Themes: Electronic & House 64, Feel-good 53, Hip-hop & Trap 46, Rock & Guitar 40, Funk & Disco 37, Pop & Party 36, Chill & Lo-fi 21, Latin & Reggae 3.
- Rotation rule: pick the unused track (not in docs/music_log.md) whose THEME differs from the previous day's and from the same-day sibling post; fit the mood to the concept (hip-hop/trap for laugh videos, funk/pop for fashion, etc.). Never reuse a track. When < 30 unused remain, run music4.yml with target = current total + 150.

## MUSIC ENFORCEMENT (mandatory, every build)
1. Music is chosen ONLY with scripts/video/pick_music.py: `pick STYLE --prev-theme <previous day's theme> --sibling-theme <same-day A/B partner's theme>` returns style-matched, never-used candidates. Styles and their allowed themes/bpm are in docs/music_style_map.json (laugh4, laugh2, d1-d7, postB). A new video style must be added to that map before its first build.
2. After the video is built and passes the frame check: `pick_music.py commit STYLE FILE DATE USE` (fails if the track was used or the theme is not allowed). This writes docs/music_used.json and docs/music_log.md. A build without a successful commit is not finished.
3. `pick_music.py check` must pass before every push. Never copy a track by hand, never reuse a track, never pick outside the style's themes.
4. Also register the theme of each day's A and B in docs/schedule.json (fields A.theme / B.theme) so the next day can avoid it.

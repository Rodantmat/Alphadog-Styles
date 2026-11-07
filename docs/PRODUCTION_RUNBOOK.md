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

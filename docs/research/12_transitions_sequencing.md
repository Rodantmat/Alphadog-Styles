# 12 - Transitions, motion and sequencing for 10 s / 10-frame product reels

Pages fetched: 58 returned content (about 51 substantive; 6 were empty, paywalled or irrelevant, flagged "low" below). 8 further fetches failed (Anubis bot wall x2, URL not on allowlist x5, redirect x1) and are listed at the end, not counted.
Also verified locally: ffmpeg 6.1.1 (all snippets marked TESTED were rendered here at 1080x1920 and looked at) and librosa 1.0.0.
Reddit was not fetched (not fetchable). Nothing from Reddit is used.

## (a) Page log

| # | URL | Type | Key takeaway | Reliability |
|---|-----|------|--------------|-------------|
| 1 | ffmpeg.org/pipermail/ffmpeg-user/2020-September/050149.html | ML post | xfade custom expr variables: X Y W H P PLANE A B a0..a3 (no answer given) | med |
| 2 | bannerbear.com/blog/how-to-do-a-ken-burns-style-effect-with-ffmpeg | blog | zoompan z='zoom+0.001', centered x/y expr; pre-scale `scale=8000:-1` cures jerkiness | med |
| 3 | mko.re/blog/ken-burns-ffmpeg/ | blog | portrait pan expressions; higher fps for long pans; `on`-based linear pan | med |
| 4 | creatomate.com/blog/how-to-zoom-images-and-videos-using-ffmpeg | blog | zoom-out via if(lte(zoom,1),1.5,max(1.001,zoom-0.0015)); video input needs d=1 and pzoom | med |
| 5 | dreamengine.com.au/.../learning-the-art-of-video-editing | editing blog | shot length sets rhythm; tension/release; do not run constant high energy; test muted | med |
| 6 | capcut.com/create/music-video-pacing-emotional-montage-rhythm | vendor guide | product demo 0.8-1.5 s per shot, hook 0.5-1 s; do not cut on every beat; align motion peaks to accents; light/medium/heavy shots | med |
| 7 | vidpros.com/video-clip-length/ | blog | Reels 1-2 s/shot; claims 2.5 s avg correlates with +35% completion (unsourced stat) | low-med |
| 8 | cincopa.com/blog/5-video-editing-tips-for-engaging-short-form-videos/ | blog | open on payoff, cut to the track, concise text | low-med |
| 9 | galibgroovemarketing.blogspot.com/.../7-reel-editing-techniques... | blog | fashion: avg cut 0.3-1.5 s, >2 s loses viewers, object match cut, ONE smooth transition done well, loop first/last frame | low-med |
| 10 | fftrac-bg.ffmpeg.org/wiki/Xfade | official wiki | full transition name list; gif/mp4 recipes; no custom-expr examples | high |
| 11 | ffmpeg.org/doxygen/6.0/vf__xfade_8c_source.html | source | smoothleft/circleopen/distance code; custom vars X,Y,W,H,A,B,PLANE,P | high |
| 12 | gist.github.com/royshil/369e175960718b5a03e40f279b131788 | gist | chain xfade: normalise settb/setsar/fps; running offset; drift if overlap not subtracted per step | med |
| 13 | kiwix SO answer 63570355 | SO | offset_i = sum(first i durations) - i*fade; 4-input example | high (matches my test) |
| 14 | ffmpeg.org/pipermail/ffmpeg-user/2022-July/055132.html | ML post | long xfade chains use lots of memory; use movie= per input | med |
| 15 | ffmpeg-cvslog/2020-January/120839.html | commit | smoothleft/right/up/down add smoothstep soft edge | high |
| 16 | repositorystats.com/scriptituk/xfade-easing | repo stats | exists: xfade-easing project (CSS easings, GL transitions as xfade exprs); no usage detail | low |
| 17 | spotlightfx.com/blog/what-are-j-cuts-and-l-cuts... | blog | J = next audio leads; L = audio trails; music can run across cuts | med |
| 18 | videomaker.com/.../what-are-match-cuts-and-how-are-they-used/ | tutorial | match on action, graphic match, sound bridge | med-high |
| 19 | capcut.com/create/match-cuts-seamless-scene-transitions | vendor guide | pick ONE anchor (shape/position/colour/motion); continue motion trajectory; start with hard cut | med |
| 20 | capcut.com/create/j-cuts-and-l-cuts-dialogue-edits | vendor guide | audio lead 6-12 frames at 30 fps (dialogue); 0.5-1 s cinematic; short crossfade to avoid pops | med |
| 21 | onsetengine.pages.dev/guides/edit-videos-to-beat... | vendor guide | cut within +-200 ms of beat; nudge 1-3 frames; soft dissolves on calm, hard cuts on drops | low-med |
| 22 | ffmpeg-devel/2020-February/257073.html | patch thread | zoompan "fix shaking" patch exists; no detail on page | med |
| 23 | ffmpeg-trac/2025-April/073180.html | ticket | trac #4298 zoompan shaky still OPEN (integer rounding); only workaround is unmerged subpixel patch | high |
| 24 | fftrac-bg.ffmpeg.org/wiki/BouncingOverlay | official wiki | overlay x/y as expressions of t; repeatlast/shortest | med (truncated) |
| 25 | ffmpeg.org/ffmpeg-all.html | docs | only first 100k chars returned; no filter sections | n/a (low) |
| 26 | linux-magazine.com/.../Gobbling-Up | magazine | paywalled; custom xfade article | n/a (low) |
| 27 | skills.cat/.../ffmpeg-animation-timing-reference | skill dump | easing formulas for alpha=; UI timing 100-500 ms; durations as whole frames | low-med (approximations) |
| 28 | videomaker.com/.../6-video-transitions-that-arent-cheesy/ | tutorial | non-cheesy: J/L, motion blur, mask, light leak/bokeh overlays, glitch, flicker | med |
| 29 | checksub.com/video-editing/best-proper-video-transitions | blog | hard cut default; dissolve; avoid split/overused wipes and zooms; purposeless transitions | med |
| 30 | descript.com/blog/article/youtube-transitions... | vendor blog | default to cuts; consistency; "push for listicles and product videos"; whip is faster than wipe | med |
| 31 | driftzine.com/spotlight-on-film-editor-dominik-braz-bittrich... | interview | Cartier: slow deliberate cuts + soft dreamlike transitions; YSL: sharp cuts to soundtrack | med |
| 32 | officechai.com/.../quiet-luxury-in-motion... | article | luxury = dissolves not flashes, slow drifts, soft shadow movement, few transitions | low-med |
| 33 | videomaker.com/.../a-beginners-guide-to-the-art-of-film-burns/ | tutorial | burn = overlay in Screen mode; soft muted orange for nostalgic | med |
| 34 | easings.net | reference | names of 30 easings (formulas not on page) | high |
| 35 | engineered.at/articles/an-algorithm-for-shuffling-playlists | blog | merge-shuffle: partition by key, interleave/intersperse; not optimal | med |
| 36 | printify.com/knowledge-hub/go-viral-on-instagram/ | POD vendor | Reels 7-12 s, hook in 3 s, loopable audio, match last frame to first | med |
| 37 | shopify.com/blog/how-to-use-instagram-reels-marketing | vendor | first 3 s count; text for muted; >=30 fps; 9:16 | med |
| 38 | coinis.com/how-to/best-way-to-product-reel-for-instagram | agency | 1-2 clean transitions; keep key content in top 65% (UI covers bottom 35%) | med |
| 39 | quso.ai/blog/instagram-reels-best-practices.html | blog | strongest visual first; one idea per reel; no cut-rate guidance | low-med |
| 40 | medium.com/dataseries/playlist-optimisation-as-a-traveling-salesperson-problem | blog | ordering = TSP; greedy nearest-neighbour O(n^2); weighted feature distance | med |
| 41 | arxiv.org/abs/2203.00233 | paper | ordered submodularity: position-weighted diversity; greedy is a tight 2-approx | high |
| 42 | vidio.ai/.../what-is-intelligent-scene-pacing-for-social-videos | blog | 0.5-1.5 s cuts on Reels; breathing room; preview on phone at 2x | low-med |
| 43 | contra.com/community/ektuS8Vw-engaging-short-form-fashion... | portfolio | EMPTY page | n/a (low) |
| 44 | librosa.org/doc/dev/auto_tutorials/01-intro/06-rhythm.html | official docs | onset_strength -> feature.tempo / beat_track(units="time"); Ellis 2007 DP tracker | high |
| 45 | besthub.dev/articles/beat-detection-concepts... | blog | DP tracker degrades with tempo changes and vocal-heavy music | low-med |
| 46 | nofilmschool.com/how-to-do-a-whip-pan | tutorial | pan same direction both shots, match speed, match brightness, trim to blur peak | med-high |
| 47 | kaweah.freedombox.rocks SO 70368647 (ffmpeg drop shadow) | SO | question only, no answer | n/a (low) |
| 48 | kaweah.freedombox.rocks SO 74211898 (shadow on overlay) | SO | question only, no answer | n/a (low) |
| 49 | kiwix.lema.org SO 30384577 (move overlay) | SO | overlay x='720+t*28' linear; enable='between(t,a,b)' | med |
| 50 | gist.github.com/gibatronic/f152319bdcfa71ec14b14c26a55f7801 | gist | in-out sine slide: overlay x='(W-w)*(-(cos(PI*(t/10))-1)/2)' | med (I confirmed formula is sine in-out) |
| 51 | spliceapp.com/blog/mastering-trip-recap-transitions... | vendor | whip pans for outfit/location reveals; align at peak blur; mask transitions; jump cuts sparingly | low-med |
| 52 | ayosec.github.io/ffmpeg-filters-docs/6.0/Filters/Video/tmix.html | docs mirror | tmix frames/weights/scale; examples | high |
| 53 | baeldung.com/linux/ffmpeg-interpolate-frames | tutorial | minterpolate slow, can distort; tblend alternative | med |
| 54 | ffmpeg.org/pipermail/ffmpeg-user/2020-June/049155.html | ML post | question only (smooth video from images) | n/a (low) |
| 55 | dvinfo.net/.../premiere-cs5-transitions-dont-look-cheesy.html | forum | editors: cross-dissolve and dip to black/white are safe; cube spin "smells of cheese" | low-med |
| 56 | attnagency.com/blog/instagram-reels-strategy-brands | agency | loop: final shot flows into opening; 15-30 s typical | low-med |
| 57 | techsmith.com/blog/video-cuts-you-should-know/ | vendor | cut-in-action, cutaway, jump cut risks | med |
| 58 | borisfx.com/documentation/sapphire/ofx/filmburntransition/ | plugin docs | film burn = 3 additive flashes, slow-in/out dissolve, warm orange/magenta; recipe to imitate | med |

Failed fetches (not counted): trac.ffmpeg.org/wiki/Xfade?version=17 (Anubis), ffmpeg-devel 2017-April framestep (Anubis), ffmpeg.org/ffmpeg-filters.html, github.com/scriptituk/xfade-easing, librosa.org beat_track page, ffmpeg-user 2017-May 036072 (all not on allowlist), el-tramo.be (redirect to #3), ayosec xfade 8.0 (returned only nav).

Honesty notes: no fetched page gave an xfade custom-expression example or xfade easing; everything in section B marked TESTED I wrote and rendered myself in ffmpeg 6.1.1. Numeric pacing ranges come from blogs (low-med reliability) and agree with each other, but there is no controlled study.

## Key findings (A)

1. Pacing. Sources agree on 0.5-1.5 s per shot for Reels, product detail 0.8-1.5 s, heroes held longer (#6, #9, #42). Cutting every beat feels mechanical (#6); luxury references (#31, #32) use slower holds and soft dissolves. For a 10 s, 10-frame reel the arithmetic gives about 1.0 s per frame, which is the correct top-of-range for "elegant, not frantic". Use 2-3 beats per shot, not 1.
2. Transition language. Hard cut is the default; dissolve/fade is safe; use ONE or TWO signature transitions consistently (#29, #30, #38, #9). Motion (push/slide with easing, whip with blur, zoom-through) works when direction continues across the cut (#46, #19). Overlays (light leak/film burn) only as a rare accent, in Screen/Add, warm and soft (#28, #33, #58).
3. Match cuts and alternation. Pick one anchor per cut (silhouette, position, colour, motion) (#19). For catalogue content the useful anchor is: same garment silhouette position in frame, or same motion direction. Alternate wide/close and person/object to give rhythm (tension/release, #5).
4. J/L cuts. Audio-only concept: for a music bed, let the next beat/phrase start 6-12 frames (0.2-0.4 s) BEFORE the picture changes (J) on the hero cut. For reels the practical equivalent is: place the visual cut 2-3 frames after the beat transient so it "lands".
5. Loop. First and last frame should match in composition/colour or the last shot should fade/push into the first (#9, #36, #56). Audio: no hard stop.
6. Safe area. Keep logos/text in the top 65% (#38).
7. Cheap vs premium (from sources + my render sheet of all 58 xfade names): cheap = pixelize, dissolve (noisy), circleopen/circleclose/circlecrop/rectcrop (iris, black frames in 6.1.1), vertopen/vertclose/horzopen/horzclose, diag*, *slice, *wind, squeeze*, wipetl/tr/bl/br, radial, distance, hblur, hard-edged wipe*. Premium = hard cut, fade (short), fadeblack/fadewhite (rare), slide*/cover*/reveal* with easing (push), smooth* (soft edge), whip with blur, zoom-through, subtle light flash.

## (b) SPEC

### B1. Transition set (use ONLY these)

| Role | Name | Duration | When |
|------|------|----------|------|
| Default | hard cut (T=1 frame, xfade=fade:duration=0.033, or concat) | 0 | ~5 of 9 joins, on beat |
| Soft | `fade` | 0.30-0.40 s | light<->light frames, closeups, folded/flat |
| Soft-premium | `smoothleft` / `smoothright` / `smoothup` (built-in) | 0.40 s | person<->person, same direction as previous motion |
| Push | custom eased push (TESTED, B3-a) | 0.45 s | person -> flat/folded |
| Whip | custom push + 7-tap motion blur (TESTED, B3-b) | 0.35-0.40 s | at most 1 per reel, on the loudest beat |
| Zoom-through | custom (TESTED, B3-c) | 0.50 s | closeup -> wide only, max 1 |
| Dip | `fadeblack` | 0.35 s | only dark -> dark, or before loop point; max 1 |
| Accent | warm flash / film burn custom (TESTED, B3-d) | 0.45 s | max 1, never with whip |
| Reveal | `coverleft/right`, `revealleft/right` (built-in, hard-edged) | 0.40 s | optional substitute for push; max 1 |

Rules: max 3 distinct transition names per reel; same-direction continuity (if shot k exits right, k+1 enters from the right-to-left motion, i.e. slideleft/smoothleft; never alternate left/right back and forth more than once); durations multiples of 1/30 s; no transition longer than 45% of either neighbouring shot.

BAN: pixelize, dissolve (grainy), circleopen, circleclose, circlecrop, rectcrop (black frames), radial, distance, vertopen, vertclose, horzopen, horzclose, diagtl/tr/bl/br, hlslice, hrslice, vuslice, vdslice, hlwind, hrwind, vuwind, vdwind, squeezeh, squeezev, wipetl/tr/bl/br, hblur, zoomin (renders a single flat frame in my 6.1.1 test), fadegrays (muddy grey on bright garments), fadefast/fadeslow (just fade), plain wipeleft/right/up/down (hard-edged, reads as PowerPoint), cube spins, glitch.

### B2. Motion parameters
- Per shot slow Ken Burns: scale 1.00 -> 1.06 (person/folded), 1.00 -> 1.10 (closeup, emblem), 1.08 -> 1.00 on alternate shots (breathing). Ease: smoothstep `p*p*(3-2p)`. Max pan drift 3% of width. Never zoom >1.12 on a cutout (edge softness).
- Anti-jitter: prescale input to 2x (2160x3840) with lanczos before zoompan (TESTED; trac #4298 is still open, #23). Use `d=<frames>` on a still; do not use video input.
- Parallax (TESTED B3-e): background scaled 1.2x drifting +-30 px over the shot; subject cutout moving ~2x the bg speed (60 px settling); soft shadow layer (cutout alpha -> black 35% -> gblur sigma 28) offset +25/+40 px that eases with the subject.
- Pop-in: easeOutBack on scale from 0.80 -> 1.0 over 0.5 s (TESTED), then hold with 3% Ken Burns. Use only on hero frame 1 and at most one more.
- Hold time before/after a transition: >= 0.5 s fully clean frame so the garment can be read.
- Safe area: text/logo in the top 65%.

### B3. Tested ffmpeg snippets (ffmpeg 6.1.1)

Chain rule (TESTED, matches #13): offset_i = sum_{j<=i}(L_j) - i*T where L_j is each clip's length and T the overlap. For uneven T: offset_i = sum_{j<=i}L_j - sum_{j<=i}T_j. Total = sum L - sum T.

**(0) Full chain with Ken Burns + built-ins (TESTED, 10.0 s, ~10 s to render):**
```python
FPS=30; T=0.3; L=(10+9*T)/10; frames=round(L*FPS)+2
# per shot i:
p=f"(on/{frames-1})"; ease=f"({p}*{p}*(3-2*{p}))"
z=f"1.0+0.08*{ease}" if i%2==0 else f"1.08-0.08*{ease}"
f"[{i}:v]scale=2160:3840:flags=lanczos,zoompan=z='{z}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={FPS},setsar=1,format=yuv420p[v{i}]"
# joins:  off+=L-T ; f"[{prev}][v{i}]xfade=transition={trans[i-1]}:duration={T}:offset={off:.3f}[x{i}]"
# output: -map [x9] -t 10 -c:v libx264 -crf 18 -pix_fmt yuv420p
```
Custom expressions need gbrp inputs so all three planes are full resolution and a0/a1/a2, b0/b1/b2 are valid; helper:
`pl(p,x,y) = if(eq(PLANE,0),p0(x,y),if(eq(PLANE,1),p1(x,y),p2(x,y)))`.
Wrap: `[0:v]format=gbrp,setsar=1[a];[1:v]format=gbrp,setsar=1[b];[a][b]xfade=transition=custom:duration=D:offset=O:expr='...',format=yuv420p`

**(a) Eased push (easeInOutCubic) - TESTED:**
```
st(0,if(lt(P,0.5),4*P*P*P,1-pow(-2*P+2,3)/2));
if(lt(X,W*(1-ld(0))), PL(a, X+W*ld(0), Y), PL(b, X-W*(1-ld(0)), Y))
```
(PL = the plane selector above; for the reverse direction mirror X.) Use easeInOutQuart (`8*pow(P,4)` / `1-pow(-2*P+2,4)/2`) for a snappier feel.

**(b) Whip pan with horizontal motion blur (7 taps, TESTED):**
```python
def pl(p,x): return f"if(eq(PLANE,0),{p}0({x},Y),if(eq(PLANE,1),{p}1({x},Y),{p}2({x},Y)))"
def tap(k):
    x=f"(X+({k})*ld(1))"
    return f"if(lt({x},W*(1-ld(0))),{pl('a',x+'+W*ld(0)')},{pl('b',x+'-W*(1-ld(0))')})"
expr="st(0,if(lt(P,0.5),8*pow(P,4),1-pow(-2*P+2,4)/2));st(1,0.012*W*sin(PI*P));("+"+".join(tap(k) for k in range(-3,4))+")/7"
# xfade=transition=custom:duration=0.4:offset=...:expr='<expr>'   (expr is ~2 KB, fine)
```
Blur peaks mid-transition (sin(PI*P)), zero at both ends so frames are sharp.

**(c) Zoom-through (A zooms 1->1.5 while B settles 0.85->1) - TESTED:**
```
st(0,if(lt(P,0.5),4*P*P*P,1-pow(-2*P+2,3)/2));
st(2,clip((P-0.25)/0.5,0,1));st(2,ld(2)*ld(2)*(3-2*ld(2)));
PL(a, W/2+(X-W/2)/(1+0.5*ld(0)), H/2+(Y-H/2)/(1+0.5*ld(0)))*(1-ld(2))
+ PL(b, W/2+(X-W/2)/(0.85+0.15*ld(0)), H/2+(Y-H/2)/(0.85+0.15*ld(0)))*ld(2)
```
(here PL takes x and y, y no longer fixed to Y).

**(d) Warm flash / light-leak style accent - TESTED (planes are G,B,R order in gbrp):**
```
st(3,0.6*pow(sin(PI*P),2));
(A*(1-P)+B*P)*(1-ld(3))+if(eq(PLANE,0),215,if(eq(PLANE,1),150,255))*ld(3)
```
For a real film burn instead: overlay a 0.4-0.5 s light-leak clip with `blend=all_mode=screen` or `overlay` on a screen-keyed clip, peak on the cut frame (#33, #58).

**(e) Pop-in + parallax + shadow - TESTED (alpha cutout PNG over background PNG, 2 s):**
```
P="min(t/0.5\,1)"; S="(0.80+0.20*(1+2.70158*pow(${P}-1\,3)+1.70158*pow(${P}-1\,2)))"   # easeOutBack
[0:v]scale=1296:2304,crop=1080:1920:x='108+30*(t/D-0.5)*2':y='192',setsar=1[bg];
[1:v]format=rgba,split[c1][c2];
[c2]colorchannelmixer=rr=0:gg=0:bb=0:aa=0.35,gblur=sigma=28[sh];
[c1]scale=w='trunc(1080*S/2)*2':h=-2:eval=frame[cs];  [sh]scale=...same...[shs];
[bg][shs]overlay=x='(W-w)/2+25+60*(1-min(t/0.8\,1))':y='(H-h)/2+40':format=auto[b2];
[b2][cs]overlay=x='(W-w)/2+60*(1-min(t/0.8\,1))':y='(H-h)/2':format=auto,format=yuv420p
```
Escape commas inside expressions as `\,` when the expression is not inside single quotes within the filter string.

**(f) Overlay easing without xfade (from #50, sine in-out):** `overlay='(W-w)*(-(cos(PI*(t/10))-1)/2):(H-h)/2'`.
Other easing formulas for alpha/expr (#27, my cross-check): ease-out cubic `1-pow(1-t,3)`; ease-in-out cubic `if(lt(t,.5),4*t*t*t,1-pow(-2*t+2,3)/2)`; expo out `1-exp(-10*t*0.693)` (approx).

**(g) Motion blur options:** (i) the custom whip above (best, no re-timing); (ii) `tmix=frames=3:weights="1 2 1"` on a 60 fps zoompan source then `fps=30` (#52) gives subtle blur on Ken Burns; (iii) avoid minterpolate (slow, artifacts, #53). `gblur` sigma is not time-expression driven in 6.1.1; for a blur ramp use `enable='between(t,a,b)'` stacked 2-3 gblurs of increasing sigma, or the custom xfade blur.

**(h) Text animation:** `drawtext=...:alpha='if(lt(t,0.3),t/0.3,1)':y='h*0.08+20*(1-min(t/0.4\,1))'` (fade + 20 px rise; ease-out `1-pow(1-min(t/0.4,1),3)`), `enable='between(t,0.2,3)'`. Keep text in the top 65%, short (3 words), min 0.8 s.

**(i) Card flip (pseudo-3D):** not found on any fetched page. Practical route: squeeze width by |cos| with `scale=w='max(2,1080*abs(cos(PI*t/D)))':h=1920:eval=frame`, swap the face at the half-way point with `overlay enable`, and re-center; or use xfade `squeezeh`-style custom. Not tested; treat as optional and not premium for apparel. Recommendation: skip.

**(j) Beat detection and alignment (librosa 1.0.0 TESTED on a 120 BPM click track: tempo 117.5, beats at 1.02,1.51,2.02,... i.e. ~0.01-0.02 s late, first beat missed):**
```python
y,sr=librosa.load(path,sr=22050,mono=True)
oenv=librosa.onset.onset_strength(y=y,sr=sr)
tempo=float(librosa.feature.tempo(onset_envelope=oenv,sr=sr)[0])
_,beats=librosa.beat.beat_track(onset_envelope=oenv,sr=sr,units="time",tightness=100)
```
Method: (1) detect beats; (2) fit a grid: median inter-beat interval `ib`, phase = median(beats mod ib), regenerate grid `t_k = phase + k*ib` (removes tracker jitter); (3) fix octave errors: if tempo <80 double it, if >160 halve it, so ib is 0.375-0.75 s; (4) choose a start offset in the song so the grid is on the first frame (trim the song; use the strongest onset in the first 1 s as the downbeat, or maximise sum of oenv at candidate shifts over bars of 4 beats); (5) set cut times to every 2nd beat (shot ~1 s at 120 BPM; ~1.3 s at 90 BPM) snapping each nominal cut to the nearest grid point within +-0.15 s, then adjust shot lengths so total = 10.0 s; (6) video cut lands 2-3 frames (0.07-0.1 s) AFTER the beat transient (human perceives picture-after-sound as synced; #21 says nudge 1-3 frames); (7) for a J-cut feel start the next beat-accented sound 6-12 frames early only if the music is edited; otherwise skip; (8) transition midpoint (not start) on the beat for dissolves/pushes: offset = beat_time - T/2; (9) hard cuts exactly on the beat. Fall back to a fixed 1.0 s grid if confidence is low (tempo outside 70-170 or fewer than 6 beats).

### B4. Ordering algorithm (greedy + local search, ~50 lines)

Metadata per frame: kind in {person, flat, folded, closeup}, view in {front, back, side, detail}, product in {hoodie, tee, polo, cap, ...}, placement in {chest, back, emblem, none}, lum (0-1 mean luminance of garment region), design_id, breed.

Hard constraints (reject candidate): same product adjacent; same kind three times in a row; same view adjacent when kind is the same; same design_id adjacent; same colour family adjacent.
Soft cost for adjacent pair (a,b) (lower is better):
```
cost(a,b) = 3.0*[a.kind==b.kind] + 2.0*[a.view==b.view] + 2.5*[a.placement==b.placement and placement!=none]
          + 1.5*[a.product==b.product(non-adjacent same product within 2)]
          + 2.0*(1 - min(1, abs(a.lum-b.lum)/0.35))        # reward light/dark alternation
          + 1.0*[same dominant hue family]
          + 0.5*|a.visual_weight - b.visual_weight|        # smooth energy except at designed accents
```
Pseudocode:
```
def order(frames):
    hero = argmax(frames, key=lambda f: f.score)           # strongest: person front, high contrast, big print, no clutter
    # slot rules:  slot0=hero (person or hero flat); slot1 must differ in kind AND product;
    # slot9 (loop frame) = frame most similar to hero in composition/colour, or hero's back view
    best=None
    for restart in range(300):                              # randomised greedy
        seq=[hero]; pool=frames-{hero}
        while pool:
            cands=[f for f in pool if hard_ok(seq,f)] or list(pool)
            cands.sort(key=lambda f: cost(seq[-1],f)+uniform(0,0.6))
            nxt=cands[0]; seq.append(nxt); pool.remove(nxt)
        seq=local_search(seq)       # 2-opt / swap on positions 1..8 keeping hero at 0, minimise total cost
        c=total(seq)+loop_cost(seq[-1],seq[0])+rhythm_penalty(seq)
        if best is None or c<best[0]: best=(c,seq)
    return best[1]
# rhythm_penalty: target pattern of kinds P O P O P O ... (person/object alternate) -> +2 per deviation;
#   exactly one "closeup" in slots 3-6 (tension), one wide/flat in slot 8 (release); at most 2 persons wearing dark adjacent.
# duration plan after ordering: heroes (slot0, closeup, slot9) 1.25 s; others 0.95-1.05 s; hard cut where cost(a,b) is low
#   (different kind and different lum already contrast), soft transition where cost is high (similar frames) or beat is calm.
# transition pick: if both lum high -> fade ; person->object -> push (direction = continue previous);
#   object->person -> smoothleft/right; closeup->wide -> zoom-through (max 1); same-kind forced -> fade 0.4;
#   at most 1 whip, 1 flash, 1 zoom-through; max 3 distinct names.
```
Why greedy + randomised restarts: exact optimum is a TSP-like NP-hard problem (#40); 10 items fit exhaustively only roughly (10! = 3.6M is actually feasible in numpy but unnecessary); greedy with restarts and swaps reaches the same cost in practice. Merge-shuffle style partitioning (#35) is a good initial seed for the "no two adjacent same product" constraint. Position-weighted diversity (#41): weight the cost of the first 3 slots 2x because first seconds matter most.

Loop-friendly last frame: pick slot 9 to share an anchor with slot 0 (same background colour or same garment silhouette position) so a fade/push from slot 9 into slot 0 looks continuous; end the reel with a 0.3 s `fade` that equals the opening frame's start (or simply end on a hard cut because the loop is a hard cut anyway; keep audio ending on a fade-out, not a stop).

## (c) 10 example sequences (frames shown as kind-view-product-placement, L=light garment, D=dark; join = transition after the frame)

Timing for all: 10.0 s total; 5 hard cuts (c), 4 soft joins as listed. Hero first, loop frame last. Soft joins have T = 0.30-0.45 s.

1. 1 person-front-hoodie-chest (D) [hero] | c | 2 flat-front-tee-chest (L) | push | 3 person-back-polo-backprint (L) | c | 4 closeup-cap-emblem (D) | smoothleft | 5 folded-hoodie-chest (L) | c | 6 person-side-tee-small emblem (D) | c | 7 flat-back-hoodie-backprint (L) | fade | 8 person-front-cap-emblem (D) | c | 9 folded-polo-emblem (L) | zoom-through | 10 person-back-hoodie-backprint (D) [loop to 1]
2. 1 person-front-tee-chest (L) [hero] | c | 2 folded-hoodie-chest (D) | smoothright | 3 person-side-cap-emblem (L) | c | 4 flat-back-tee-backprint (D) | c | 5 person-front-polo-emblem (L) | push | 6 closeup-hoodie-chest (D) | c | 7 person-back-tee-backprint (L) | fade | 8 flat-front-polo-chest (D) | c | 9 person-front-hoodie-chest (L) | fadeblack | 10 folded-cap-emblem (D) [loop]
3. 1 closeup-hoodie-chest (D) hero (pop-in) | c | 2 person-front-polo-chest (L) | push | 3 flat-back-hoodie-backprint (D... must differ product from 1/neighbour: use tee) -> flat-back-tee-backprint (D) | c | 4 person-side-hoodie-emblem (L) | smoothleft | 5 folded-tee-chest (L->D swap to keep alternation: use D) | c | 6 person-back-cap-backprint (L) | c | 7 flat-front-hoodie-chest (D) | fade | 8 person-front-tee-emblem (L) | c | 9 folded-polo-chest (D) | whip | 10 person-front-hoodie-chest (L) [loop]
4. 1 person-back-hoodie-backprint (D) hero | c | 2 flat-front-polo-emblem (L) | smoothup | 3 person-front-cap-chest (L->dark cap) (D) | c | 4 folded-tee-chest (L) | c | 5 person-side-polo-chest (D) | push | 6 flat-back-hoodie-backprint (L) | c | 7 closeup-tee-emblem (D) | fade | 8 person-front-hoodie-chest (L) | c | 9 folded-cap-emblem (D) | smoothright | 10 person-back-tee-backprint (L) [loop]
5. 1 person-front-polo-emblem (L) hero | c | 2 closeup-polo-emblem (D) match-cut on emblem position | push | 3 flat-back-tee-backprint (L) | c | 4 person-side-hoodie-chest (D) | c | 5 folded-cap-emblem (L) | smoothleft | 6 person-front-tee-chest (D) | c | 7 flat-front-hoodie-chest (L) | fade | 8 person-back-polo-backprint (D) | c | 9 folded-tee-chest (L) | flash | 10 person-front-cap-chest (D) [loop]
6. 1 person-front-hoodie-emblem (L) hero | fade | 2 folded-tee-chest (D) | c | 3 person-back-cap-backprint (D->L cap) (L) | smoothleft | 4 flat-back-polo-backprint (D) | c | 5 person-side-tee-chest (L) | c | 6 closeup-hoodie-backprint (D) | push | 7 person-front-polo-chest (L) | c | 8 folded-cap-emblem (D) | c | 9 flat-front-hoodie-chest (L) | fade | 10 person-back-tee-backprint (D) [loop]
7. 1 person-front-cap-emblem (D) hero | c | 2 flat-front-hoodie-chest (L) | smoothright | 3 person-side-polo-chest (D) | c | 4 folded-tee-emblem (L) | push | 5 person-back-hoodie-backprint (D) | c | 6 closeup-tee-chest (L) | c | 7 person-front-polo-emblem (D) | fade | 8 flat-back-cap-backprint (L) | c | 9 folded-hoodie-chest (D) | zoom-through | 10 person-front-tee-chest (L) [loop]
8. 1 person-back-tee-backprint (L) hero | c | 2 folded-hoodie-chest (D) | push | 3 person-front-polo-chest (L) | smoothup | 4 flat-back-hoodie-backprint (D) | c | 5 person-side-cap-emblem (L) | c | 6 flat-front-tee-emblem (D) | fade | 7 closeup-polo-chest (L) | c | 8 person-front-hoodie-emblem (D) | c | 9 folded-cap-emblem (L) | whip | 10 person-back-polo-backprint (D) [loop]
9. 1 person-front-hoodie-chest (L) hero | push | 2 flat-front-polo-emblem (D) | c | 3 person-side-tee-chest (L) | c | 4 folded-cap-emblem (D) | smoothleft | 5 person-back-hoodie-backprint (L) | c | 6 closeup-tee-emblem (D) | c | 7 flat-back-polo-backprint (L) | fade | 8 person-front-cap-chest (D) | c | 9 folded-hoodie-chest (L) | flash | 10 person-back-tee-backprint (D) [loop]
10. 1 closeup-polo-chest (D) hero | c | 2 person-front-tee-emblem (L) | smoothright | 3 folded-hoodie-chest (D) | c | 4 person-back-cap-backprint (L) | push | 5 flat-front-hoodie-chest (D) | c | 6 person-side-polo-emblem (L) | c | 7 flat-back-tee-backprint (D) | fade | 8 person-front-hoodie-chest (L) | c | 9 folded-cap-emblem (D) | fadeblack | 10 person-back-polo-backprint (L) [loop]

Each sequence satisfies: no two adjacent same product, person/object alternate except at 4-5 and 6-7 (deliberate double-object or double-person beats), light/dark alternate, one closeup, and a hero first. Run the checker `validate(seq)` (hard constraints above) in the pipeline and re-run the optimiser rather than hand-ordering; the 10 above are templates for the optimiser's target pattern.

## Implementation checklist
1. Pre-render each shot as its own clip (2x prescale zoompan or parallax/pop) at 30 fps, yuv420p, setsar=1.
2. Build xfade chain with the offset rule; custom transitions need gbrp on both inputs.
3. Beat grid via librosa; compute shot lengths from grid; verify sum L - sum T = 10.000.
4. Render audio separately (afade out 0.4 s), mux.
5. QA: extract frame at each join midpoint and at +-0.2 s, check no black frames (circle/rect/zoomin bans), check hold >= 0.5 s clean frame per shot.

#!/usr/bin/env python3
"""Make an Instagram 4:5 carousel (1080x1350 slides) from a built Post B reel: one still per shot, cropped to the feed-safe 4:5 window
(rows 285-1635 of the 1080x1920 frame). Slide 1 carries the breed hook, the last slide the share CTA (both are burned into the reel).
Usage: carousel_from_reel.py out/postc/c39 [n_shots=8]   -> out/postc/c39/slide01.jpg .. slideNN.jpg"""
import sys, subprocess, json
d = sys.argv[1]; n = int(sys.argv[2]) if len(sys.argv) > 2 else 8
dur = float(subprocess.check_output(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",f"{d}/reel.mp4"]))
body = dur - 0.6; seg = body / n
for i in range(n):
    t = seg * (i + 0.5) + (0.12 if i == 0 else 0) - (0.1 if i == n-1 else 0)
    subprocess.check_call(["ffmpeg","-v","error","-y","-ss",f"{t:.3f}","-i",f"{d}/reel.mp4","-frames:v","1","-vf","crop=1080:1350:0:285","-q:v","2",f"{d}/slide{i+1:02d}.jpg"])
print("slides", n, "from", d)

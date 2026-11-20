#!/usr/bin/env python3
"""LOOPIFY (owner 2026-11-20, engagement research: replays + watch-through are top ranking signals).
usage: loopify.py in.mp4 out.mp4 [dissolve=0.6]
Appends a short dissolve from the LAST frame back to the FIRST frame, so the reel loops without a visible jump on replay.
Video length grows by dissolve+0.1 s (finale hold is kept intact); audio is extended and faded out at the end. 30 fps, 1080x1920 preserved."""
import sys,subprocess,json
src,out=sys.argv[1],sys.argv[2]; T=float(sys.argv[3]) if len(sys.argv)>3 else 0.6
pr=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=width,height,r_frame_rate","-of","json",src],capture_output=True,text=True,check=True).stdout)
D=float(pr["format"]["duration"]); L=D+T+0.1
f=("[0:v]split[a][b];[a]tpad=stop_mode=clone:stop_duration=%.2f,setsar=1,fps=30,format=yuv420p[m];"
   "[b]trim=end_frame=1,setpts=PTS-STARTPTS,setsar=1,fps=30,format=yuv420p,loop=loop=%d:size=1:start=0,trim=duration=%.2f[z];"
   "[m][z]xfade=transition=fade:duration=%.2f:offset=%.3f[v];"
   "[0:a]apad=pad_dur=%.2f,atrim=0:%.3f,afade=t=out:st=%.3f:d=%.2f[au]")%(T,int(30*(T+0.2)),T+0.1,T,D,T+0.2,L,L-1.0,1.0)
subprocess.run(["ffmpeg","-y","-v","error","-i",src,"-filter_complex",f,"-map","[v]","-map","[au]","-c:v","libx264","-preset","medium","-crf","20","-c:a","aac","-b:a","160k","-movflags","+faststart",out],check=True)
print("LOOPED",out,"%.2f s -> %.2f s"%(D,L))

"""Download + clip + analyse one shard of the Mixkit index. usage: build.py SHARD NSHARDS -> out/musicbuild/s<N>/mxNNN.mp3 + catalog_<N>.json
Clip = the most energetic 45 s window (hook-friendly), 128 kbps. Analysis: bpm, energy (mean RMS dB), brightness; theme mapped from Mixkit genre/tags."""
import sys,os,json,subprocess,urllib.request,time,numpy as np
sh,n=int(sys.argv[1]),int(sys.argv[2]); idx=json.load(open("out/musiclib/index.json")); mine=[t for i,t in enumerate(idx) if i%n==sh]
od=f"out/musicbuild/s{sh}"; os.makedirs(od,exist_ok=True); H={"User-Agent":"Mozilla/5.0"}
import librosa
def theme(t):
    s=(t["genre"]+" "+" ".join(t["tags"])).lower()
    for keys,th in ((("hip hop","hip-hop","trap","rap","beats"),"Hip-hop & Trap"),(("reggae","latin","reggaeton","salsa","bossa"),"Latin & Reggae"),(("funk","disco","soul","groove","r&b"),"Funk & Disco"),
                    (("rock","guitar","metal","punk","blues","country","indie"),"Rock & Guitar"),(("house","techno","electronic","edm","dance","trance","synth","dubstep","drum"),"Electronic & House"),
                    (("lo-fi","lofi","chill","ambient","jazz","piano","acoustic","relax","sleep","meditat"),"Chill & Lo-fi"),(("pop","party"),"Pop & Party"),(("happy","upbeat","uplift","fun","feel","summer","positive","inspir"),"Feel-good"),
                    (("cinematic","classical","orchestra","epic","dramatic","horror","sad"),"Cinematic (unused)")):
        if any(k in s for k in keys): return th
    return "Feel-good"
cat=[]
for k,t in enumerate(mine):
    out=f"{od}/{t['id']}.mp3"
    try:
        raw=f"/tmp/{t['id']}.mp3"
        for a in range(3):
            try: open(raw,"wb").write(urllib.request.urlopen(urllib.request.Request(t["url"],headers=H),timeout=90).read()); break
            except Exception as e:
                if a==2: raise
                time.sleep(3)
        y,sr=librosa.load(raw,sr=22050,mono=True); dur=len(y)/sr
        on=librosa.onset.onset_strength(y=y,sr=sr); bpm=float(np.atleast_1d(librosa.feature.tempo(onset_envelope=on,sr=sr))[0])
        while bpm<70: bpm*=2
        while bpm>170: bpm/=2
        rms=librosa.feature.rms(y=y)[0]; fr=sr/512; W=int(45*fr)
        if len(rms)>W:
            cs=np.convolve(rms,np.ones(W)/W,mode="valid"); st=float(np.argmax(cs)/fr)
        else: st=0.0
        subprocess.run(["ffmpeg","-y","-v","error","-ss",f"{st:.2f}","-t","45","-i",raw,"-ac","2","-b:a","128k","-af","afade=t=in:d=0.3,afade=t=out:st=43.5:d=1.5",out],check=True)
        cen=float(np.mean(librosa.feature.spectral_centroid(y=y,sr=sr)))
        cat.append({**t,"theme":theme(t),"bpm":round(bpm,1),"energy":round(float(20*np.log10(np.mean(rms)+1e-6)),2),"bright":round(cen),"clip_start":round(st,1),"full_dur":round(dur,1),"file":f"{t['id']}.mp3","shard":sh,"license":"Mixkit Free License (commercial, no attribution)"})
        os.remove(raw)
    except Exception as e: print("ERR",t["id"],repr(e)[:100],flush=True)
    if k%25==0: print(sh,k,len(mine),flush=True)
json.dump(cat,open(f"{od}/catalog_{sh}.json","w"),indent=0); print("done",len(cat))

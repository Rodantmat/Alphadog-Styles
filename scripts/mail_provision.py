"""AlphaDog Styles own mail server on DigitalOcean (docker-mailserver), DNS on Cloudflare, outbound relayed through Resend.
MODE=provision (idempotent: server, DNS, mailboxes) | MODE=add ADDR=x@alphadogstyles.com | MODE=status
Secrets are kept encrypted in the repo (mail/*.enc, AES-256 with STORE_ADMIN_TOKEN) so later runs can manage the server.
Env: DIGITALOCEAN_TOKEN, CLOUDFLARE_API_TOKEN, RESEND_API_KEY, STORE_ADMIN_TOKEN, MAILBOXES (comma list), OWNER_EMAIL."""
import os,json,time,subprocess,secrets,string,urllib.request,urllib.error,base64
DOM="alphadogstyles.com"; HOST="mail."+DOM; NAME="mail-alphadogstyles"
DO=os.environ["DIGITALOCEAN_TOKEN"].strip(); CF=os.environ["CLOUDFLARE_API_TOKEN"].strip(); RK=os.environ["RESEND_API_KEY"].strip(); KP=os.environ["STORE_ADMIN_TOKEN"].strip()
MODE=os.environ.get("MODE","provision"); OWNER=os.environ.get("OWNER_EMAIL","rodolfoaamattos@gmail.com")
def http(base,tok,m,p,b=None):
    r=urllib.request.Request(base+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"Authorization":"Bearer "+tok,"Content-Type":"application/json"})
    try:
        x=urllib.request.urlopen(r,timeout=60).read(); return json.loads(x) if x else {}
    except urllib.error.HTTPError as e: return {"_err":e.code,"body":e.read().decode()[:400]}
do=lambda m,p,b=None: http("https://api.digitalocean.com/v2",DO,m,p,b)
cf=lambda m,p,b=None: http("https://api.cloudflare.com/client/v4",CF,m,p,b)
def enc(path,data):
    subprocess.run(["openssl","enc","-aes-256-cbc","-pbkdf2","-salt","-pass","env:KP","-out",path],input=data,check=True,env={**os.environ,"KP":KP})
def dec(path):
    return subprocess.run(["openssl","enc","-d","-aes-256-cbc","-pbkdf2","-pass","env:KP","-in",path],capture_output=True,check=True,env={**os.environ,"KP":KP}).stdout
os.makedirs("mail",exist_ok=True)
# --- SSH key (kept encrypted in repo) ---
if not os.path.exists("mail/ssh_key.enc"):
    subprocess.run(["ssh-keygen","-t","ed25519","-N","","-f","/tmp/mailkey","-C","alphadog-mail"],check=True,capture_output=True)
    enc("mail/ssh_key.enc",open("/tmp/mailkey","rb").read()); open("mail/ssh_key.pub","w").write(open("/tmp/mailkey.pub").read())
else:
    open("/tmp/mailkey","wb").write(dec("mail/ssh_key.enc")); os.chmod("/tmp/mailkey",0o600)
pub=open("mail/ssh_key.pub").read().strip()
creds=json.loads(dec("mail/creds.enc")) if os.path.exists("mail/creds.enc") else {}
def ssh(cmd,timeout=120):
    return subprocess.run(["ssh","-i","/tmp/mailkey","-o","StrictHostKeyChecking=no","-o","UserKnownHostsFile=/dev/null","-o","ConnectTimeout=10","root@"+ip,cmd],capture_output=True,text=True,timeout=timeout)
# --- droplet ---
keys=do("GET","/account/keys?per_page=200").get("ssh_keys",[])
kid=next((k["id"] for k in keys if k["public_key"].strip()==pub),None)
if not kid: kid=do("POST","/account/keys",{"name":"alphadog-mail","public_key":pub})["ssh_key"]["id"]
dr=next((d for d in do("GET","/droplets?tag_name=alphadog-mail").get("droplets",[]) if d["name"] in (NAME,HOST)),None)
if not dr and MODE=="provision":
    ud=open("mail/user_data.sh").read().replace("__RESEND_KEY__",RK)
    r=do("POST","/droplets",{"name":HOST,"region":"sfo3","size":"s-1vcpu-1gb","image":"ubuntu-24-04-x64","ssh_keys":[kid],"backups":True,"monitoring":True,"ipv6":False,"tags":["alphadog-mail"],"user_data":ud})
    if r.get("_err"): print("DROPLET CREATE FAILED",r); raise SystemExit(1)
    dr=r["droplet"]; print("droplet created",dr["id"])
if not dr: print("no mail server yet"); raise SystemExit(1)
for i in range(60):
    dr=do("GET",f"/droplets/{dr['id']}")["droplet"]; v4=[n["ip_address"] for n in dr["networks"]["v4"] if n["type"]=="public"]
    if dr["status"]=="active" and v4: ip=v4[0]; break
    time.sleep(10)
print("server",dr["id"],ip,dr["size_slug"],dr["region"]["slug"])
# --- DNS (Cloudflare) ---
zid=cf("GET","/zones?name="+DOM)["result"][0]["id"]
def recs(t,n): return cf("GET",f"/zones/{zid}/dns_records?type={t}&name={n}").get("result") or []
def upsert(t,n,content,**kw):
    ex=recs(t,n)
    body={"type":t,"name":n,"content":content,"ttl":300,"proxied":False,**kw}
    if ex:
        if ex[0]["content"]!=content or any(ex[0].get(k)!=v for k,v in kw.items()): cf("PUT",f"/zones/{zid}/dns_records/{ex[0]['id']}",body)
        for e in ex[1:]: cf("DELETE",f"/zones/{zid}/dns_records/{e['id']}")
    else: cf("POST",f"/zones/{zid}/dns_records",body)
upsert("A",HOST,ip)
for e in recs("MX",DOM):
    if e["content"].rstrip(".")!=HOST: print("removing old MX",e["content"],cf("DELETE",f"/zones/{zid}/dns_records/{e['id']}").get("success"))
if not any(e["content"].rstrip(".")==HOST for e in recs("MX",DOM)): cf("POST",f"/zones/{zid}/dns_records",{"type":"MX","name":DOM,"content":HOST,"priority":10,"ttl":300})
spf=[e for e in recs("TXT",DOM) if e["content"].strip('"').startswith("v=spf1")]
want='"v=spf1 mx include:amazonses.com ~all"'
if spf: cf("PUT",f"/zones/{zid}/dns_records/{spf[0]['id']}",{"type":"TXT","name":DOM,"content":want,"ttl":300})
else: cf("POST",f"/zones/{zid}/dns_records",{"type":"TXT","name":DOM,"content":want,"ttl":300})
if not [e for e in recs("TXT","_dmarc."+DOM)]: cf("POST",f"/zones/{zid}/dns_records",{"type":"TXT","name":"_dmarc."+DOM,"content":'"v=DMARC1; p=none; rua=mailto:support@alphadogstyles.com"',"ttl":300})
print("DNS ok")
# --- wait for the mail stack ---
for i in range(90):
    try:
        r=ssh("test -f /root/mail-ready && docker ps --format '{{.Names}} {{.Status}}'",timeout=30)
        if r.returncode==0 and "mailserver" in r.stdout: print(r.stdout.strip()); break
    except Exception as e: pass
    time.sleep(15)
else: print("MAIL STACK NOT READY"); raise SystemExit(1)
if MODE=="exec":
    r=ssh(os.environ["CMD"],timeout=600); print("EXIT",r.returncode); print(r.stdout[-4000:]); print(r.stderr[-2000:]); raise SystemExit(0)
# --- mailboxes ---
want_boxes=[x.strip() for x in os.environ.get("MAILBOXES","support,customization").split(",") if x.strip()]
if MODE=="add": want_boxes=[os.environ["ADDR"].split("@")[0]]
existing=ssh("docker exec mailserver setup email list").stdout
new=[]
for b in want_boxes:
    addr=f"{b}@{DOM}"
    if addr in existing and addr in creds: continue
    pw="".join(secrets.choice(string.ascii_letters+string.digits) for _ in range(20))
    cmd=("update" if addr in existing else "add")
    r=ssh(f"docker exec mailserver setup email {cmd} {addr} '{pw}'")
    if r.returncode!=0: print("mailbox fail",addr,r.stderr[:300]); continue
    creds[addr]=pw; new.append(addr); print("mailbox ready",addr)
time.sleep(5)
print(ssh("docker exec mailserver setup email list").stdout)
enc("mail/creds.enc",json.dumps(creds).encode())
json.dump({"droplet":dr["id"],"ip":ip,"host":HOST,"mailboxes":sorted(creds)},open("mail/state.json","w"),indent=1)
# --- send the owner the iPhone settings for new mailboxes (via the store's Resend sender) ---
if new:
    rows="".join(f"<h3>{a}</h3><p>Password: <b>{creds[a]}</b></p>" for a in new)
    html=(f"<p>Your AlphaDog Styles mailboxes are ready.</p>{rows}<p><b>iPhone:</b> Settings → Apps → Mail → Mail Accounts → Add Account → Other → Add Mail Account. "
          "Name: AlphaDog Styles, Email: the address above, Password: above, Description: e.g. AlphaDog Support → Next → choose <b>IMAP</b>.</p>"
          f"<p>Incoming mail server: Host <b>{HOST}</b>, User name: the full email address, Password: above.<br>Outgoing mail server: Host <b>{HOST}</b>, User name: the full email address, Password: above.</p>"
          "<p>If asked: IMAP port 993 with SSL; SMTP port 587 (or 465 with SSL). Save, then delete this email.</p>")
    body=json.dumps({"to":OWNER,"subject":"Your AlphaDog mailboxes: iPhone setup","html":html,"mailbox":"support"}).encode()
    req=urllib.request.Request("https://alphadogstyles.com/api/internal/send",data=body,method="POST",headers={"x-admin-token":KP,"content-type":"application/json","User-Agent":"a"})
    print("owner email:",urllib.request.urlopen(req,timeout=60).read()[:60])
print("MAIL DONE")

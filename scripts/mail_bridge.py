"""Bridge between our own mail server (IMAP/SMTP) and the store's support inbox.
sync: copy new messages from support@ / customization@ into the store (flagged $AlphaSynced; your unread state is untouched).
send: reply as the mailbox through our server (so it shows in the mailbox's Sent folder on your phone).
Credentials come from mail/creds.enc (decrypted with STORE_ADMIN_TOKEN)."""
import os,json,ssl,imaplib,smtplib,email,email.utils,subprocess,time,urllib.request,urllib.error
from email.message import EmailMessage
from email.header import decode_header,make_header
HOST="mail.alphadogstyles.com"; U="https://alphadogstyles.com"; KP=os.environ["STORE_ADMIN_TOKEN"].strip()
def creds():
    if not os.path.exists("mail/creds.enc"): return {}
    out=subprocess.run(["openssl","enc","-d","-aes-256-cbc","-pbkdf2","-pass","env:KP","-in","mail/creds.enc"],capture_output=True,env={**os.environ,"KP":KP})
    return json.loads(out.stdout) if out.returncode==0 else {}
def store(m,p,b=None):
    r=urllib.request.Request(U+p,data=json.dumps(b).encode() if b is not None else None,method=m,headers={"x-admin-token":KP,"content-type":"application/json","User-Agent":"a"})
    return json.load(urllib.request.urlopen(r,timeout=60))
def text_of(msg):
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type()=="text/plain" and "attachment" not in str(part.get("Content-Disposition","")):
                return part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8","replace")
        for part in msg.walk():
            if part.get_content_type()=="text/html":
                import re; return re.sub(r"<[^>]+>"," ",part.get_payload(decode=True).decode(part.get_content_charset() or "utf-8","replace"))
        return ""
    return msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8","replace")
def sync():
    n=0
    for addr,pw in creds().items():
        if addr.startswith("orders@"): continue   # marketplace sale notifications: handled by market_orders.py
        box="custom" if addr.startswith("customization") else "support"
        try:
            M=imaplib.IMAP4_SSL(HOST,993,ssl_context=ssl.create_default_context()); M.login(addr,pw); M.select("INBOX")
            typ,data=M.uid("search",None,"UNKEYWORD","$AlphaSynced")
            for uid in (data[0].split() if data and data[0] else [])[-50:]:
                typ,msgdata=M.uid("fetch",uid,"(BODY.PEEK[])")
                msg=email.message_from_bytes(msgdata[0][1])
                try:
                    frm=email.utils.parseaddr(msg.get("From",""))[1].lower()
                    try: subj=str(make_header(decode_header(msg.get("Subject",""))))
                    except Exception: subj=str(msg.get("Subject",""))
                    clean=lambda t: t.replace("\x00","").encode("utf-8","replace").decode("utf-8")  # Postgres TEXT rejects NUL / lone surrogates
                    store("POST","/api/internal/support",{"mailbox":box,"from":clean(frm),"subject":clean(subj+(" [msgid:"+msg.get("Message-ID","")+"]" if msg.get("Message-ID") else "")),"body":clean(text_of(msg)[:20000])})
                    M.uid("store",uid,"+FLAGS","($AlphaSynced)"); n+=1
                except urllib.error.HTTPError as e:
                    detail=e.read().decode("utf-8","replace")[:300]
                    print("sync error",addr,"uid",uid.decode(),"HTTP",e.code,detail)   # skip this one message, keep syncing the rest
                except Exception as e: print("sync error",addr,"uid",uid.decode(),type(e).__name__,str(e)[:200])
            M.logout()
        except Exception as e: print("sync error",addr,e)
    return n
def send(mailbox,to,subject,html,in_reply_to=None):
    c=creds(); addr=("customization" if mailbox=="custom" else "support")+"@alphadogstyles.com"
    if addr not in c: return False
    msg=EmailMessage(); msg["From"]=f"AlphaDog Styles <{addr}>"; msg["To"]=to; msg["Subject"]=subject; msg["Date"]=email.utils.formatdate(localtime=True); msg["Message-ID"]=email.utils.make_msgid(domain="alphadogstyles.com")
    if in_reply_to: msg["In-Reply-To"]=in_reply_to; msg["References"]=in_reply_to
    import re; msg.set_content(re.sub(r"<[^>]+>","",html.replace("<br>","\n").replace("</p>","\n\n"))); msg.add_alternative(html,subtype="html")
    with smtplib.SMTP(HOST,587,timeout=60) as s:
        s.starttls(context=ssl.create_default_context()); s.login(addr,c[addr]); s.send_message(msg)
    M=imaplib.IMAP4_SSL(HOST,993); M.login(addr,c[addr])
    for folder in ("Sent","INBOX.Sent"):
        try:
            if M.append(folder,"\\Seen",imaplib.Time2Internaldate(time.time()),msg.as_bytes())[0]=="OK": break
        except Exception: pass
    M.logout(); return True
if __name__=="__main__":
    import sys
    if sys.argv[1]=="sync": print("synced",sync())

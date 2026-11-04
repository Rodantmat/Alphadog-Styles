"""READ-ONLY: list sender+subject (no bodies, no addresses of buyers) of marketplace emails in the seller Gmail, to learn the TikTok Shop order-email format."""
import os,imaplib,ssl,email,datetime
from email.header import decode_header,make_header
pw=os.environ["FLIPPING_GMAIL_APP_PASSWORD"].replace(" ","").strip()
M=imaplib.IMAP4_SSL("imap.gmail.com",993,ssl_context=ssl.create_default_context()); M.login("flippingmagic.sales@gmail.com",pw); M.select("INBOX",readonly=True)
since=(datetime.date.today()-datetime.timedelta(days=45)).strftime("%d-%b-%Y")
for who in ("tiktok","tiktokshop","ebay","etsy"):
    typ,d=M.search(None,f'(SINCE {since} FROM "{who}")'); ids=d[0].split() if d and d[0] else []
    print(f"== from {who}: {len(ids)} emails")
    seen={}
    for n in ids[-400:]:
        h=email.message_from_bytes(M.fetch(n,"(BODY.PEEK[HEADER.FIELDS (FROM SUBJECT)])")[1][0][1])
        subj=str(make_header(decode_header(h.get("Subject",""))))[:90]; frm=email.utils.parseaddr(h.get("From",""))[1]
        key=(frm,subj[:40]); seen[key]=seen.get(key,0)+1
    for (frm,sj),c in sorted(seen.items(),key=lambda x:-x[1])[:25]: print(f"  {c:3d} x {frm} | {sj}")
M.logout()

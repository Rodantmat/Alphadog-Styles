import os,imaplib,ssl,email,re,datetime,html
from email.header import decode_header,make_header
pw=os.environ["FLIPPING_GMAIL_APP_PASSWORD"].replace(" ","").strip()
M=imaplib.IMAP4_SSL("imap.gmail.com",993,ssl_context=ssl.create_default_context()); M.login("flippingmagic.sales@gmail.com",pw); M.select("INBOX",readonly=True)
since=(datetime.date.today()-datetime.timedelta(days=45)).strftime("%d-%b-%Y")
typ,d=M.search(None,f'(SINCE {since} FROM "sellersupport@shop.tiktok.com")')
for n in d[0].split():
    m=email.message_from_bytes(M.fetch(n,"(BODY.PEEK[])")[1][0][1]); s=str(make_header(decode_header(m.get("Subject",""))))
    if not re.search(r"Action Required|Rejected|Settlement Tier|Product Listing|First Sale",s): continue
    t=""
    for p in m.walk():
        if p.get_content_type() in("text/plain","text/html"):
            b=p.get_payload(decode=True).decode(p.get_content_charset() or "utf8","ignore"); t=re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>"," ",b))); 
            if p.get_content_type()=="text/plain": break
    print("##",s[:100],"|",m.get("Date"),"\n",t[:700],"\n")
M.logout()

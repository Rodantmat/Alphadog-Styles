#!/bin/bash
# AlphaDog Styles mail server bootstrap (docker-mailserver). Placeholders __RESEND_KEY__ replaced at provision time.
set -e
export DEBIAN_FRONTEND=noninteractive
apt-get update -y && apt-get install -y ca-certificates curl gnupg ufw unattended-upgrades certbot
curl -fsSL https://get.docker.com | sh
ufw default deny incoming; ufw default allow outgoing
for p in 22 25 80 143 465 587 993; do ufw allow $p/tcp; done; ufw --force enable
mkdir -p /opt/mail && cd /opt/mail
# TLS certificate for mail.alphadogstyles.com (DNS A record is created before boot finishes; retry until it resolves)
for i in $(seq 1 30); do certbot certonly --standalone --non-interactive --agree-tos -m support@alphadogstyles.com -d mail.alphadogstyles.com && break; sleep 20; done
cat > compose.yaml <<'YML'
services:
  mailserver:
    image: ghcr.io/docker-mailserver/docker-mailserver:15
    container_name: mailserver
    hostname: mail.alphadogstyles.com
    ports: ["25:25","143:143","465:465","587:587","993:993"]
    volumes:
      - ./dms/mail-data/:/var/mail/
      - ./dms/mail-state/:/var/mail-state/
      - ./dms/mail-logs/:/var/log/mail/
      - ./dms/config/:/tmp/docker-mailserver/
      - /etc/letsencrypt:/etc/letsencrypt:ro
      - /etc/localtime:/etc/localtime:ro
    environment:
      - SSL_TYPE=letsencrypt
      - ENABLE_RSPAMD=1
      - ENABLE_OPENDKIM=0
      - ENABLE_OPENDMARC=0
      - ENABLE_POLICYD_SPF=0
      - ENABLE_AMAVIS=0
      - ENABLE_SPAMASSASSIN=0
      - ENABLE_CLAMAV=0
      - ENABLE_FAIL2BAN=1
      - ENABLE_MANAGESIEVE=1
      - POSTMASTER_ADDRESS=support@alphadogstyles.com
      - DEFAULT_RELAY_HOST=[smtp.resend.com]:587
      - RELAY_USER=resend
      - RELAY_PASSWORD=__RESEND_KEY__
      - SPOOF_PROTECTION=1
      - ONE_DIR=1
      - PERMIT_DOCKER=none
      - TZ=America/Los_Angeles
    cap_add: ["NET_ADMIN"]
    restart: always
YML
docker compose up -d
# renew certs monthly and reload
echo '17 3 * * * root certbot renew --quiet --pre-hook "docker stop mailserver" --post-hook "docker start mailserver"' > /etc/cron.d/certbot-mail
# nightly backup of mail data (kept 7 days on disk; DigitalOcean weekly droplet backups also on)
echo '41 2 * * * root tar czf /opt/mail/backup-$(date +\%u).tgz -C /opt/mail dms' > /etc/cron.d/mail-backup
touch /root/mail-ready

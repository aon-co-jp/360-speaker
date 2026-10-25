#!/bin/sh
# VPSで毎朝クローラーを動かす(systemdタイマー 05:30)。 /root/easy-web.tokyo/360-speaker で実行。
set -e
cd /root/easy-web.tokyo/360-speaker
(cd crawler && cargo build --release)
cat > /etc/systemd/system/360-speaker-crawl.service <<'EOF'
[Unit]
Description=360-speaker diaphragm-material candidate crawler (arXiv + Crossref)
After=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/root/easy-web.tokyo/360-speaker
ExecStart=/root/easy-web.tokyo/360-speaker/crawler/target/release/materials-crawler /root/easy-web.tokyo/360-speaker/web/data/materials-candidates.json
EOF
cat > /etc/systemd/system/360-speaker-crawl.timer <<'EOF'
[Unit]
Description=Daily run of the 360-speaker materials crawler

[Timer]
OnCalendar=*-*-* 05:30:00
Persistent=true

[Install]
WantedBy=timers.target
EOF
systemctl daemon-reload
systemctl enable --now 360-speaker-crawl.timer
systemctl start 360-speaker-crawl.service
systemctl list-timers 360-speaker-crawl.timer --no-pager | head -3

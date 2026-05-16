#!/bin/bash
cd /root/happy-dance/backend
/root/happy-dance/backend/.venv/bin/python crawler.py >> /var/log/happy-dance-crawler.log 2>&1
if [ $? -ne 0 ]; then
    /root/happy-dance/backend/.venv/bin/python /root/happy-dance/backend/send_alert.py "$(date '+%Y-%m-%d %H:%M:%S')"
fi

#!/usr/bin/env sh
# Daily database backup. Add to crontab:  0 3 * * * /root/salum-tracker/backup.sh
set -eu
cd "$(dirname "$0")"
mkdir -p backups
docker compose -p "${STACK:-salum-tracker}" exec -T db pg_dump -U salum salum | gzip > "backups/salum-$(date +%F).sql.gz"
find backups -name 'salum-*.sql.gz' -mtime +30 -delete

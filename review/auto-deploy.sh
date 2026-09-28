#!/usr/bin/env bash
# Cron entry point: run deploy.sh only when GitHub has new commits.
# Crontab line (every 10 min, flock stops overlapping runs):
#   */10 * * * * flock -n /tmp/peacerep-deploy.lock bash ~/<repo>/review/auto-deploy.sh >> ~/deploy.log 2>&1
set -euo pipefail
cd "$(dirname "$0")"

git fetch --quiet
if [ "$(git rev-parse HEAD)" != "$(git rev-parse '@{u}')" ]; then
  echo "=== $(date -Is) new commits, deploying"
  ./deploy.sh
fi

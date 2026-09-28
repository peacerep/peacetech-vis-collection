#!/usr/bin/env bash
# Build the review app and publish it to nginx. Run on the VM from anywhere:
#   ~/<repo>/review/deploy.sh
# Metadata is baked into the bundle at build time, so re-run after every pull.
set -euo pipefail

WEB_ROOT="${WEB_ROOT:-/var/www/html}"
cd "$(dirname "$0")"

git pull --ff-only
npm ci
npm run build
sudo rsync -a --delete dist/ "$WEB_ROOT/"

echo "Deployed to $WEB_ROOT"

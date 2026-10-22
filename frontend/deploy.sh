#!/usr/bin/env bash
# Build the frontend and publish it to the nginx web root.
# Usage: ./deploy.sh   (run from anywhere; the web root is owned by ws, so no sudo is needed)
set -euo pipefail

cd "$(dirname "$0")"
WEB_ROOT=${WEB_ROOT:-/var/www/html}
BACKUP=${BACKUP_DIR:-$HOME/backups/www-html-original}   # one-time copy of whatever was there before LaunchWise

[ -d node_modules ] || npm ci
npm run build

if [ ! -d "$BACKUP" ]; then
  mkdir -p "$(dirname "$BACKUP")"
  cp -a "$WEB_ROOT" "$BACKUP"
  echo "Backed up the original web root to $BACKUP"
fi

# --delete removes files from older builds (and the old placeholder) so only the new build is served.
rsync -a --delete dist/ "$WEB_ROOT/"
echo "Deployed $(ls dist/assets | wc -l) asset files to $WEB_ROOT"

#!/usr/bin/env bash
set -euo pipefail

export PATH="/home/joy/.local/bin:${PATH}"
cd /mnt/d/dev/Worldline/web
exec ./node_modules/.bin/vite --host 0.0.0.0 --port 5173

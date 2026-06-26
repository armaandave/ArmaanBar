#!/bin/bash
set -euo pipefail

# Simple script to launch ArmaanBar (kills existing local instance first)
# Usage: ./Scripts/launch.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
APP_PATH="$PROJECT_ROOT/ArmaanBar.app"

echo "==> Killing existing ArmaanBar instances"
pkill -x ArmaanBar || pkill -f ArmaanBar.app || true
sleep 0.5

if [[ ! -d "$APP_PATH" ]]; then
    echo "ERROR: ArmaanBar.app not found at $APP_PATH"
    echo "Run ./Scripts/package_app.sh first to build the app"
    exit 1
fi

echo "==> Launching ArmaanBar from $APP_PATH"
open -n "$APP_PATH"

# Wait a moment and check if it's running
sleep 1
if pgrep -x ArmaanBar > /dev/null; then
    echo "OK: ArmaanBar is running."
else
    echo "ERROR: App exited immediately. Check crash logs in Console.app (User Reports)."
    exit 1
fi

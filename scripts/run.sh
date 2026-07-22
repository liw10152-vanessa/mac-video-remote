#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")/.."
if [[ ! -x build/remote-helper ]]; then
  ./scripts/build.sh
fi
exec /usr/bin/python3 app.py "$@"

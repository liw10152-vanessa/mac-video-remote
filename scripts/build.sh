#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p build
clang -fobjc-arc native/remote_helper.m -o build/remote-helper \
  -framework AppKit -framework ApplicationServices -framework Foundation
echo "已生成 build/remote-helper"

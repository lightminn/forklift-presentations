#!/usr/bin/env bash
set -euo pipefail
deck_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
port="${1:-8765}"
if [[ ! "$port" =~ ^[0-9]+$ ]] || (( port < 1024 || port > 65535 )); then
  echo '포트는 1024–65535 사이의 정수여야 합니다.' >&2
  exit 2
fi
python_bin="${PYTHON:-python3}"
echo "주차별 발표 목록: http://127.0.0.1:${port}/"
echo "최근 발표자료: http://127.0.0.1:${port}/latest/"
echo '종료: Ctrl+C'
exec "$python_bin" -m http.server "$port" --bind 127.0.0.1 --directory "$deck_dir"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if [[ ! -d _deps ]]; then
  python3 -m pip install --target ./_deps -r requirements.txt
fi
export PYTHONPATH="_deps:."
python3 -m pytest -q "$@"

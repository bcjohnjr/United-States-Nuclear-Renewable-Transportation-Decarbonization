#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 us914_validate.py --full

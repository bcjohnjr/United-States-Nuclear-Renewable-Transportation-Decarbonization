#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 us9141_repo_check.py
python3 us914_validate.py --full

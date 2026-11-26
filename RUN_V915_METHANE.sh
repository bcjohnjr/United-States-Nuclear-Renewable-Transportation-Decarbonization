#!/bin/sh
set -eu
cd "$(dirname "$0")"
python3 us915_methane.py > us915_validation.txt
python3 us915_figures.py

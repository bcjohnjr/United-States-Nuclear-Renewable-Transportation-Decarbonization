#!/bin/sh
set -eu
cd "$(dirname "$0")"
sh RUN_V917.sh
python us918_evidence.py
python us918_figures.py
python us918_validate.py

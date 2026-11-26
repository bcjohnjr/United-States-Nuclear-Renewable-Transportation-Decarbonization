#!/bin/sh
set -eu
cd "$(dirname "$0")"
python us917_validate.py --inputs-only
python us915_methane.py
python us916_coupled.py
python us917_evidence.py
python us917_figures.py
python us917_validate.py

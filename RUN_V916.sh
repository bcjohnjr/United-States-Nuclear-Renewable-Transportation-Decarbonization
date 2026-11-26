#!/bin/sh
set -eu
cd "$(dirname "$0")"
python us915_methane.py
python us916_coupled.py
python us916_figures.py
python us916_validate.py

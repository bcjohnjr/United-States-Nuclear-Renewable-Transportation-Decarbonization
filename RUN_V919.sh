#!/bin/sh
set -eu
cd "$(dirname "$0")"
python us919_sweetspot.py
python us919_figures.py
python us919_map_reproduce.py
python us919_validate.py

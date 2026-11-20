#!/usr/bin/env bash
# Run the v8.3 U.S. transport model: transport LP and Monte Carlo, gas depletion, fuel transition, nutrient balance, community screen, petroleum break-even, tests and figures.
# Flat layout: everything is read from and written to this folder.
# Usage: bash run_all.sh [monte_carlo_draws] [--no-figures]   (default 1000 draws, figures on)
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1   # keep the folder flat (no __pycache__)
cd "$(dirname "$0")"
N="${1:-1000}"
FIGS=1
for a in "$@"; do [ "$a" = "--no-figures" ] && FIGS=0; done
[[ "$N" =~ ^[0-9]+$ ]] || N=1000
python3 us2_model.py "$N" | tee run_log.txt
python3 us2_gas_extension.py > /dev/null
python3 us5_fuel_transition.py "$FIGS" > v5_transition_run_log.txt
python3 us5_test.py
if [ "$FIGS" = "1" ]; then
  python3 us6_nutrient_balance.py "$N" | tee v6_nutrient_run_log.txt
else
  python3 us6_nutrient_balance.py "$N" --no-figures | tee v6_nutrient_run_log.txt
fi
python3 us6_test.py
if [ "$FIGS" = "1" ]; then
  python3 us7_community_screen.py | tee v7_community_run_log.txt
else
  python3 us7_community_screen.py > v7_community_run_log.txt
fi
python3 us7_test.py
python3 us8_petroleum_breakeven.py
if [ "$FIGS" = "1" ]; then
  python3 us2_figures.py
  python3 us2_science_figs.py
  python3 us2_poster_map.py
  python3 us7_publication_map.py
fi
echo "Done: v8.3 model run, tests and figures in $(pwd)"

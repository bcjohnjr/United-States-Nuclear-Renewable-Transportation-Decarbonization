# U.S. transport decarbonization and agricultural methane mitigation — V9.19

This release is a **delta overlay on V9.18** (public base commit `68e89a5b87788d2bd529cd2f8caf14a571b7891e`). Keep all existing root-level code, data and source illustrations. Extract the V9.19 update ZIP directly into the same root; no nested directory is needed. Do not upload the editorial manuscript archive. Use Python with the dependency versions in the existing `requirements-v918.txt`.

```
python -m pip install -r requirements-v918.txt
```

Windows: `RUN_V919.bat`. Linux/macOS: `sh RUN_V919.sh`. The older `RUN_V918.sh` / `.bat` remain available to regenerate the reference foundation; V9.19 reads the existing published V9.18 evidence results and independently reconstructs its central input parameters, then reruns the optimization. No network access or API key is required after dependencies are installed. Exact byte hashes are tested in the pinned environment; cross-platform figure rendering can differ with fonts or system libraries.

## Results and interpretation

The full-crop target costs $445.45 billion/year in 2050 and avoids 3.061 Gt CO2e/year vs continued petroleum. Four inherited petroleum-price cases cost $475.03–1,007.70 billion/year. Stronger cost endpoints yield $383.27 billion/year. These are conditional results using inherited low cost bounds, not forecasts. The target is more expensive than the BEV-cost-matched AEO2026 comparator. Joint uncertainty and fixed-service transition screens do not establish a physical construction schedule or universal annual savings. An accelerated readiness gate illustrates the conditions required for a no-overspend annualized pathway.

`V919_COST_ASSUMPTIONS.md` explains the assumptions. `US919_Results.json` and `us919_*.csv` contain the results. `V919_FIGURE_CROSSWALK.csv` identifies all 26 submitted visuals, including six updated maps whose original geometry is preserved by exact image patches. `V919_OUTPUT_SHA256.csv` covers generated outputs; `V919_DELTA_SHA256.csv` covers update files other than itself. No prior source files are deleted. New figures carry the `V919_` prefix.

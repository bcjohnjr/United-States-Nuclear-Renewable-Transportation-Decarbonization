# V9.14.1 — Science-targeted U.S. transport decarbonisation editorial and GitHub-flat correction

**Status:** V9.14 numerical model preserved; V9.14.1 corrects declarations and version references, figure provenance, Figure S30 display precision and repository checks. All named authors have read and approved the final manuscript and its submission, as confirmed by the corresponding author. The corresponding author confirms no external funding and the contact email jonathan@cloudwashlaundry.com. The authors declare no competing interests, with the Cloud Wash Laundry Corporation association disclosed. **Not yet certified as ready to submit** pending precise coauthor contribution records, figure permission and publication of an exact repository release. All numerical resource quantities are **conditional scenario screens**, not verified regional supply or full lifecycle measurements.

## Flat-directory reproduction (no project tree, no Git checkout required)

1. Extract **every file** from this ZIP into **the same directory** (do not put files in `src/`, `data/`, or other subdirectories). The AEO workbook collection and historical Word inputs remain in flat ZIP files in that directory.
2. Install Python 3.11+ and dependencies: `python -m pip install -r requirements-v914.txt` (on Windows, `py -3 -m pip install -r requirements-v914.txt` also works).
3. Windows quick integrity check: double-click `RUN_V914_QUICK_CHECK.bat` or run `py -3 us914_validate.py`.
4. **Windows full independent rerun:** double-click `RUN_V914_REPRODUCE.bat` (or `py -3 us914_validate.py --full`). Linux/macOS: `bash RUN_V914_REPRODUCE.sh`.

`--full` first verifies the SHA-256-checksum-audited package, then copies all flat-root source data into a temporary *flat* directory, and re-executes the crop/soil screens, paired 1,000-draw Monte Carlo, TIFF figures and current Word files there. The output ZIP and manifest are never modified by the test. V9.14.1 adds a GitHub-flat checkout preflight and regenerates all four editorial Word files during the isolated test. On a matching Python/SciPy solver environment, the two current Monte Carlo outputs must match byte for byte. On other solver versions, numerical feasibility may reproduce without binary-identical CSV; failure will be reported rather than silently passed.

## Journal files

`SCIENCE_EDITORIAL_UPLOAD_ONLY_V9.14.zip` contains exactly four current Word documents (article, supplement, cover letter, title page) and 35 RGB TIFF figure files at 600 dpi. Extract this **inner ZIP** when assembling the eventual journal submission. Do not send the complete research ZIP to the editor in place of upload-specific materials. The publisher's current policy and required upload fields must be reviewed prior to submission.

Grid Harvester Figs. S1 and S22 are required components and remain source-matched. Under one engineering case, modeled cycle energy is 33.9 versus 90.9 MJ per 1.44-ha harvesting cycle (62.7% less energy)—**not** a field measurement or a fuel-production-efficiency improvement.

## V9.14 substantive corrections

- Abstract reports **59.8% zero selected agricultural residues** in the current 1,000 uncalibrated screening draws, and clearly distinguishes economic conditions from verified national implementation.
- Explicit route-factor consistency audit: the base model applies **10 g CO₂e/MJ** to the **combined** terrestrial crop/grass fuel route. Of 1,173.878 TWh on that route in the illustrative solution, 431.6 TWh is crop-derived. The generic crop portion is **15.5376 Mt CO₂e/year**, before conditional replacement by explicit agricultural process inventory. Noncrop fuel, process hydrogen and electric lifecycle emissions are not removed.
- Hypothetical sampling of the 7–13 g/MJ coefficient now first adjusts the inherited model emissions before removing the *same* crop-route coefficient; a mere parameter redraw cannot fabricate an emissions reduction. The invariant is enforced by `us914_validate.py`.
- The +$20/$40/$80 per dry metric tonne delivery stress refers to **additional crop-only delivery costs above assumed baseline delivered-tier screening prices**, *not* total farmgate/road/processing/nutrient charges or verified BT23 delivered county bids.
- The integrated paper, source-level code, supplement **S32 route-factor/units audit**, current uncertainty outputs and reproducible figures were updated together. The editorial ZIP was rebuilt and checked against its loose source files.

## Explicit scientific and ethical limitations

The 166-Mt/y national crop capacity and 13 individual capacities, field collection eligibility, plant-available nutrient fractions, crop-specific HTL liquid yields, net field CO₂e effects and soil-carbon persistence have not been regionally or experimentally verified. The source AEO2026 reference covers only a **partial** cost and lifecycle boundary. This is **not** a claimed national cost saving relative to the official EIA reference. County-level BT23 portal exports were not supplied or silently invented. Year-round grid/dispatch feasibility and final reactor build schedules are outside this screen. Do not call the analysis a certified cradle-to-grave LCA.

## Author and release tasks still open

See `AUTHOR_CLEARANCE_PENDING_V9.14.md`, `SCIENCE_POLICY_AUTHOR_REVIEW_V9.14.md`, `US914_EDITORIAL_FIGURE_PROVENANCE.csv`, and `GITHUB_RELEASE_NOTES_V9.14.md`. Author approval, no external funding, contact email and the no-competing-interests declaration have been entered in the Word documents from the corresponding author’s confirmations. Precise CRediT roles of the other authors, any relevant IP/financial relationships requiring additional disclosure, and figure permissions must still be checked against journal requirements. **Do not invent** repository tags, archived DOI values, prompt histories, figure provenance or Science editorial permissions. Only insert GitHub/Zenodo links after user verification and publication of the exact V9.14 research files.

## V9.14.1 GitHub-ready regression (code and datasets remain at repository root)

Run `RUN_V9141_REPOSITORY_CHECK.bat` on Windows or `bash RUN_V9141_REPOSITORY_CHECK.sh` on Linux/macOS. This verifies every root Python file parses, checksum-manifest completeness, original V9.13 output preservation, 35 editorial figure matches and an isolated full reproduction. `GITHUB_ACTIONS_US_TRANSPORT_V9141.yml` is a workflow template; **copy it into `.github/workflows/us-transport-v9141.yml`** to activate GitHub Actions. That `.github/workflows/` directory is GitHub configuration, not a dependency of the flat root Python code.

The GitHub account connector did not expose the target U.S. transport repository during package preparation; this ZIP has been tested as a fresh flat-root checkout simulation, **not claimed to have passed live GitHub Actions**. Confirm a successful Actions run from the exact final commit before citing the repository.

Historical V9.13-named uncertainty outputs were recalculated in V9.14. The original V9.13 CSV and JSON are retained at the flat root with `V913_ORIGINAL__` prefixes; `V913_V914_CORRECTED_LEGACY_AUDIT.csv` lists all seven identical-name files that changed between official V9.13 and V9.14 archives with both hashes. File names carried forward from an older code interface are not, by themselves, proof of old numbers. The scientific calculations remain V9.14.

The checksum CSV is **not digitally signed**. `MAKE_MANIFEST_V9141.py` is provided only for intentional audited edits, not as a substitute for integrity verification. All supplied single files are below GitHub's 100 MB limit. Source archives and large copyrighted third-party datasets must be checked for redistribution permission before repository publication.

## V9.14.1 author-declaration delta (25 November 2026)

The manuscript, cover letter and title page now state that all named authors have reviewed and approved submission; no external funding was received; and the corresponding-author contact is **jonathan@cloudwashlaundry.com**. The numerical model, Monte Carlo results, figures and supplementary methods are unchanged. The regeneration script `us9141_finalize.py`, repository preflight and full validator enforce the same assertions. The revised editor-only ZIP includes all four current documents and 35 unchanged figure TIFFs. CRediT details not supplied by the authors are **not invented**. The separate release patch contains only files that differ from the preceding V9.14.1 research archive, together with the updated SHA-256 manifest.

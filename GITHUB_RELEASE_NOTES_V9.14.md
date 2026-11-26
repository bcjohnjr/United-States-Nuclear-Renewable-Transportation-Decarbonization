# V9.14.1 — user-managed GitHub/archival release

Extract the complete **outer ZIP**, without adding extra source/data subdirectories, into the intended repository root. Upload all flat-root Python scripts, version-specific `.csv`/`.json` data, 600-dpi TIFFs, both embedded input archives and required source document archives. Git and GitHub do not require the scripts to live in a nested directory.

On Windows:

```
py -3 -m pip install -r requirements-v914.txt
RUN_V914_QUICK_CHECK.bat
RUN_V914_REPRODUCE.bat
```

On Linux/macOS:

```
python3 -m pip install -r requirements-v914.txt
bash RUN_V914_REPRODUCE.sh
```

After all checks pass, create a fixed V9.14 tag, verify every declared source file hash, and archive the version in a DOI issuing repository such as Zenodo. **Do not paste a guessed DOI or commit ID** into the manuscript. Confirm third-party AEO source-workbook distribution rights and AI/figure permissions before making the archive public.

Publication of the exact repository release remains the user's task; none of the builder tools pushes code to GitHub, creates a tag or books a DOI.

## Clean GitHub checkout procedure

**Code and data remain flat:** copy all files from the outer research ZIP to the repository root. Place the optional `GITHUB_ACTIONS_US_TRANSPORT_V9141.yml` template at `.github/workflows/us-transport-v9141.yml` if automated CI is desired. On the target branch, run `python us9141_repo_check.py` and `python us914_validate.py --full`; on Windows use `RUN_V9141_REPOSITORY_CHECK.bat`. Do not publish an unverified tag or DOI. For this V9.14.1 editorial release, the numerical model retains the name V9.14; only documentation and figure S30 display precision changed.

Do not add the outer archive itself to a GitHub checkout that is being validated with its own manifest. Do not move required Python/data/Word files to `src/`, `data/` or `docs/` without rewriting source paths.

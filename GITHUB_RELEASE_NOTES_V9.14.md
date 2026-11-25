# V9.14 — user-managed GitHub/archival release

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

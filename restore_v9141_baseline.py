"""Restore the original manifested V9.14.1 files in a separate directory."""
from pathlib import Path
import csv,hashlib,sys,zipfile,shutil
root=Path(__file__).resolve().parent
out=Path(sys.argv[1]).resolve()
if out==root or (out.exists() and any(out.iterdir())): raise SystemExit('Choose a new empty directory outside active V9.15 files.')
out.mkdir(parents=True,exist_ok=True)
with zipfile.ZipFile(root/'ARCHIVED_V9141_REPLACED_ARTIFACTS.zip') as old:
    for row in csv.DictReader((root/'MANIFEST_V9.14_SHA256.csv').open()):
        n=row['filename']; data=old.read(n) if n in old.namelist() else (root/n).read_bytes()
        if hashlib.sha256(data).hexdigest()!=row['sha256']: raise ValueError('Original hash mismatch: '+n)
        (out/n).write_bytes(data)
for n in ['MANIFEST_V9.14_SHA256.csv','MAKE_MANIFEST_V9141.py','RUN_V9141_REPOSITORY_CHECK.bat','RUN_V9141_REPOSITORY_CHECK.sh','V9141_README_FIRST.txt','us9141_repo_check.py']:
    if (root/n).exists() and not (out/n).exists(): shutil.copy2(root/n,out/n)
print('PASS: original manifested V9.14.1 files restored and hash-verified.')

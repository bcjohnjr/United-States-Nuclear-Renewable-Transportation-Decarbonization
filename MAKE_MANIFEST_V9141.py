#!/usr/bin/env python3
"""Rebuild flat-root SHA-256 manifest for a deliberately edited new release.
Do NOT run merely to make a broken validation pass; first review diffs.
"""
from pathlib import Path
from hashlib import sha256
import csv
ROOT=Path(__file__).resolve().parent
m=ROOT/'MANIFEST_V9.14_SHA256.csv'
files=sorted(p for p in ROOT.iterdir() if p.is_file() and p!=m)
with m.open('w',newline='',encoding='utf-8') as out:
    w=csv.writer(out); w.writerow(['filename','sha256','size_bytes'])
    for p in files:w.writerow([p.name,sha256(p.read_bytes()).hexdigest(),p.stat().st_size])
print('UPDATED CHECKSUM MANIFEST',len(files),'flat-root files (unsigned SHA-256)',flush=True)

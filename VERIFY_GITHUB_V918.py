"""Verify published flat V9.18 release against local release Git blob manifest.
Public read-only GitHub API; no credentials needed for public repo. Optional
GITHUB_TOKEN environment variable for rate limits. This is NOT required to run
scientific model offline. Run before publishing a commit link in the article.
"""
from pathlib import Path
import csv,json,os,sys,urllib.request,urllib.parse,hashlib
P=Path(__file__).resolve().parent
REPO='bcjohnjr/United-States-Nuclear-Renewable-Transportation-Decarbonization'
def get(url):
 headers={'Accept':'application/vnd.github+json','User-Agent':'V918-flat-release-verifier'}
 if os.environ.get('GITHUB_TOKEN'):headers['Authorization']='Bearer '+os.environ['GITHUB_TOKEN']
 with urllib.request.urlopen(urllib.request.Request(url,headers=headers),timeout=60) as r:return json.load(r)
def main():
 ref=sys.argv[1] if len(sys.argv)>1 else 'main'; base='https://api.github.com/repos/'+REPO
 commit=get(base+'/commits/'+urllib.parse.quote(ref,safe=''));sha=commit['sha']; tree=get(base+'/git/trees/'+commit['commit']['tree']['sha'])
 if tree.get('truncated'):raise RuntimeError('GitHub truncated root tree; cannot certify')
 remote={x['path']:x for x in tree['tree'] if x['type']=='blob'}
 rows=list(csv.DictReader((P/'V918_GIT_BLOBS.csv').open(encoding='utf-8')))
 mismatches=[]
 for r in rows:
  x=remote.get(r['filename']);
  if not x or x['sha']!=r['git_blob_sha1']:mismatches.append((r['filename'],'missing' if not x else 'different bytes'))
 if mismatches:
  for x in mismatches:print(*x,sep=': ')
  print(f'FAIL: {len(mismatches)}/{len(rows)} expected root files differ or missing at {sha}');return 1
 print(f'PASS: {len(rows)} release files match GitHub root blobs at commit {sha}')
 print('Pinned release URL: https://github.com/'+REPO+'/tree/'+sha)
 print('Run RUN_V918 in an independently cloned checkout to verify numerical execution.')
 return 0
if __name__=='__main__':sys.exit(main())

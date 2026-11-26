"""Replay exact, non-generative annotation patches on unchanged V9.18 artwork."""
from pathlib import Path
import hashlib,io,json,zipfile
from PIL import Image
P=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with zipfile.ZipFile(P/'V919_MAP_PATCHES.zip') as z:
 for r in json.loads(z.read('patches.json')):
  source=P/r['source']; assert sha(source)==r['source_sha256'], source
  with Image.open(source) as original: im=original.convert('RGB')
  with Image.open(io.BytesIO(z.read(r['patch']))) as patch: im.paste(patch,tuple(r['xy']),patch.getchannel('A'))
  assert hashlib.sha256(im.tobytes()).hexdigest()==r['rgb_sha256'],r['output']
  target=P/r['output']; kwargs={'compression':'tiff_lzw'} if target.suffix=='.tif' else {}
  if r['dpi']: kwargs['dpi']=tuple(r['dpi'])
  im.save(target,**kwargs)
  print('Map pixels verified:',target.name)

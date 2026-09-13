"""Fallback for ComfyUI versions without automatic model placement."""
import argparse,hashlib,json,os,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--comfyui',required=True,type=Path);p.add_argument('--check-only',action='store_true');a=p.parse_args()
if not (a.comfyui.expanduser().resolve()/'main.py').is_file():raise SystemExit('Not a ComfyUI directory')
base=(a.comfyui.expanduser().resolve()/'models/yue2');base.mkdir(parents=True,exist_ok=True)
def digest(path):
    value=hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda:f.read(8*1024*1024),b''):value.update(block)
    return value.hexdigest()
for item in json.loads((ROOT/'models.json').read_text()):
    target=base/item['name']
    if not target.resolve().is_relative_to(base.resolve()) and not target.is_symlink():raise SystemExit('Invalid destination')
    if target.exists():
        if target.stat().st_size==item['size'] and digest(target)==item['sha256']:print('OK',item['name'],flush=True);continue
        raise SystemExit('Existing model differs; no overwrite: '+str(target))
    if a.check_only:raise SystemExit('Missing: '+str(target))
    target.parent.mkdir(parents=True,exist_ok=True);part=target.with_name(target.name+'.part')
    if part.exists():raise SystemExit('Partial file exists; inspect before retry: '+str(part))
    print('Downloading',item['name'],flush=True)
    try:
        with urllib.request.urlopen(item['url'],timeout=120) as source,part.open('xb') as out:
            while block:=source.read(8*1024*1024):out.write(block)
        if part.stat().st_size!=item['size'] or digest(part)!=item['sha256']:raise RuntimeError('Downloaded model integrity mismatch')
        os.replace(part,target)
    except Exception:
        print('Download failed; partial file retained:',part);raise
print('All YuE2 files verified.')

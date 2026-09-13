"""Check the exact package file set and every SHA256, excluding only this manifest."""
import hashlib,json
from pathlib import Path

def verify(root):
    root=Path(root).resolve()
    manifest=json.loads((root/'SHA256SUMS.json').read_text())
    if not isinstance(manifest,dict):raise ValueError('Invalid manifest')
    actual={str(f.relative_to(root).as_posix()):f for f in root.rglob('*') if f.is_file() or f.is_symlink()}
    actual.pop('SHA256SUMS.json',None)
    missing=set(manifest)-set(actual);extra=set(actual)-set(manifest)
    errors=['Missing: '+n for n in sorted(missing)]+['Extra: '+n for n in sorted(extra)]
    for name in sorted(set(manifest)&set(actual)):
        f=actual[name]
        if f.is_symlink():errors.append('Symlink: '+name);continue
        if hashlib.sha256(f.read_bytes()).hexdigest()!=manifest[name]:errors.append('SHA256 mismatch: '+name)
    if errors:raise ValueError('\n'.join(errors))
    workflow=json.loads(next((root/'workflows').glob('*.json')).read_text())
    nodes={n['id']:n for n in workflow['nodes']}
    if nodes[3]['properties']['models']!=json.loads((root/'models.json').read_text()):raise ValueError('Model metadata mismatch')
    if workflow['links'][0][5]!='YUE2_PLAN':raise ValueError('Invalid planner connection')
    print('PASS: exact file set and SHA256:',len(manifest),'files')
if __name__=='__main__':
    try:verify(Path(__file__).resolve().parent)
    except (ValueError,OSError) as e:raise SystemExit(str(e))

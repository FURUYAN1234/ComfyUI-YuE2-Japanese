"""Build a reproducible source package from a clean Git checkout."""
import argparse,hashlib,json,re,subprocess,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def build(output):
    dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=normal'],cwd=ROOT,text=True).strip()
    if dirty:raise SystemExit('Build requires a clean Git checkout.')
    version=(ROOT/'VERSION').read_text().strip()
    if not re.fullmatch(r'(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)',version):raise SystemExit('VERSION must be MAJOR.MINOR.PATCH')
    names=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode().split('\0')
    files={n:(ROOT/n).read_bytes() for n in names if n and n not in ('.gitignore',)}
    for n in files:
        if (ROOT/n).is_symlink():raise SystemExit('Source symlink not allowed: '+n)
    hashes={n:hashlib.sha256(b).hexdigest() for n,b in sorted(files.items())}
    files['SHA256SUMS.json']=(json.dumps(hashes,ensure_ascii=False,indent=2)+'\n').encode()
    output=Path(output).expanduser().resolve();output.mkdir(parents=True,exist_ok=True)
    basename='YuE2_Japanese_LMStudio_v'+version
    path=output/(basename+'.zip')
    if path.exists():raise SystemExit('Refusing to overwrite '+str(path))
    with zipfile.ZipFile(path,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for n,b in sorted(files.items()):
            info=zipfile.ZipInfo(basename+'/'+n,date_time=(2000,1,1,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED;info.external_attr=0o100644<<16
            z.writestr(info,b,compresslevel=9)
    print(path)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args();build(a.output)

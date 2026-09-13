"""Install this package into an existing WSL/Linux ComfyUI without modifying its venv."""
import argparse, json, os, shutil, subprocess, sys, urllib.request
from datetime import datetime
from pathlib import Path
ROOT=Path(__file__).resolve().parent
YUE_COMMIT='88da114a67df892af0329472073b96a5ef700b93'
def run(args,**kwargs):
    print(' '.join(map(str,args)),flush=True)
    subprocess.run(list(map(str,args)),check=True,**kwargs)
def copy_with_backup(source,target,backup):
    target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=source.read_bytes():
        backup.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(target,backup)
    shutil.copy2(source,target)
def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--comfyui',type=Path,required=True)
    parser.add_argument('--runtime',type=Path,help='YuE2 environment directory; preserves an existing local_config.json by default')
    parser.add_argument('--workflow-dir',type=Path,help='Optional workflow destination; default: COMFYUI/user/default/workflows/YuE2')
    parser.add_argument('--python',default='python3.12')
    parser.add_argument('--skip-environment',action='store_true',help='Only deploy files into an already verified YuE2 environment')
    a=parser.parse_args();comfy=a.comfyui.expanduser().resolve()
    existing_config=comfy/'custom_nodes/comfyui-yue2-local/local_config.json'
    configured=json.loads(existing_config.read_text()).get('runtime') if existing_config.is_file() else None
    runtime=(a.runtime or (Path(configured) if configured else Path.home()/'.local/share/yue2')).expanduser().resolve()
    if sys.platform!='linux':raise SystemExit('Run this installer inside WSL Ubuntu/Linux, not Windows Python.')
    if not (comfy/'main.py').is_file():raise SystemExit('The specified folder is not ComfyUI.')
    try:
        with urllib.request.urlopen('http://127.0.0.1:8188/queue',timeout=2) as response:q=json.load(response)
    except OSError:q=None
    if q and (q['queue_running'] or q['queue_pending']):raise SystemExit('ComfyUI has active jobs. Wait before installing.')
    runtime.mkdir(parents=True,exist_ok=True);repo=runtime/'repo';python=runtime/'.venv/bin/python'
    if not a.skip_environment:
        if not repo.exists():
            run(['git','clone','--no-checkout','https://github.com/multimodal-art-projection/YuE',repo])
            run(['git','checkout','--detach',YUE_COMMIT],cwd=repo)
        actual=subprocess.check_output(['git','rev-parse','HEAD'],cwd=repo,text=True).strip()
        dirty=subprocess.check_output(['git','status','--porcelain','--untracked-files=no'],cwd=repo,text=True).strip()
        if actual!=YUE_COMMIT or dirty:raise SystemExit('Existing YuE source differs from the pinned clean commit. Select another runtime folder.')
        if not python.exists():run([a.python,'-m','venv',runtime/'.venv'])
        has_pip=subprocess.run([python,'-c','import pip'],capture_output=True).returncode==0
        uv=shutil.which('uv')
        if not has_pip and not uv:raise SystemExit('pip is missing. Install python3.12-venv, or use the uv that created this environment.')
        pip=[python,'-m','pip','install'] if has_pip else [uv,'pip','install','--python',python]
        run([*pip,'torch==2.10.0','--index-url','https://download.pytorch.org/whl/cu128'])
        run([*pip,repo])
    if not python.exists():raise SystemExit('YuE2 Python environment is missing.')
    run([python,'-c',"import torch,yue2; print(torch.__version__,torch.cuda.is_available(),torch.cuda.get_arch_list()); assert torch.cuda.is_available()"])
    stamp=datetime.now().strftime('%Y%m%d%H%M%S');backup=runtime/'backups'/stamp
    for source in (ROOT/'runtime').glob('*.py'):copy_with_backup(source,runtime/source.name,backup/'runtime'/source.name)
    node_target=comfy/'custom_nodes/comfyui-yue2-local'
    for source in (ROOT/'custom_nodes/comfyui-yue2-local').rglob('*'):
        if source.is_file() and '__pycache__' not in source.parts:
            rel=source.relative_to(ROOT/'custom_nodes/comfyui-yue2-local');copy_with_backup(source,node_target/rel,backup/'node'/rel)
    for name in ('download_models.py','models.json'):
        copy_with_backup(ROOT/name,node_target/name,backup/'node'/name)
    config=node_target/'local_config.json'
    if config.exists():
        (backup/'node').mkdir(parents=True,exist_ok=True);shutil.copy2(config,backup/'node'/'local_config.json')
    config.write_text(json.dumps({'runtime':str(runtime)},indent=2))
    workflow_dir=(a.workflow_dir.expanduser().resolve() if a.workflow_dir else comfy/'user/default/workflows/YuE2')
    for source in (ROOT/'workflows').glob('*.json'):
        copy_with_backup(source,workflow_dir/source.name,backup/'workflows'/source.name)
    (comfy/'models/yue2').mkdir(parents=True,exist_ok=True)
    print('Installed. Restart ComfyUI, reload the workflow, and download missing models from its model links.')
    print('Runtime:',runtime,'\nWorkflow folder:',workflow_dir)
if __name__=='__main__':main()

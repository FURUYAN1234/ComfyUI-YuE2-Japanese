"""ComfyUI front end; YuE2 runs only in its dedicated Python environment."""
import os
import importlib.util,json,queue,subprocess,threading,time,uuid
from datetime import datetime
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
import folder_paths
import comfy.model_management as mm
from comfy.utils import ProgressBar

RUNTIME=Path(os.environ.get('COMFYUI_YUE2_HOME',str(Path.home()/'Codex/work/yue2')))
local_config=Path(__file__).with_name('local_config.json')
if local_config.is_file():RUNTIME=Path(json.loads(local_config.read_text())['runtime'])
MODEL_ROOT=Path(folder_paths.models_dir)/'yue2'
folder_paths.add_model_folder_path('yue2',str(MODEL_ROOT))
folder_paths.folder_names_and_paths['yue2'][1].update({'.safetensors','.json','.tiktoken','.md',''})
def planner_module():
    spec=importlib.util.spec_from_file_location('yue2_local_planner',RUNTIME/'planner.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class YuE2JapanesePlanner:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'brief':('STRING',{'multiline':True,'default':'雨の日にコンビニ行く感じ。ちょっと切ないけど明るい、女の子の声で。歌詞もおまかせ。'}),'length':(['短い試作（4行）','通常（16行）'],),'seed':('INT',{'default':831001,'min':0,'max':2147483647}),'duration_mode':(['歌詞量で指定（従来）','目標30秒（試験的）','目標60秒（試験的）','目標120秒（試験的）','秒数を指定（目安）'],),'target_seconds':('INT',{'default':30,'min':10,'max':240,'tooltip':'秒数を指定（目安）で使用。生成結果の長さを保証する値ではありません。'})}}
    RETURN_TYPES=('YUE2_PLAN',);RETURN_NAMES=('曲の企画JSON / Song plan',);FUNCTION='create';CATEGORY='audio/YuE2'
    def create(self,brief,length,seed,duration_mode='歌詞量で指定（従来）',target_seconds=30):
        mm.throw_exception_if_processing_interrupted()
        mm.unload_all_models();mm.soft_empty_cache()
        bar=ProgressBar(4);n=0
        def progress(message):
            nonlocal n
            print('[YuE2 Planner] '+message,flush=True);n+=1;bar.update_absolute(min(n,4),4)
        plan,report=planner_module().plan_song(brief,short=length.startswith('短い'),seed=seed,progress=progress,duration_mode=duration_mode,target_seconds=target_seconds)
        return (json.dumps({'brief':brief,'plan':plan,'report':report},ensure_ascii=False,indent=2),)

class YuE2LocalSong:
    @classmethod
    def INPUT_TYPES(cls):
        files=folder_paths.get_filename_list('yue2')
        return {'required':{'song_plan':('YUE2_PLAN',),'seed':('INT',{'default':831001,'min':0,'max':2147483647}),'model':([x for x in files if x=='YuE2-3B/model.safetensors'],),'vae':([x for x in files if x=='YuE2-Vae/model.safetensors'],)}}
    RETURN_TYPES=('AUDIO','STRING');RETURN_NAMES=('曲 / Audio','生成記録 / Details');FUNCTION='generate';CATEGORY='audio/YuE2'
    def generate(self,song_plan,seed,model='YuE2-3B/model.safetensors',vae='YuE2-Vae/model.safetensors'):
        data=json.loads(song_plan);plan=planner_module().validate(data['plan'])
        if not (RUNTIME/'.venv/bin/python').is_file():raise RuntimeError('YuE2独立環境が見つかりません。')
        mm.throw_exception_if_processing_interrupted();mm.unload_all_models();mm.soft_empty_cache()
        job=datetime.now().strftime('%Y%m%d%H%M%S')+'_'+uuid.uuid4().hex[:6]
        output=Path(folder_paths.get_output_directory())/'audio'/'YuE2'/job
        output.parent.mkdir(parents=True,exist_ok=True)
        request={'id':'song_'+job,'style':plan['style'],'lyrics':plan['lyrics'],'cot':'full','seed':seed}
        paths=[]
        for name in (model,vae):
            found=folder_paths.get_full_path('yue2',name)
            if not found:raise RuntimeError('モデルがありません。ワークフローの不足モデル案内から取得してください: '+name)
            paths.append(str(Path(found).parent))
        jobs=RUNTIME/'jobs';jobs.mkdir(exist_ok=True)
        request_file=jobs/(job+'.json');request_file.write_text(json.dumps(request,ensure_ascii=False,indent=2))
        (jobs/(job+'.plan.json')).write_text(song_plan)
        command=[str(RUNTIME/'.venv/bin/python'),'-u',str(RUNTIME/'run_song.py'),'--request',str(request_file),'--output',str(output),'--model-dir',paths[0],'--vae-dir',paths[1]]
        lines=queue.Queue();tail=[];bar=ProgressBar(5);start=time.monotonic()
        with (jobs/(job+'.log')).open('w') as log:
            child_env=os.environ.copy()
            for key in ('PYTHONPATH','PYTHONHOME','LD_LIBRARY_PATH'):child_env.pop(key,None)
            process=subprocess.Popen(command,env=child_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,bufsize=1)
            def reader():
                for line in process.stdout:lines.put(line)
            thread=threading.Thread(target=reader,daemon=True);thread.start()
            try:
                while process.poll() is None or not lines.empty():
                    mm.throw_exception_if_processing_interrupted()
                    if time.monotonic()-start>1200:raise TimeoutError('YuE2生成が20分を超えたため停止しました。ログを確認してください。')
                    try:line=lines.get(timeout=.5)
                    except queue.Empty:continue
                    log.write(line);log.flush();tail.append(line);tail=tail[-15:];print(line.rstrip(),flush=True)
                    for marker,value in [('Planning score',1),('Generating song',2),('Synthesizing audio',3),('Decoding audio',4)]:
                        if marker in line:bar.update_absolute(value,5)
                if process.wait()!=0:raise RuntimeError('YuE2生成に失敗しました。\n'+''.join(tail))
            finally:
                if process.poll() is None:
                    process.terminate()
                    try:process.wait(timeout=10)
                    except subprocess.TimeoutExpired:process.kill();process.wait()
                    state_path=output.with_suffix('.state.json')
                    state=json.loads(state_path.read_text()) if state_path.exists() else {}
                    state.update(status='interrupted',ended_at=datetime.now().astimezone().isoformat());state_path.write_text(json.dumps(state,ensure_ascii=False,indent=2))
        result=json.loads((output/'result.json').read_text())
        if any(result['truncated'].values()):raise RuntimeError('生成が途中で打ち切られました。音声は検証用として保存しています: '+str(output))
        wave,sr=sf.read(output/'audio.flac',dtype='float32',always_2d=True)
        if sr!=48000 or len(wave)<sr or not np.isfinite(wave).all() or np.max(np.abs(wave))<1e-5:raise RuntimeError('生成音声の形式または波形が不正です。')
        (output/'song_plan.json').write_text(song_plan)
        bar.update_absolute(5,5)
        details={'title':plan['title'],'folder':str(output),'audio_seconds':result['audio_seconds'],'lyrics':plan['lyrics'],'style':plan['style'],'target_seconds':data.get('report',{}).get('duration',{}).get('target_seconds'),'duration_mode':data.get('report',{}).get('duration',{}).get('mode','歌詞量で指定（従来）'),'song_generation_seconds':round(time.monotonic()-start,2),'duration_note':'目標秒数は目安です。実際の秒数はaudio_secondsを確認してください。','note':'日本語歌唱の品質は試聴して確認してください。モデルはCC BY-NC 4.0。'}
        return ({'waveform':torch.from_numpy(wave.T.copy()).unsqueeze(0),'sample_rate':sr},json.dumps(details,ensure_ascii=False,indent=2))

NODE_CLASS_MAPPINGS={'YuE2JapanesePlanner':YuE2JapanesePlanner,'YuE2LocalSong':YuE2LocalSong}
NODE_DISPLAY_NAME_MAPPINGS={'YuE2JapanesePlanner':'YuE2 日本語おまかせ作詞 / LM Studio GPU','YuE2LocalSong':'YuE2 曲生成 / Isolated GPU'}

# Fixed official manifest only: the browser cannot choose URLs or destination paths.
import asyncio, sys
from aiohttp import web
from server import PromptServer
WEB_DIRECTORY='./web'
_download_lock=asyncio.Lock()
@PromptServer.instance.routes.post('/yue2/download-models')
async def download_required_models(request):
    if request.headers.get('Origin') and request.headers['Origin'].split('://',1)[-1] != request.host:
        return web.json_response({'error':'Cross-origin request rejected'},status=403)
    if _download_lock.locked():return web.json_response({'error':'モデル取得は既に実行中です。'},status=409)
    running,pending=PromptServer.instance.prompt_queue.get_current_queue()
    if running or pending:return web.json_response({'error':'生成キューが空になってからモデルを取得してください。'},status=409)
    async with _download_lock:
        helper=Path(__file__).with_name('download_models.py')
        child=await asyncio.create_subprocess_exec(sys.executable,str(helper),'--comfyui',str(Path(folder_paths.base_path)),stdout=asyncio.subprocess.PIPE,stderr=asyncio.subprocess.STDOUT)
        try:
            output,_=await asyncio.wait_for(child.communicate(),timeout=1800)
        except (asyncio.TimeoutError,asyncio.CancelledError):
            child.terminate()
            try:await asyncio.wait_for(child.wait(),timeout=10)
            except asyncio.TimeoutError:child.kill();await child.wait()
            return web.json_response({'error':'取得が中断されました。部分ファイルとログを確認してください。'},status=504)
        message=output.decode(errors='replace')[-5000:]
        print('[YuE2 models] '+message,flush=True)
        if child.returncode:return web.json_response({'error':message},status=500)
        return web.json_response({'message':'必須13ファイルの取得・SHA256確認が完了しました。モデル一覧を更新、またはComfyUIを再起動してください。'})

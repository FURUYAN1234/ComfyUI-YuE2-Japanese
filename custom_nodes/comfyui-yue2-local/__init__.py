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

RUNTIME=Path('/home/furu/Codex/work/yue2')
def planner_module():
    spec=importlib.util.spec_from_file_location('yue2_local_planner',RUNTIME/'planner.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

class YuE2JapanesePlanner:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'brief':('STRING',{'multiline':True,'default':'雨の日にコンビニ行く感じ。ちょっと切ないけど明るい、女の子の声で。歌詞もおまかせ。'}),'length':(['短い試作（4行）','通常（16行）'],),'seed':('INT',{'default':831001,'min':0,'max':2147483647})}}
    RETURN_TYPES=('YUE2_PLAN',);RETURN_NAMES=('曲の企画JSON / Song plan',);FUNCTION='create';CATEGORY='audio/YuE2'
    def create(self,brief,length,seed):
        mm.throw_exception_if_processing_interrupted()
        mm.unload_all_models();mm.soft_empty_cache()
        bar=ProgressBar(4);n=0
        def progress(message):
            nonlocal n
            print('[YuE2 Planner] '+message,flush=True);n+=1;bar.update_absolute(min(n,4),4)
        plan,report=planner_module().plan_song(brief,short=length.startswith('短い'),seed=seed,progress=progress)
        return (json.dumps({'brief':brief,'plan':plan,'report':report},ensure_ascii=False,indent=2),)

class YuE2LocalSong:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'song_plan':('YUE2_PLAN',),'seed':('INT',{'default':831001,'min':0,'max':2147483647})}}
    RETURN_TYPES=('AUDIO','STRING');RETURN_NAMES=('曲 / Audio','生成記録 / Details');FUNCTION='generate';CATEGORY='audio/YuE2'
    def generate(self,song_plan,seed):
        data=json.loads(song_plan);plan=planner_module().validate(data['plan'])
        if not (RUNTIME/'.venv/bin/python').is_file():raise RuntimeError('YuE2独立環境が見つかりません。')
        mm.throw_exception_if_processing_interrupted();mm.unload_all_models();mm.soft_empty_cache()
        job=datetime.now().strftime('%Y%m%d%H%M%S')+'_'+uuid.uuid4().hex[:6]
        output=Path(folder_paths.get_output_directory())/'audio'/'YuE2'/job
        output.parent.mkdir(parents=True,exist_ok=True)
        request={'id':'song_'+job,'style':plan['style'],'lyrics':plan['lyrics'],'cot':'full','seed':seed}
        jobs=RUNTIME/'jobs';jobs.mkdir(exist_ok=True)
        request_file=jobs/(job+'.json');request_file.write_text(json.dumps(request,ensure_ascii=False,indent=2))
        (jobs/(job+'.plan.json')).write_text(song_plan)
        command=[str(RUNTIME/'.venv/bin/python'),'-u',str(RUNTIME/'run_song.py'),'--request',str(request_file),'--output',str(output)]
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
        details={'title':plan['title'],'folder':str(output),'audio_seconds':result['audio_seconds'],'lyrics':plan['lyrics'],'style':plan['style'],'timing':result['timing'],'note':'日本語歌唱の品質は試聴して確認してください。モデルはCC BY-NC 4.0。'}
        return ({'waveform':torch.from_numpy(wave.T.copy()).unsqueeze(0),'sample_rate':sr},json.dumps(details,ensure_ascii=False,indent=2))

NODE_CLASS_MAPPINGS={'YuE2JapanesePlanner':YuE2JapanesePlanner,'YuE2LocalSong':YuE2LocalSong}
NODE_DISPLAY_NAME_MAPPINGS={'YuE2JapanesePlanner':'YuE2 日本語おまかせ作詞 / LM Studio GPU','YuE2LocalSong':'YuE2 曲生成 / Isolated GPU'}

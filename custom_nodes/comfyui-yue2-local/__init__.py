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

RUNTIME=Path(os.environ.get('COMFYUI_YUE2_HOME',str(Path.home()/'.local/share/yue2')))
local_config=Path(__file__).with_name('local_config.json')
if local_config.is_file():RUNTIME=Path(json.loads(local_config.read_text())['runtime'])
MODEL_ROOT=Path(folder_paths.models_dir)/'yue2'
folder_paths.add_model_folder_path('yue2',str(MODEL_ROOT))
folder_paths.folder_names_and_paths['yue2'][1].update({'.safetensors','.json','.tiktoken','.md',''})
def runtime_module(name):
    spec=importlib.util.spec_from_file_location('yue2_local_'+name,RUNTIME/(name+'.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

def planner_module():return runtime_module('planner')

def notify_planner(node_id,state,message):
    from server import PromptServer
    server=PromptServer.instance
    if server and server.client_id:
        server.send_sync('yue2.llm_status',{'node_id':str(node_id),'state':state,'message':message},server.client_id)


class YuE2SongOptions:
    @classmethod
    def INPUT_TYPES(cls):
        o=runtime_module('song_options')
        return {'required':{'mode':(o.MODES,),'voice':(list(o.VOICES),),'genre':(list(o.GENRES),),'mood':(list(o.MOODS),),'instruments':(list(o.INSTRUMENTS),),'bpm':('INT',{'default':0,'min':0,'max':220,'tooltip':'0=おまかせ。指定は40〜220。'}),'timing':(o.TIMING,),'seconds':('INT',{'default':30,'min':10,'max':240})}}
    RETURN_TYPES=('YUE2_OPTIONS',);RETURN_NAMES=('Settings / 設定',);FUNCTION='create';CATEGORY='audio/YuE2'
    def create(self,**kwargs):return (runtime_module('song_options').settings(**kwargs),)

class YuE2SongSwitches(YuE2SongOptions):
    @classmethod
    def INPUT_TYPES(cls):
        fields=super().INPUT_TYPES()['required'];fields.pop('mode')
        return {'required':{
            'use_presets':('BOOLEAN',{'default':True,'label_on':'ON / 使用','label_off':'OFF / 不使用','tooltip':'Use presets / プリセットを使用。手動と両方OFFは不可。'}),
            'use_manual':('BOOLEAN',{'default':False,'label_on':'ON / 使用','label_off':'OFF / 不使用','tooltip':'Use manual lyrics/style / 手動歌詞・曲調を使用。両方ONなら曲調を追加。'}),**fields}}
    @classmethod
    def VALIDATE_INPUTS(cls,use_presets,use_manual):
        return True if use_presets or use_manual else 'プリセットと手動入力を両方OFFにはできません。どちらかをONにしてください。'
    def create(self,use_presets,use_manual,**kwargs):
        return super().create(mode='手動' if use_manual else 'プリセット',use_presets=use_presets,use_manual=use_manual,**kwargs)

class YuE2InputSwitches(YuE2SongSwitches):
    @classmethod
    def INPUT_TYPES(cls):
        fields=super().INPUT_TYPES()['required']
        return {'required':{k:fields[k] for k in ('use_presets','use_manual','timing','seconds')}}
    RETURN_TYPES=('YUE2_SWITCHES',);RETURN_NAMES=('Input control / 入力制御',)
    def create(self,use_presets,use_manual,timing,seconds):
        values=runtime_module('song_options').settings(use_presets=use_presets,use_manual=use_manual,timing=timing,seconds=seconds)
        return ({k:values[k] for k in ('use_presets','use_manual','timing','seconds')},)

class YuE2PresetOptions(YuE2SongOptions):
    @classmethod
    def INPUT_TYPES(cls):
        fields=super().INPUT_TYPES()['required']
        return {'required':{k:v for k,v in fields.items() if k not in ('mode','timing','seconds')}}

class YuE2ManualLyrics:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'title':('STRING',{'default':'手動入力の曲'}),'lyrics':('STRING',{'multiline':True,'default':''}),'style':('STRING',{'multiline':True,'default':''})}}
    RETURN_TYPES=('YUE2_MANUAL',);RETURN_NAMES=('Manual lyrics / 手動歌詞',);FUNCTION='create';CATEGORY='audio/YuE2'
    def create(self,title,lyrics,style):return ({'title':title,'lyrics':lyrics,'style':style},)

class YuE2VisualTheme:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'enabled':('BOOLEAN',{'default':False,'label_on':'ON / 画像から全部おまかせ','label_off':'OFF / 画像を使わない'}),'kind':(['4コマ漫画','1枚絵'],),'reading_order':(['上から下','右上→左上→右下→左下','左上→右上→左下→右下'],),'dialogue':(['内容を解釈してオリジナル歌詞','読めたセリフを歌詞に取り入れる'],)},'optional':{'image':('IMAGE',)}}
    RETURN_TYPES=('YUE2_VISUAL',);RETURN_NAMES=('Visual theme / 画像テーマ',);FUNCTION='create';CATEGORY='audio/YuE2'
    def create(self,enabled,kind,reading_order,dialogue,image=None):
        if not enabled:return ({'enabled':False},)
        if image is None or len(image)!=1:raise ValueError('画像ONでは1枚の画像を接続してください。4コマは1枚にまとめた画像を使用します。')
        import io,base64
        from PIL import Image
        picture=Image.fromarray((image[0].detach().cpu().numpy().clip(0,1)*255).astype(np.uint8)).convert('RGB')
        def encode(part):
            part=part.copy();part.thumbnail((1600,1600),Image.Resampling.LANCZOS)
            buffer=io.BytesIO();part.save(buffer,format='JPEG',quality=94)
            return 'data:image/jpeg;base64,'+base64.b64encode(buffer.getvalue()).decode('ascii')
        images=[encode(picture)]
        if kind=='4コマ漫画':
            w,h=picture.size
            if reading_order=='上から下':boxes=[(0,max(0,int(h*i/4-h*.04)),w,min(h,int(h*(i+1)/4+h*.04))) for i in range(4)]
            else:
                boxes=[(0,0,int(w*.54),int(h*.54)),(int(w*.46),0,w,int(h*.54)),(0,int(h*.46),int(w*.54),h),(int(w*.46),int(h*.46),w,h)]
                if reading_order.startswith('右'):boxes=[boxes[i] for i in (1,0,3,2)]
            images.extend(encode(picture.crop(box)) for box in boxes)
        return ({'enabled':True,'kind':kind,'reading_order':reading_order,'dialogue':dialogue,'image_url':images[0],'image_urls':images},)

class YuE2JapanesePlanner:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'brief':('STRING',{'multiline':True,'default':'雨の日にコンビニ行く感じ。ちょっと切ないけど明るい、女の子の声で。歌詞もおまかせ。'}),'length':(['短い試作（4行）','通常（16行）'],),'seed':('INT',{'default':831001,'min':0,'max':2147483647}),'duration_mode':(['歌詞量で指定（従来）','目標30秒（試験的）','目標60秒（試験的）','目標120秒（試験的）','秒数を指定（目安）'],),'target_seconds':('INT',{'default':30,'min':10,'max':240,'tooltip':'秒数を指定（目安）で使用。生成結果の長さを保証する値ではありません。'})},'optional':{'settings':('YUE2_OPTIONS',),'manual':('YUE2_MANUAL',),'switches':('YUE2_SWITCHES',),'visual':('YUE2_VISUAL',)},'hidden':{'unique_id':'UNIQUE_ID'}}
    RETURN_TYPES=('YUE2_PLAN',);RETURN_NAMES=('曲の企画JSON / Song plan',);FUNCTION='create';CATEGORY='audio/YuE2'
    def create(self,brief,length,seed,duration_mode='歌詞量で指定（従来）',target_seconds=30,settings=None,manual=None,switches=None,lyric_lines=None,unique_id=None,visual=None):
        mm.throw_exception_if_processing_interrupted()
        chosen=None; manual_plan=None; original_brief=brief
        if switches is not None:
            settings={**(settings or runtime_module('song_options').settings()),**switches}
            settings['mode']='手動' if settings['use_manual'] else 'プリセット'
        visual=visual if visual and visual.get('enabled') else None
        if visual:
            current=settings or runtime_module('song_options').settings()
            settings=runtime_module('song_options').settings(timing='1曲（イントロ〜エンディング）',seconds=current['seconds'])
            manual=None
            brief='画像の登場人物・セリフ・物語に合う日本語のテーマソング。曲調と歌声もすべておまかせ。'
        if settings is not None:
            chosen,manual_plan,brief=runtime_module('song_options').prepare(brief,settings,manual)
            duration_mode=chosen['timing'] if chosen['timing']=='1曲（イントロ〜エンディング）' else '歌詞量で指定（従来）' if chosen['timing']=='可変尺（自然な長さ）' else '秒数を指定（目安）'
            target_seconds=chosen['seconds']
        if manual_plan is not None:
            mm.unload_all_models();mm.soft_empty_cache()
            notify_planner(unique_id,'running','LM Studio: 手動歌詞の曲名を考えます / Naming your lyrics')
            try:plan,title_report=planner_module().title_song(planner_module().validate(manual_plan),seed,progress=lambda message:notify_planner(unique_id,'running',message))
            except Exception:
                notify_planner(unique_id,'error','曲名生成が停止しました / Title generation stopped');raise
            notify_planner(unique_id,'complete','曲名完了・LLM解放済み / Title ready; LLM unloaded')
            report={**title_report,'mode':'manual','llm_called':True,'duration':{**planner_module().duration_plan(length.startswith('短い'),duration_mode,target_seconds),'lyric_lines':sum(bool(x.strip()) and not x.lstrip().startswith('[') for x in plan['lyrics'].splitlines()),'line_source':'manual'},'settings':chosen}
            return (json.dumps({'brief':original_brief,'plan':plan,'report':report,'settings':chosen},ensure_ascii=False,indent=2),)
        mm.unload_all_models();mm.soft_empty_cache()
        bar=ProgressBar(4);n=0
        def progress(message):
            nonlocal n
            print('[YuE2 Planner] '+message,flush=True);notify_planner(unique_id,'running',message);n+=1;bar.update_absolute(min(n,4),4)
        notify_planner(unique_id,'running','LM Studio: 起動・接続を確認しています / Checking LLM startup')
        try:
            plan,report=planner_module().plan_song(brief,short=length.startswith('短い'),seed=seed,progress=progress,duration_mode=duration_mode,target_seconds=target_seconds,lyric_lines=lyric_lines,**({"visual":visual} if visual else {}))
        except Exception:
            notify_planner(unique_id,'error','LLM処理が停止しました。実行エラーを確認してください / LLM stopped; check execution error')
            raise
        notify_planner(unique_id,'complete','作詞完了・LLM解放済み / Lyrics ready; LLM unloaded')
        if chosen:
            report['settings']=chosen
            if chosen['style']:plan['style']=chosen['style']+', '+plan['style']
        return (json.dumps({'brief':original_brief,'plan':plan,'report':report,'settings':chosen},ensure_ascii=False,indent=2),)

class YuE2LyricPlanner(YuE2JapanesePlanner):
    LINE_PRESETS={'短い試作（4行）':4,'8行':8,'12行':12,'通常（16行）':16,'24行':24,'32行':32}
    @classmethod
    def INPUT_TYPES(cls):
        fields=super().INPUT_TYPES()
        return {'required':{'brief':fields['required']['brief'],
            'lyric_length':([*cls.LINE_PRESETS,'自由に指定'],{'tooltip':'LLMが作詞する歌詞の行数。曲の秒数は入力切替ノードで設定します。'}),
            'lyric_lines':('INT',{'default':8,'min':1,'max':64,'tooltip':'自由に指定を選んだときの行数。空行や[Verse]などの見出しを除く1〜64行。'}),
            'seed':fields['required']['seed']},'optional':fields['optional'],'hidden':{'unique_id':'UNIQUE_ID'}}
    def create(self,brief,lyric_length,lyric_lines,seed,settings=None,manual=None,switches=None,unique_id=None,visual=None):
        counts={**self.LINE_PRESETS,'自由に指定':lyric_lines}
        if lyric_length not in counts:raise ValueError('歌詞の行数の選択が不正です。')
        if type(lyric_lines) is not int or not 1<=lyric_lines<=64:raise ValueError('自由指定の歌詞は1〜64行です。')
        return super().create(brief,'短い試作（4行）',seed,settings=settings,manual=manual,switches=switches,lyric_lines=counts[lyric_length],unique_id=unique_id,visual=visual)


class YuE2Pronunciation:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'song_plan':('YUE2_PLAN',),'enabled':('BOOLEAN',{'default':True}),
            'action':(['今回だけ / Once','記憶・更新 / Remember','登録を削除 / Delete'],),
            'corrections':('STRING',{'multiline':True,'default':'','tooltip':'単語=よみ を1行ずつ入力。同じ単語の登録で更新。削除時は単語だけ。長い語句を優先。'})}}
    RETURN_TYPES=('YUE2_PLAN','STRING');RETURN_NAMES=('Readings applied / 読み適用済み','Review / 読み・辞書の確認')
    FUNCTION='correct';CATEGORY='audio/YuE2'
    @classmethod
    def IS_CHANGED(cls,**kwargs):
        # Dictionary changes made by another workflow must invalidate cached results.
        import hashlib
        path=RUNTIME/'private'/'lyric_readings.json'
        return hashlib.sha256(path.read_bytes()).hexdigest() if path.exists() else 'empty'
    def correct(self,song_plan,enabled,action,corrections):
        from .reading import apply
        return apply(song_plan,enabled,action,corrections,RUNTIME/'private'/'lyric_readings.json')

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
        chosen=data.get('settings')
        finish=None
        if chosen:
            finish=runtime_module('audio_finish').finish_audio(output,chosen['timing'],chosen['seconds'])
            result['generated_audio_seconds']=result['audio_seconds'];result['audio_seconds']=finish['output_seconds'];result['postprocess']=finish
            (output/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
        wave,sr=sf.read(output/'audio.flac',dtype='float32',always_2d=True)
        if sr!=48000 or len(wave)<sr or not np.isfinite(wave).all() or np.max(np.abs(wave))<1e-5:raise RuntimeError('生成音声の形式または波形が不正です。')
        (output/'song_plan.json').write_text(song_plan)
        bar.update_absolute(5,5)
        details={'workflow_version':Path(__file__).with_name('VERSION').read_text().strip(),'created_at':job[:14],'title':plan['title'],'folder':str(output),'audio_seconds':result['audio_seconds'],'lyrics':data.get('display_lyrics',plan['lyrics']),'style':plan['style'],'target_seconds':data.get('report',{}).get('duration',{}).get('target_seconds'),'duration_mode':data.get('report',{}).get('duration',{}).get('mode','歌詞量で指定（従来）'),'song_generation_seconds':round(time.monotonic()-start,2),'duration_note':'目標秒数は目安です。実際の秒数はaudio_secondsを確認してください。','note':'日本語歌唱の品質は試聴して確認してください。モデルはCC BY-NC 4.0。'}
        if data.get('report',{}).get('image_reading'):details['image_reading']=data['report']['image_reading']
        if chosen:
            details.update(creation_mode=chosen['mode'],settings=chosen,duration_mode=chosen['timing'],target_seconds=None if chosen['timing'] in ['可変尺（自然な長さ）','1曲（イントロ〜エンディング）'] else chosen['seconds'],postprocess=finish)
            if chosen['timing']=='ぴったり尺（編集）':details['duration_note']='指定尺へ編集済み。末尾フェード・カット／無音補完を使用。元音声はaudio_original.flacに保存。'
        if chosen and chosen['timing']=='1曲（イントロ〜エンディング）':details['duration_note']='1曲構成・秒数カットなし。手動ONでは入力歌詞を維持。曲の終わり方は試聴で確認してください。'
        if data.get('pronunciation'): details['pronunciation']=data['pronunciation']
        (output/'details.json').write_text(json.dumps(details,ensure_ascii=False,indent=2))
        return {'ui':{'yue2_song':[{'title':plan['title'],'seconds':result['audio_seconds']}]},'result':({'waveform':torch.from_numpy(wave.T.copy()).unsqueeze(0),'sample_rate':sr},json.dumps(details,ensure_ascii=False,indent=2))}

def song_folder(details):
    data=json.loads(details);root=Path(folder_paths.get_output_directory()).resolve();folder=Path(data['folder']).resolve()
    if not folder.is_relative_to(root/'audio'/'YuE2') or not (folder/'audio.flac').is_file():raise ValueError('YuE2 output folder is invalid.')
    return data,folder,str(folder.relative_to(root))

def named_asset(data,folder,source,kind=''):
    import re,unicodedata,shutil
    title=unicodedata.normalize('NFC',data['title']);title=re.sub(r'[<>:"/\\|?*\x00-\x1f]', '_',title).strip(' .')[:64] or 'Song'
    version=data.get('workflow_version',Path(__file__).with_name('VERSION').read_text().strip())
    stamp=data.get('created_at',folder.name.split('_')[0])
    if not re.fullmatch(r'\d{14}',stamp) or not re.fullmatch(r'\d+\.\d+\.\d+',version):raise ValueError('Invalid song version or timestamp')
    target=folder/(title+('_'+kind if kind else '')+'_v'+version+'_'+stamp+Path(source).suffix)
    if not target.exists():
        try:os.link(folder/source,target)
        except OSError:
            with target.open('xb') as out,(folder/source).open('rb') as inp:shutil.copyfileobj(inp,out)
    elif target.read_bytes()!=(folder/source).read_bytes():raise FileExistsError('Named output already contains different data.')
    return target.name

class YuE2AudioOutput:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'audio':('AUDIO',),'details':('STRING',{'forceInput':True})}}
    RETURN_TYPES=();FUNCTION='show';OUTPUT_NODE=True;CATEGORY='audio/YuE2'
    def show(self,audio,details):
        data,folder,subfolder=song_folder(details)
        filename=named_asset(data,folder,'audio.flac')
        return {'ui':{'yue2_media':[{'kind':'audio','lyrics':data['lyrics'],'title':data['title'],'seconds':data['audio_seconds'],'subfolder':subfolder,'play':filename,'download':filename}]},'result':()}

class YuE2MidiOutput:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'details':('STRING',{'forceInput':True})}}
    RETURN_TYPES=();FUNCTION='show';OUTPUT_NODE=True;CATEGORY='audio/YuE2'
    def show(self,details):
        data,folder,subfolder=song_folder(details)
        result=subprocess.run([str(RUNTIME/'.venv/bin/python'),str(RUNTIME/'midi_export.py'),str(folder)],capture_output=True,text=True,timeout=90)
        if result.returncode:raise RuntimeError('MIDI export failed: '+result.stderr[-2000:])
        report=json.loads(result.stdout)
        filename=named_asset(data,folder,'score.mid');preview=named_asset(data,folder,'midi_preview.wav','MIDI試聴')
        return {'ui':{'yue2_media':[{'kind':'midi','lyrics':data['lyrics'],'lyric_alignment':report['lyric_alignment'],'lyric_timeline':report['lyric_timeline'],'title':data['title'],'seconds':report['seconds'],'notes':report['notes'],'subfolder':subfolder,'play':preview,'download':filename}]},'result':()}

NODE_CLASS_MAPPINGS={'YuE2Pronunciation':YuE2Pronunciation,'YuE2VisualTheme':YuE2VisualTheme,'YuE2AudioOutput':YuE2AudioOutput,'YuE2MidiOutput':YuE2MidiOutput,'YuE2LyricPlanner':YuE2LyricPlanner,'YuE2InputSwitches':YuE2InputSwitches,'YuE2PresetOptions':YuE2PresetOptions,'YuE2SongSwitches':YuE2SongSwitches,'YuE2SongOptions':YuE2SongOptions,'YuE2ManualLyrics':YuE2ManualLyrics,'YuE2JapanesePlanner':YuE2JapanesePlanner,'YuE2LocalSong':YuE2LocalSong}
NODE_DISPLAY_NAME_MAPPINGS={'YuE2Pronunciation':'Lyric readings & memory / 歌詞の読み修正・記憶','YuE2VisualTheme':'Visual theme / 画像・漫画から全部おまかせ','YuE2AudioOutput':'Audio playback & download / 音声の再生・保存','YuE2MidiOutput':'Lyrics MIDI / 歌詞付きMIDIの試聴・保存','YuE2LyricPlanner':'Japanese lyrics / 日本語の作詞・歌詞行数','YuE2InputSwitches':'Input switches / 入力切り替え','YuE2PresetOptions':'Music presets / 音楽プリセット','YuE2SongSwitches':'Preset / Manual switches / プリセット・手動切替','YuE2SongOptions':'Song presets / 曲のプリセット','YuE2ManualLyrics':'Manual lyrics / 手動歌詞・曲調','YuE2JapanesePlanner':'YuE2 日本語おまかせ作詞 / LM Studio GPU','YuE2LocalSong':'YuE2 曲生成 / Isolated GPU'}

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

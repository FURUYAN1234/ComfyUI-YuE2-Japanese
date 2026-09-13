"""Local GPU lyric/style planning for YuE2; no cloud API."""
import json, os, re, socket, struct, subprocess, time, urllib.request, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
MODEL='qwen/qwen3.5-9b'
IDENTIFIER='yue2-planner'
SCHEMA={'type':'object','properties':{k:{'type':'string'} for k in ('title','style','lyrics')},'required':['title','style','lyrics'],'additionalProperties':False}
SYSTEM='''あなたは日本語の作詞家です。ユーザーの曖昧な指示を補い、歌詞と曲調を完成させてください。
JSONのtitleは日本語の曲名、styleは英語の具体的な曲調説明（歌唱言語、ジャンル、感情、楽器、声質、テンポ）、lyricsは実際に歌うオリジナル歌詞です。
言語指定がなければ日本語の歌詞とJapanese vocalsを使います。固有アーティスト名の代わりに音楽的特徴を記述します。
歌詞は口ずさみやすい短い行にします。動作、温度、感覚、時系列の意味に矛盾がない自然な言葉を選んでください。
未指定の設定は質問せず補います。ユーザーが歌詞を指定した場合はその内容を尊重します。解説は歌詞に入れません。JSONだけを返します。'''
def endpoint():
 for line in Path('/proc/net/route').read_text().splitlines()[1:]:
  fields=line.split()
  if fields[1]=='00000000': return 'http://'+socket.inet_ntoa(struct.pack('<L',int(fields[2],16)))+':1234'
 raise RuntimeError('WSLのWindows側アドレスを取得できません。')
def cli_path():
 configured=os.environ.get('YUE2_LMS_CLI')
 if configured:
  if not Path(configured).is_file():raise RuntimeError('YUE2_LMS_CLIの実行ファイルがありません。')
  return configured
 ps=shutil.which('powershell.exe')
 if ps:
  r=subprocess.run([ps,'-NoProfile','-Command',"[Environment]::GetFolderPath('LocalApplicationData')"],capture_output=True,timeout=15,check=True)
  windows=r.stdout.decode(errors='replace').strip()
  base=subprocess.check_output(['wslpath','-u',windows],text=True,timeout=5).strip()
  candidate=Path(base)/'Programs/LM Studio/resources/app/.webpack/lms.exe'
  if candidate.is_file():return str(candidate)
 found=shutil.which('lms') or shutil.which('lms.exe')
 if found:return found
 raise RuntimeError('LM Studio CLIがありません。WindowsにLM Studioを導入し、READMEのCLI確認を実行してください。')
def cli(*args,timeout=180):
 exe=cli_path()
 r=subprocess.run([exe,*args],stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=timeout)
 if r.returncode: raise RuntimeError('LM Studio: '+r.stderr.decode(errors='replace')[-700:])
 return r.stdout.decode(errors='replace')
def api(base,path,data=None,timeout=180):
 req=urllib.request.Request(base+path,data=None if data is None else json.dumps(data,ensure_ascii=False).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=timeout) as response:return json.load(response)
def validate(plan):
 if not isinstance(plan,dict) or set(plan)!=set(SCHEMA['required']): raise ValueError('曲データの項目が不正です。')
 for k,limit in [('title',160),('style',3000),('lyrics',12000)]:
  if not isinstance(plan[k],str) or not plan[k].strip() or len(plan[k])>limit: raise ValueError(k+'が空欄、または長すぎます。')
 if not re.search(r'\[(Verse|Chorus|Intro|Bridge|Outro)[^\]]*\]',plan['lyrics'],re.I):raise ValueError('歌詞のセクションがありません。')
 if '<think>' in plan['lyrics'] or '```' in plan['lyrics']:raise ValueError('歌詞に生成用の説明が混入しました。')
 return plan
DURATION_MODES=('歌詞量で指定（従来）','目標30秒（試験的）','目標60秒（試験的）','目標120秒（試験的）','秒数を指定（目安）')
def duration_plan(short,mode,target_seconds):
 if mode not in DURATION_MODES:raise ValueError('長さの指定方法が不正です。')
 if type(target_seconds) is not int or not 10<=target_seconds<=240:raise ValueError('目標秒数は10〜240の整数で指定してください。')
 target={'目標30秒（試験的）':30,'目標60秒（試験的）':60,'目標120秒（試験的）':120}.get(mode)
 if mode=='秒数を指定（目安）':target=target_seconds
 total=(4 if short else 16) if target is None else max(2,min(24,2*int(target/20+.5)))
 return {'mode':mode,'target_seconds':target,'lyric_lines':total,'exact_duration':False}
def section_counts(short,target_lines=None):
 total=target_lines if target_lines is not None else (4 if short else 16)
 names=('verse','chorus') if total<=8 else ('verse1','chorus1','verse2','chorus2')
 q,r=divmod(total,len(names));return {name:q+(i<r) for i,name in enumerate(names)}
def response_schema(short,target_lines=None):
 counts=section_counts(short,target_lines)
 props={k:{'type':'array','items':{'type':'string'},'minItems':n,'maxItems':n} for k,n in counts.items()}
 return {'type':'object','properties':{'title':{'type':'string'},'style':{'type':'string'},'lyrics':{'type':'object','properties':props,'required':list(counts),'additionalProperties':False}},'required':['title','style','lyrics'],'additionalProperties':False}
def compile_plan(raw,short,target_lines=None):
 counts=section_counts(short,target_lines)
 if not isinstance(raw,dict) or set(raw)!=set(SCHEMA['required']):raise ValueError('曲の企画形式が不正です。')
 parts=raw['lyrics']
 if not isinstance(parts,dict) or set(parts)!=set(counts):raise ValueError('歌詞のセクション数が不正です。')
 chunks=[]
 for key,count in counts.items():
  lines=parts[key]
  if not isinstance(lines,list) or len(lines)!=count or any(not isinstance(x,str) or not x.strip() or '\n' in x or '[' in x or ']' in x for x in lines):raise ValueError('歌詞の行数または内容が不正です。')
  chunks.append(('['+('Verse' if key.startswith('verse') else 'Chorus')+']\n')+'\n'.join(x.strip() for x in lines))
 plan=validate(dict(raw,lyrics='\n\n'.join(chunks)))
 if not re.search(r'Japanese',plan['style'],re.I):plan['style']='Japanese vocals, '+plan['style']
 return plan
def plan_song(brief,short=True,seed=831001,progress=print,duration_mode=DURATION_MODES[0],target_seconds=30):
 if not isinstance(brief,str) or not brief.strip() or len(brief)>6000:raise ValueError('日本語の指示を1〜6000文字で入力してください。')
 duration=duration_plan(short,duration_mode,target_seconds)
 base=endpoint()
 try:api(base,'/api/v1/models',timeout=5)
 except Exception:
  progress('LM Studio APIを起動しています')
  cli('server','start','--port','1234','--bind',base.split('//')[1].split(':')[0],timeout=30)
 instances=json.loads(cli('ps','--json',timeout=20))
 if any(m.get('identifier')==IDENTIFIER for m in instances):raise RuntimeError('YuE2用LLMが既に使用されています。終了後に再実行してください。')
 report={'model':MODEL,'gpu':'max','seed':seed,'duration':duration};start=time.perf_counter();owned=False
 try:
  progress('LM Studio: LLMをGPUへ読み込んでいます')
  cli('load',MODEL,'--gpu','max','--context-length','4096','--parallel','1','--ttl','300','--identifier',IDENTIFIER,'--yes');owned=True
  report['load_seconds']=time.perf_counter()-start
  progress('LM Studio: 作詞・曲調を生成しています')
  counts=section_counts(short,duration['lyric_lines'])
  length='lyricsはJSONオブジェクト。各配列の歌詞行数: '+json.dumps(counts,ensure_ascii=False)+'。配列の各要素は歌う短い言葉だけ。タグや改行を含めない。イントロ・アウトロは短い楽器演奏としてstyleだけに記述。'
  if duration['target_seconds'] is not None:
   length+=' 目標は曲全体で約'+str(duration['target_seconds'])+'秒。ノードの指定時間を本文より優先して歌詞量、テンポ、構成を調整し、styleにも英語で目標秒数を含める。'
  length+='/no_think'
  body={'model':IDENTIFIER,'messages':[{'role':'system','content':SYSTEM+'\n'+length},{'role':'user','content':brief}],'temperature':.7,'seed':seed,'max_tokens':1800,'reasoning_effort':'none','chat_template_kwargs':{'enable_thinking':False},'response_format':{'type':'json_schema','json_schema':{'name':'song_plan','strict':True,'schema':response_schema(short,duration['lyric_lines'])}}}
  t=time.perf_counter();response=api(base,'/v1/chat/completions',body);report['generation_seconds']=time.perf_counter()-t;report['usage']=response.get('usage')
  choice=response['choices'][0]
  if choice.get('finish_reason')!='stop':raise RuntimeError('作詞が途中終了しました。曲生成を開始しません。')
  plan=compile_plan(json.loads(choice['message']['content']),short,duration['lyric_lines'])
  if duration['target_seconds'] is not None:plan['style']='Target total duration approximately '+str(duration['target_seconds'])+' seconds, compact intro and outro. '+plan['style']
  return plan,report
 finally:
  if owned:
   progress('LM Studio: GPUメモリを解放しています')
   cli('unload',IDENTIFIER,timeout=60)
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('brief');p.add_argument('--output',required=True);a=p.parse_args()
 plan,report=plan_song(a.brief)
 Path(a.output).write_text(json.dumps({'plan':plan,'report':report},ensure_ascii=False,indent=2))
 print(json.dumps(plan,ensure_ascii=False))

"""Local GPU lyric/style planning for YuE2; no cloud API."""
import json, os, re, socket, struct, subprocess, time, urllib.request
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
def cli(*args,timeout=180):
 exe='/mnt/c/Users/furu/AppData/Local/Programs/LM Studio/resources/app/.webpack/lms.exe'
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
def response_schema(short):
 sections=('verse','chorus') if short else ('verse1','chorus1','verse2','chorus2')
 count=2 if short else 4
 lines={'type':'array','items':{'type':'string'},'minItems':count,'maxItems':count}
 return {'type':'object','properties':{'title':{'type':'string'},'style':{'type':'string'},'lyrics':{'type':'object','properties':{k:lines for k in sections},'required':list(sections),'additionalProperties':False}},'required':['title','style','lyrics'],'additionalProperties':False}
def compile_plan(raw,short):
 sections=response_schema(short)['properties']['lyrics']['required'];count=2 if short else 4
 if not isinstance(raw,dict) or set(raw)!=set(SCHEMA['required']):raise ValueError('曲の企画形式が不正です。')
 parts=raw['lyrics']
 if not isinstance(parts,dict) or set(parts)!=set(sections):raise ValueError('歌詞のセクション数が不正です。')
 chunks=[]
 for key in sections:
  lines=parts[key]
  if not isinstance(lines,list) or len(lines)!=count or any(not isinstance(x,str) or not x.strip() or '\n' in x or '[' in x or ']' in x for x in lines):raise ValueError('歌詞の行数または内容が不正です。')
  chunks.append(('['+('Verse' if key.startswith('verse') else 'Chorus')+']\n')+'\n'.join(x.strip() for x in lines))
 plan=dict(raw,lyrics='\n\n'.join(chunks))
 if not re.search(r'Japanese',plan['style'],re.I):plan['style']='Japanese vocals, '+plan['style']
 return validate(plan)
def plan_song(brief,short=True,seed=831001,progress=print):
 if not isinstance(brief,str) or not brief.strip() or len(brief)>6000:raise ValueError('日本語の指示を1〜6000文字で入力してください。')
 base=endpoint()
 try:api(base,'/api/v1/models',timeout=5)
 except Exception:
  progress('LM Studio APIを起動しています')
  cli('server','start','--port','1234','--bind',base.split('//')[1].split(':')[0],timeout=30)
 instances=json.loads(cli('ps','--json',timeout=20))
 if any(m.get('identifier')==IDENTIFIER for m in instances):raise RuntimeError('YuE2用LLMが既に使用されています。終了後に再実行してください。')
 report={'model':MODEL,'gpu':'max','seed':seed};start=time.perf_counter();owned=False
 try:
  progress('LM Studio: LLMをGPUへ読み込んでいます')
  cli('load',MODEL,'--gpu','max','--context-length','4096','--parallel','1','--ttl','300','--identifier',IDENTIFIER,'--yes');owned=True
  report['load_seconds']=time.perf_counter()-start
  progress('LM Studio: 作詞・曲調を生成しています')
  length='lyricsはJSONオブジェクトです。verseとchorusは各2個の短い歌詞行の配列。合計4行だけ。' if short else 'lyricsはJSONオブジェクトです。verse1、chorus1、verse2、chorus2は各4個の歌詞行の配列。合計16行。'
  length+=' 配列の各要素は歌う言葉だけ。セクションタグや改行を含めない。イントロとアウトロは短い楽器演奏としてstyleだけに記述。/no_think'
  body={'model':IDENTIFIER,'messages':[{'role':'system','content':SYSTEM+'\n'+length},{'role':'user','content':brief}],'temperature':.7,'seed':seed,'max_tokens':1800,'reasoning_effort':'none','chat_template_kwargs':{'enable_thinking':False},'response_format':{'type':'json_schema','json_schema':{'name':'song_plan','strict':True,'schema':response_schema(short)}}}
  t=time.perf_counter();response=api(base,'/v1/chat/completions',body);report['generation_seconds']=time.perf_counter()-t;report['usage']=response.get('usage')
  choice=response['choices'][0]
  if choice.get('finish_reason')!='stop':raise RuntimeError('作詞が途中終了しました。曲生成を開始しません。')
  plan=compile_plan(json.loads(choice['message']['content']),short)
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

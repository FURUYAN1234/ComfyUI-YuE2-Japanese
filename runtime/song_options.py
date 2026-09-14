"""Portable validated song presets; no application state or model calls."""
MODES=['おまかせ','プリセット','手動']
FULL_SONG='1曲（イントロ〜エンディング）'
TIMING=[FULL_SONG,'可変尺（自然な長さ）','目標尺（目安）','ぴったり尺（編集）']
VOICES={'おまかせ':'','女性・やわらかい':'soft female vocals','女性・力強い':'powerful female vocals','男性・やわらかい':'soft male vocals','男性・力強い':'powerful male vocals','中性的・透明感':'clear androgynous vocals'}
GENRES={'おまかせ':'','ポップ':'pop','ロック':'rock','アコースティック':'acoustic pop','ジャズ':'jazz pop','エレクトロ':'electronic pop','バラード':'ballad','シティポップ':'city pop','Lo-fi':'lo-fi pop','ダンス':'dance pop','オーケストラ':'orchestral pop','和風':'Japanese folk pop','子守歌':'lullaby'}
MOODS={'おまかせ':'','明るい':'bright and cheerful','切ない':'bittersweet','落ち着いた':'calm and gentle','元気':'energetic','幻想的':'dreamy','壮大':'cinematic and grand'}
INSTRUMENTS={'おまかせ':'','ピアノ中心':'piano-led arrangement','アコギ中心':'acoustic guitar-led arrangement','バンド':'electric guitar, bass and drums','シンセ中心':'synthesizers and electronic drums','弦楽器中心':'orchestral strings and piano','ジャズトリオ':'piano, upright bass and brushed drums','Lo-fiビート':'soft piano, mellow bass and dusty drums','和楽器中心':'koto, shamisen and shakuhachi'}
def settings(mode='おまかせ',voice='おまかせ',genre='おまかせ',mood='おまかせ',instruments='おまかせ',bpm=0,timing=FULL_SONG,seconds=30,use_presets=None,use_manual=None):
 if mode not in MODES or timing not in TIMING:raise ValueError('作成方法または時間モードが不正です。')
 if type(bpm) is not int or not (bpm==0 or 40<=bpm<=220):raise ValueError('BPMは0（おまかせ）または40〜220です。')
 if type(seconds) is not int or not 10<=seconds<=240:raise ValueError('秒数は10〜240の整数です。')
 if use_presets is None and use_manual is None:
  use_presets=True;use_manual=mode=='手動'
 elif type(use_presets) is not bool or type(use_manual) is not bool:
  raise ValueError('プリセットと手動入力のON/OFFは両方指定してください。')
 if not use_presets and not use_manual:
  raise ValueError('プリセットと手動入力を両方OFFにはできません。どちらかをONにしてください。')
 parts=[]
 for value,table in [(voice,VOICES),(genre,GENRES),(mood,MOODS),(instruments,INSTRUMENTS)]:
  if value not in table:raise ValueError('プリセットにない値です。')
  if table[value]:parts.append(table[value])
 if bpm:parts.append(str(bpm)+' BPM')
 if not use_presets:parts=[]
 return {'use_presets':use_presets,'use_manual':use_manual,'mode':mode,'voice':voice,'genre':genre,'mood':mood,'instruments':instruments,'bpm':bpm,'timing':timing,'seconds':seconds,'style':', '.join(parts)}
def prepare(brief,options,manual=None):
 o=settings(**{k:options[k] for k in ['mode','voice','genre','mood','instruments','bpm','timing','seconds','use_presets','use_manual'] if k in options})
 style=o['style']
 if o['use_manual']:
  if not isinstance(manual,dict):raise ValueError('手動モードでは手動歌詞ノードを接続してください。')
  lyrics=manual.get('lyrics','').strip();manual_style=manual.get('style','').strip()
  if not lyrics:raise ValueError('手動モードの歌詞が空欄です。')
  if not manual_style and not style:raise ValueError('曲調を入力するかプリセットを選んでください。')
  import re
  if not re.search(r'\[(Verse|Chorus|Intro|Bridge|Outro)[^\]]*\]',lyrics,re.I):lyrics='[Verse]\n'+lyrics
  plan={'title':manual.get('title','').strip() or '手動入力の曲','lyrics':lyrics,'style':'Japanese vocals, '+', '.join(x for x in [style,manual_style] if x)}
  return o,plan,brief
 prompt=(brief or '').strip() or '選択した設定に合う日本語の曲。歌詞もおまかせ。'
 if style:prompt+='\n選択された音楽設定（未指定項目だけ補完し、選択内容と矛盾させない）：'+style
 return o,None,prompt
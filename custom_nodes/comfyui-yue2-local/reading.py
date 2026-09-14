"""Private, persistent lyric readings. Never mutate the display lyrics."""
import json, re, os, tempfile, threading
from pathlib import Path
LOCK=threading.RLock()

def parse(text, delete=False):
    result={}
    for number,line in enumerate(text.splitlines(),1):
        line=line.strip()
        if not line: continue
        if delete:
            key=line
            value=""
        else:
            if "=" not in line: raise ValueError(f"読み修正 {number}行目: 単語=よみ の形式で入力してください。")
            key,value=(x.strip() for x in line.split("=",1))
            if not re.fullmatch(r"[ぁ-ゖァ-ヺー ・、。！？!?]+",value): raise ValueError(f"読み修正 {number}行目: 読みはひらがな・カタカナで入力してください。")
        if not key or len(key)>100 or len(value)>200 or any(c in key for c in "[]=\r\n"):
            raise ValueError(f"読み修正 {number}行目: 単語または読みが不正です。")
        if key in result: raise ValueError(f"読み修正: 単語が重複しています: {key}")
        result[key]=value
    if len(result)>5000: raise ValueError("辞書は5000件までです。")
    return result

def load(path):
    if not path.exists(): return {}
    data=json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data,dict): raise ValueError("読み辞書の形式が不正です。元ファイルを確認してください。")
    return parse("\n".join(f"{k}={v}" for k,v in data.items()))

def save(path,entries):
    path.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(prefix=".readings-",dir=path.parent)
    try:
        with os.fdopen(fd,"w",encoding="utf-8") as f:
            json.dump(entries,f,ensure_ascii=False,indent=2);f.flush();os.fsync(f.fileno())
        os.replace(name,path)
    finally:
        if os.path.exists(name): os.unlink(name)

def apply(plan_text,enabled,action,corrections,path):
    data=json.loads(plan_text)
    if not enabled: return plan_text,"OFF / 読み修正なし"
    if action not in ("今回だけ / Once","記憶・更新 / Remember","登録を削除 / Delete"):
        raise ValueError("読み修正の操作が不正です。")
    changes=parse(corrections,action=="登録を削除 / Delete")
    with LOCK:
        entries=load(path)
        if action=="登録を削除 / Delete":
            for key in changes: entries.pop(key,None)
        elif action=="記憶・更新 / Remember": entries.update(changes)
        if len(entries)>5000: raise ValueError("辞書は5000件までです。")
        if action!="今回だけ / Once" and changes: save(path,entries)
        effective={**entries,**(changes if action=="今回だけ / Once" else {})}
    original=data.get("display_lyrics",data["plan"]["lyrics"])
    pattern=re.compile("|".join(re.escape(k) for k in sorted(effective,key=len,reverse=True))) if effective else None
    applied=[]
    def replace(match):
        key=match.group();applied.append(key);return effective[key]
    sung="\n".join(line if line.lstrip().startswith("[") or not pattern else pattern.sub(replace,line) for line in original.split("\n"))
    data["display_lyrics"]=original;data["plan"]["lyrics"]=sung
    data["pronunciation"]={"applied":{k:effective[k] for k in dict.fromkeys(applied)},"singing_lyrics":sung}
    report="生成用の読み / Singing lyrics\n"+sung+"\n\n適用 / Applied\n"+"\n".join(k+"="+effective[k] for k in dict.fromkeys(applied))+"\n\n記憶済み / Remembered\n"+"\n".join(k+"="+v for k,v in entries.items())
    return json.dumps(data,ensure_ascii=False,indent=2),report

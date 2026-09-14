"""Build an editable MIDI and a simple, explicitly synthetic audition WAV."""
from pathlib import Path
import hashlib,json,shutil,subprocess,tempfile
import numpy as np
import soundfile as sf
import mido
from pykakasi import kakasi
import re
EXPORT_VERSION=2
ROOT=Path(__file__).resolve().parent

def add_lyrics(mf,lyrics):
    """Attach editable kana to the score vocal notes; alignment is approximate."""
    lines=[x.strip() for x in lyrics.splitlines() if x.strip() and not x.lstrip().startswith('[')]
    if not lines:raise ValueError('Song lyrics are missing.')
    converter=kakasi();units=[]
    for line in lines:
        kana=''.join(x['hira'] for x in converter.convert(line))
        parts=[]
        for char in kana:
            if char in 'ゃゅょぁぃぅぇぉゎ' and parts:parts[-1]+=char
            elif re.match(r'[ぁ-ゖーa-zA-Z0-9]',char):parts.append(char)
        units.extend(parts)
    if not units:raise ValueError('No readable lyric syllables.')
    # abc2midi emits the first declared score voice after the conductor track.
    track=mf.tracks[1]
    attacks=sum(msg.type=='note_on' and msg.velocity>0 for msg in track)
    if not attacks:raise ValueError('Vocal score contains no notes.')
    out=mido.MidiTrack();out.append(mido.MetaMessage('track_name',name='Vocal - editable lyrics'))
    index=0
    for msg in track:
        if msg.type=='note_on' and msg.velocity>0:
            begin=index*len(units)//attacks;end=(index+1)*len(units)//attacks
            text=''.join(units[begin:end]) or 'ー'
            out.append(mido.MetaMessage('lyrics',text=text,time=msg.time));out.append(msg.copy(time=0));index+=1
        else:out.append(msg.copy())
    mf.tracks[1]=out
    for index,other in enumerate(mf.tracks):
        if index!=1:other.insert(0,mido.MetaMessage('track_name',name='Tempo and original lyrics' if index==0 else 'Instrument '+str(index-1)))
    mf.tracks[0].insert(0,mido.MetaMessage('text',text='Lyrics alignment is approximate; edit pronunciation and note assignment.'))
    for line in reversed(lines):mf.tracks[0].insert(0,mido.MetaMessage('text',text=line))
    mf.charset='utf-8'
    return {'lyric_events':attacks,'lyric_syllables':len(units),'lyrics':lyrics,'lyric_encoding':'UTF-8','lyric_alignment':'Approximate kana allocation to vocal score notes; adjust in your singing editor.'}

def lyric_timeline(path):
    mf=mido.MidiFile(path,charset='utf-8');seconds=0.;events=[]
    # Preserve conductor tempo and vocal note-offs so rests do not hold a syllable.
    tempo=500000;active={};pending=None
    for msg in mido.merge_tracks([mf.tracks[0],mf.tracks[1]] if len(mf.tracks)>1 else mf.tracks):
        seconds+=mido.tick2second(msg.time,mf.ticks_per_beat,tempo)
        if msg.type=='set_tempo':tempo=msg.tempo
        elif msg.type=='lyrics':
            pending={'seconds':round(seconds,6),'text':msg.text};events.append(pending)
        elif msg.type=='note_on' and msg.velocity and pending is not None:
            active.setdefault((msg.channel,msg.note),[]).append(pending);pending=None
        elif msg.type=='note_off' or msg.type=='note_on' and msg.velocity==0:
            queue=active.get((msg.channel,msg.note),[])
            if queue:queue.pop(0)['end_seconds']=round(seconds,6)
    return events

def prepare(folder):
    folder=Path(folder).resolve();abc=folder/'score.abc';midi=folder/'score.mid';wav=folder/'midi_preview.wav';manifest=folder/'midi_export.json'
    digest=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    first_voice=re.search(r'(?m)^V:\s*(\S+)',abc.read_text())
    if not first_voice or first_voice.group(1).lower()!='vocal':raise ValueError('Cannot identify the first score voice as Vocal; refusing to attach lyrics to an instrumental track.')
    source_hash=digest(abc)
    plan=json.loads((folder/'song_plan.json').read_text())
    lyrics=plan['plan']['lyrics'];lyrics_hash=hashlib.sha256(lyrics.encode()).hexdigest()
    if manifest.is_file():
        old=json.loads(manifest.read_text())
        if old.get('export_version')==EXPORT_VERSION and old.get('lyrics_sha256')==lyrics_hash and old.get('score_sha256')==source_hash and all(p.is_file() and digest(p)==old.get(k) for p,k in [(midi,'midi_sha256'),(wav,'preview_sha256')]):return {**old,'lyric_timeline':lyric_timeline(midi)}
        raise RuntimeError('MIDI files changed; use a new song folder to avoid overwriting edits.')
    if midi.exists() or wav.exists():raise FileExistsError('Existing MIDI/preview has no matching export record. Move it before exporting.')
    tool=shutil.which('abc2midi') or str(ROOT/'tools/abcmidi/usr/bin/abc2midi')
    if not Path(tool).is_file():raise RuntimeError('MIDI converter missing. Rerun install.py to install MIDI tools.')
    with tempfile.TemporaryDirectory(prefix='yue2-midi-') as temp:
        temp=Path(temp);mid=temp/'score.mid';preview=temp/'midi_preview.wav'
        r=subprocess.run([tool,str(abc),'-o',str(mid)],capture_output=True,text=True,timeout=60)
        if r.returncode or re.search(r'(?im)^\s*error',r.stdout+'\n'+r.stderr):raise RuntimeError('ABC to MIDI conversion failed: '+(r.stdout+r.stderr)[-1500:])
        mf=mido.MidiFile(mid)
        lyric_report=add_lyrics(mf,lyrics);mf.save(mid)
        mf=mido.MidiFile(mid,charset='utf-8');active={};notes=[];seconds=0.
        for msg in mf:
            seconds+=msg.time
            if msg.type=='note_on' and msg.velocity:
                active.setdefault((msg.channel,msg.note),[]).append((seconds,msg.velocity))
            elif msg.type=='note_off' or msg.type=='note_on' and msg.velocity==0:
                key=(msg.channel,msg.note)
                if active.get(key):
                    start,velocity=active[key].pop(0);notes.append((start,seconds,msg.note,velocity,msg.channel))
        if any(active.values()):raise ValueError('MIDI contains unclosed notes.')
        if not notes or not 0<seconds<=1200:raise ValueError('Empty or excessively long MIDI.')
        sr=24000;audio=np.zeros(int((seconds+.5)*sr),dtype=np.float32)
        for start,end,pitch,velocity,channel in notes:
            begin=int(start*sr);n=max(1,int((end-start)*sr));t=np.arange(n,dtype=np.float32)/sr
            freq=440*2**((pitch-69)/12);signal=np.sin(2*np.pi*freq*t)+.25*np.sin(4*np.pi*freq*t)
            envelope=np.minimum(t/.01,1)*np.minimum(np.maximum((n/sr-t)/.08,0),1)*np.exp(-t*.45)
            audio[begin:begin+n]+=signal*envelope*(velocity/127)
        peak=float(np.max(np.abs(audio)))
        if not np.isfinite(audio).all() or peak<1e-6:raise ValueError('Invalid MIDI preview audio.')
        audio*=.85/peak;sf.write(preview,audio,sr,subtype='PCM_16')
        report={**lyric_report,'export_version':EXPORT_VERSION,'lyrics_sha256':lyrics_hash,'score_sha256':source_hash,'midi_sha256':digest(mid),'preview_sha256':digest(preview),'tracks':len(mf.tracks),'notes':len(notes),'seconds':seconds,'preview':'Simple synthesized audition; not the original voice or instruments.'}
        # New output files only; keep the original score and generated song intact.
        with midi.open('xb') as f:f.write(mid.read_bytes())
        with wav.open('xb') as f:f.write(preview.read_bytes())
        manifest.write_text(json.dumps(report,indent=2))
    return {**report,'lyric_timeline':lyric_timeline(midi)}
if __name__=='__main__':
    import sys
    print(json.dumps(prepare(sys.argv[1]),ensure_ascii=False))
"""Sample-exact FLAC finishing, preserving the original generated file."""
from pathlib import Path
import numpy as np
import soundfile as sf

def finish_audio(folder,mode='可変尺（自然な長さ）',seconds=30):
 folder=Path(folder); source=folder/'audio.flac'
 info=sf.info(source)
 if info.frames<info.samplerate or info.samplerate!=48000:raise ValueError('生成音声の形式が不正です。')
 if mode not in ['可変尺（自然な長さ）','目標尺（目安）','ぴったり尺（編集）']:raise ValueError('時間モードが不正です。')
 if type(seconds) is not int or not 10<=seconds<=240:raise ValueError('秒数は10〜240の整数です。')
 report={'mode':mode,'original_seconds':info.frames/info.samplerate,'output_seconds':info.frames/info.samplerate,'edited':False,'method':'none','original_file':'audio.flac'}
 if mode!='ぴったり尺（編集）':return report
 original=folder/'audio_original.flac'
 if original.exists():raise FileExistsError('元音声が既にあります。上書きしません。')
 wave,sr=sf.read(source,dtype='float32',always_2d=True)
 if not np.isfinite(wave).all():raise ValueError('音声に不正な数値があります。')
 target=seconds*sr; kept=min(len(wave),target); result=np.zeros((target,wave.shape[1]),dtype=np.float32);result[:kept]=wave[:kept]
 fade=min(sr//2,kept)
 result[kept-fade:kept]*=np.linspace(1,0,fade,dtype=np.float32)[:,None]
 temporary=folder/'audio_finished.part'
 sf.write(temporary,result,sr,format='FLAC',subtype=info.subtype)
 checked=sf.info(temporary)
 if checked.frames!=target or checked.samplerate!=sr:raise RuntimeError('仕上げ後の秒数が一致しません。')
 source.replace(original)
 try:temporary.replace(source)
 except BaseException:original.replace(source);raise
 report.update(edited=True,output_seconds=seconds,method='trim_and_fade' if info.frames>target else 'fade_and_silence_pad' if info.frames<target else 'fade_only',original_file='audio_original.flac',trimmed_seconds=max(0,info.frames-target)/sr,padded_seconds=max(0,target-info.frames)/sr,fade_seconds=fade/sr)
 return report
import importlib.util,tempfile,unittest
from pathlib import Path
import numpy as np
import soundfile as sf
ROOT=Path(__file__).resolve().parents[1]
def load(name):
 s=importlib.util.spec_from_file_location(name,ROOT/'runtime'/(name+'.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
o=load('song_options');a=load('audio_finish')
class SongFeatures(unittest.TestCase):
 def test_manual_and_presets(self):
  options=o.settings(mode='手動',voice='女性・やわらかい',instruments='ピアノ中心',timing='ぴったり尺（編集）',seconds=10)
  chosen,plan,_=o.prepare('',options,{'lyrics':'この歌を届けよう','title':'手動','style':''})
  self.assertEqual(plan['lyrics'],'[Verse]\nこの歌を届けよう');self.assertIn('female',plan['style']);self.assertIn('piano',plan['style'])
  chosen,plan,prompt=o.prepare('',o.settings(mode='プリセット',genre='ロック',bpm=120))
  self.assertIsNone(plan);self.assertIn('rock',prompt);self.assertIn('120 BPM',prompt)
  for args in [{'seconds':9},{'seconds':241},{'seconds':True},{'bpm':20},{'voice':'invalid'}]:
   with self.assertRaises(ValueError):o.settings(**args)
  with self.assertRaises(ValueError):o.prepare('',options,{'lyrics':''})
 def test_exact_trim_pad_and_original(self):
  for duration,method in [(12,'trim_and_fade'),(8,'fade_and_silence_pad'),(10,'fade_only')]:
   with tempfile.TemporaryDirectory() as t:
    p=Path(t);sr=48000;wave=(.2*np.sin(2*np.pi*440*np.arange(duration*sr)/sr)).astype('float32');sf.write(p/'audio.flac',wave,sr)
    original=(p/'audio.flac').read_bytes();report=a.finish_audio(p,'ぴったり尺（編集）',10)
    self.assertEqual(sf.info(p/'audio.flac').frames,480000);self.assertEqual(report['method'],method)
    self.assertEqual((p/'audio_original.flac').read_bytes(),original)
    final,_=sf.read(p/'audio.flac');self.assertLess(abs(final[-1]),1e-5)
    with self.assertRaises(FileExistsError):a.finish_audio(p,'ぴったり尺（編集）',10)
 def test_natural_unchanged(self):
  with tempfile.TemporaryDirectory() as t:
   p=Path(t);sf.write(p/'audio.flac',np.ones(48000)*.1,48000);original=(p/'audio.flac').read_bytes()
   r=a.finish_audio(p);self.assertFalse(r['edited']);self.assertEqual((p/'audio.flac').read_bytes(),original)
if __name__=='__main__':unittest.main()
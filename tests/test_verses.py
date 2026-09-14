import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'runtime'))
import planner,song_options
class Verses(unittest.TestCase):
 def test_structure(self):
  for n in (1,2,3):
   counts=planner.section_counts(False,full_song=True,verse_count=n)
   raw={'title':'検証','style':'Japanese pop','lyrics':{k:[k+'歌詞'+str(i) for i in range(v)] for k,v in counts.items()}}
   p=planner.compile_plan(raw,False,full_song=True,verse_count=n)
   self.assertEqual(p['lyrics'].count('[Verse]'),n)
   self.assertIn('[Outro]',p['lyrics'])
   self.assertEqual(song_options.settings(verse_count=n)['verse_count'],n)
 def test_duplicate(self):
  counts=planner.section_counts(False,full_song=True)
  raw={'title':'検証','style':'Japanese pop','lyrics':{k:[k+'歌詞'+str(i) for i in range(v)] for k,v in counts.items()}}
  raw['lyrics']['verse2'][0]=raw['lyrics']['verse1'][0]
  with self.assertRaisesRegex(ValueError,'重複'):planner.compile_plan(raw,False,full_song=True)
 def test_chorus_repeat_allowed(self):
  counts=planner.section_counts(False,full_song=True)
  raw={'title':'検証','style':'Japanese pop','lyrics':{k:[k+'歌詞'+str(i) for i in range(v)] for k,v in counts.items()}}
  raw['lyrics']['chorus2']=raw['lyrics']['chorus1'][:]
  planner.compile_plan(raw,False,full_song=True)
 def test_invalid(self):
  for n in (0,4,True):
   with self.assertRaises(ValueError):song_options.settings(verse_count=n)
if __name__=='__main__':unittest.main()
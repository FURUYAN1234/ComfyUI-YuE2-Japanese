import sys, unittest, inspect, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'runtime'))
import planner, song_options
class StandardSong(unittest.TestCase):
 def test_standard_only(self):
  self.assertEqual(planner.section_counts(False,full_song=True),planner.FULL_SECTIONS)
  self.assertNotIn('verse_count',inspect.signature(planner.plan_song).parameters)
  self.assertNotIn('verse_count',inspect.signature(song_options.settings).parameters)
  self.assertEqual(song_options.settings()['timing'],song_options.FULL_SONG)
 def test_legacy_option_cannot_change_structure(self):
  for n in (1,3):
   options=dict(song_options.settings(),verse_count=n)
   chosen,_,_=song_options.prepare('日本語の歌',options)
   self.assertNotIn('verse_count',chosen)
 def test_extra_verse_rejected(self):
  parts={k:[k+'歌詞']*(1 if k=='outro' else 2) for k in planner.FULL_SECTIONS}
  raw={'title':'検証','style':'Japanese pop','lyrics':parts}
  result=planner.compile_plan(raw,False,full_song=True)
  self.assertEqual(result['lyrics'].count('[Verse]'),2)
  parts['verse3']=['余分な番です','追加はしません']
  with self.assertRaises(ValueError):planner.compile_plan(raw,False,full_song=True)
 def test_workflow_has_no_verse_widget(self):
  w=json.loads(next((ROOT/'workflows').glob('*.json')).read_text())
  control=next(n for n in w['nodes'] if n['type']=='YuE2InputSwitches')
  self.assertEqual(len(control['widgets_values']),4)
  self.assertEqual(control['widgets_values'][2],song_options.FULL_SONG)
if __name__=='__main__':unittest.main()

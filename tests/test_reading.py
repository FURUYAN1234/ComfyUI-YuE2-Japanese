from pathlib import Path
import unittest,tempfile,json,importlib.util
p=Path(__file__).resolve().parents[1]/'custom_nodes/comfyui-yue2-local/reading.py'
s=importlib.util.spec_from_file_location('reading',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
class Readings(unittest.TestCase):
 def test_flow(self):
  with tempfile.TemporaryDirectory() as d:
   path=Path(d)/'private/readings.json'; original=json.dumps({'plan':{'lyrics':'[Verse]\n今日と今日中\n明日へ'}})
   out,_=m.apply(original,True,'記憶・更新 / Remember','今日=きょう\n今日中=きょうじゅう',path)
   data=json.loads(out);self.assertEqual(data['plan']['lyrics'],'[Verse]\nきょうときょうじゅう\n明日へ');self.assertEqual(data['display_lyrics'],'[Verse]\n今日と今日中\n明日へ')
   out,_=m.apply(original,True,'今回だけ / Once','今日=こんにち',path);self.assertIn('こんにちときょうじゅう',out);self.assertEqual(m.load(path)['今日'],'きょう')
   out,_=m.apply(original,False,'登録を削除 / Delete','今日',path);self.assertEqual(out,original);self.assertIn('今日',m.load(path))
   m.apply(original,True,'登録を削除 / Delete','今日',path);self.assertNotIn('今日',m.load(path))
   out,_=m.apply(original,True,'今回だけ / Once','',path);self.assertIn('今日ときょうじゅう',out)
 def test_invalid(self):
  for text in ['今日','今日=<script>','[Verse]=ばーす','今日=きょう\n今日=こんにち']:
   with self.assertRaises(ValueError):m.parse(text)
 def test_bad_dictionary_preserved(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'dict';p.write_text('broken')
   with self.assertRaises(ValueError):m.apply('{"plan":{"lyrics":"今日"}}',True,'記憶・更新 / Remember','今日=きょう',p)
   self.assertEqual(p.read_text(),'broken')
if __name__=='__main__':unittest.main()
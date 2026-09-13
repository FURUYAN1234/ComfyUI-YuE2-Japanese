import importlib.util,json,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('installer',ROOT/'install.py'); installer=importlib.util.module_from_spec(spec);spec.loader.exec_module(installer)
class PortableInstall(unittest.TestCase):
 def exercise(self,existing=False,custom=False):
  with tempfile.TemporaryDirectory() as t:
   root=Path(t); home=root/'reader-home'; comfy=root/'reader-comfy'; comfy.mkdir();(comfy/'main.py').write_text('')
   runtime=root/'existing-runtime' if existing else home/'.local/share/yue2'
   (runtime/'.venv/bin').mkdir(parents=True);(runtime/'.venv/bin/python').write_text('test stub')
   config=comfy/'custom_nodes/comfyui-yue2-local/local_config.json'
   if existing:
    config.parent.mkdir(parents=True);config.write_text(json.dumps({'runtime':str(runtime)}))
   target=root/'chosen-workflows' if custom else comfy/'user/default/workflows/YuE2'
   args=['install.py','--comfyui',str(comfy),'--skip-environment']
   if custom: args += ['--workflow-dir',str(target)]
   with patch('sys.argv',args),patch.object(installer.Path,'home',return_value=home),patch.object(installer,'run') as run,patch.object(installer.urllib.request,'urlopen',side_effect=URLError('test server absent')):
    installer.main()
   self.assertEqual(json.loads(config.read_text())['runtime'],str(runtime))
   self.assertTrue((target/next((ROOT/'workflows').glob('*.json')).name).is_file())
   self.assertTrue((runtime/'planner.py').is_file())
   self.assertEqual(sorted(x.name for x in (comfy/'user/default/workflows').glob('*')), [] if custom else ['YuE2'])
   self.assertEqual(run.call_count,1) # GPU validation is a mocked boundary, not a live GPU test.
 def test_fresh_reader_paths(self): self.exercise()
 def test_upgrade_preserves_runtime_and_custom_workflow_folder(self): self.exercise(existing=True,custom=True)
if __name__=='__main__':unittest.main()
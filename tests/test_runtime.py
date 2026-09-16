import importlib.util,unittest,json,ast,types,subprocess,urllib.error
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('planner',ROOT/'runtime/planner.py');planner=importlib.util.module_from_spec(spec);spec.loader.exec_module(planner)
class RuntimeContract(unittest.TestCase):
    def test_lm_studio_startup_recovery(self):
        clock=[0]
        def sleep(seconds):clock[0]+=seconds
        with patch.object(planner,'api',side_effect=[urllib.error.URLError('offline'),{'models':[]}]),patch.object(planner,'cli',side_effect=subprocess.TimeoutExpired('lms',30)) as cli,patch.object(planner.time,'monotonic',side_effect=lambda:clock[0]),patch.object(planner.time,'sleep',side_effect=sleep):
            planner.ensure_server('http://127.0.0.1:1234',lambda _:None)
        self.assertEqual(cli.call_count,1)

    def test_lm_studio_startup_stops_after_two_attempts(self):
        clock=[0]
        def sleep(seconds):clock[0]+=seconds
        with patch.object(planner,'api',side_effect=urllib.error.URLError('offline')),patch.object(planner,'cli',side_effect=subprocess.TimeoutExpired('lms',30)) as cli,patch.object(planner.time,'monotonic',side_effect=lambda:clock[0]),patch.object(planner.time,'sleep',side_effect=sleep):
            with self.assertRaisesRegex(RuntimeError,'2回'):planner.ensure_server('http://127.0.0.1:1234',lambda _:None)
        self.assertEqual(cli.call_count,2)
        self.assertEqual(clock[0],60)

    def test_lm_studio_http_error_does_not_restart(self):
        error=urllib.error.HTTPError('http://127.0.0.1:1234',401,'Unauthorized',{},None)
        with patch.object(planner,'api',side_effect=error),patch.object(planner,'cli') as cli:
            with self.assertRaises(urllib.error.HTTPError):planner.ensure_server('http://127.0.0.1:1234')
        cli.assert_not_called()

    def test_visual_lyric_sanitizing_recovers_image_text_only(self):
        source="[Bridge]\nA24えいがかメモもCC BY-SA 3.0じょうけんひょうも\n静かな歌"
        cleaned,changed=planner.sanitize_visual_lyrics(source)
        self.assertTrue(changed)
        self.assertIn("映る景色を胸に抱く",cleaned)
        self.assertIn("静かな歌",cleaned)
        self.assertNotRegex(cleaned.splitlines()[1],r"[A-Za-zＡ-Ｚａ-ｚ0-9０-９]")
        untouched,changed=planner.sanitize_visual_lyrics("[Verse]\n雨の歌")
        self.assertEqual(untouched,"[Verse]\n雨の歌");self.assertFalse(changed)

    def test_full_song_structure(self):
        d=planner.duration_plan(True,planner.FULL_SONG,30,7)
        self.assertIsNone(d['target_seconds']);self.assertTrue(d['full_song'])
        counts=planner.section_counts(True,7,True)
        raw={'title':'雨のあと','style':'Japanese pop','lyrics':{k:[k+'歌の言葉'+str(i) for i in range(1 if k=='outro' else 2)] for k in counts}}
        plan=planner.compile_plan(raw,True,7,True)
        self.assertTrue(plan['lyrics'].startswith('[Intro]'))
        self.assertIn('[Bridge]',plan['lyrics']);self.assertIn('[Outro]',plan['lyrics'])
        self.assertEqual(plan['lyrics'].count('[Chorus]'),3)
        bad={**raw,'lyrics':{k:v for k,v in raw['lyrics'].items() if k!='outro'}}
        with self.assertRaises(ValueError):planner.compile_plan(bad,True,7,True)
        raw['lyrics']['outro']=[]
        with self.assertRaises(ValueError):planner.compile_plan(raw,True,7,True)

    def test_duration_selection_and_boundaries(self):
        self.assertEqual(planner.duration_plan(True,'歌詞量で指定（従来）',30)['lyric_lines'],4)
        self.assertEqual(planner.duration_plan(False,'歌詞量で指定（従来）',30)['lyric_lines'],16)
        for mode,seconds in [('目標30秒（試験的）',30),('目標60秒（試験的）',60),('目標120秒（試験的）',120),('秒数を指定（目安）',45)]:
            plan=planner.duration_plan(True,mode,45);self.assertEqual(plan['target_seconds'],seconds)
            self.assertFalse(plan['exact_duration']);self.assertGreaterEqual(plan['lyric_lines'],2)
        for invalid in [9,241,30.5,'30',True]:
            with self.assertRaises(ValueError):planner.duration_plan(True,'秒数を指定（目安）',invalid)
        with self.assertRaises(ValueError):planner.duration_plan(True,'unknown',30)
    def test_lyric_preset_route(self):
        # Execute the real class with a capture-only parent, avoiding GPU loading.
        source=ast.parse((ROOT/'custom_nodes/comfyui-yue2-local/__init__.py').read_text())
        node=next(n for n in source.body if isinstance(n,ast.ClassDef) and n.name=='YuE2LyricPlanner')
        class Parent:
            @classmethod
            def INPUT_TYPES(cls):return {'required':{'brief':('STRING',),'seed':('INT',)},'optional':{}}
            def create(self,*args,**kwargs):return kwargs
        scope={'YuE2JapanesePlanner':Parent};exec(compile(ast.Module(body=[node],type_ignores=[]),'actual-node','exec'),scope)
        cls=scope['YuE2LyricPlanner'];choices=cls.INPUT_TYPES()['required']['lyric_length'][0]
        self.assertEqual(list(cls.LINE_PRESETS.values()),[4,8,12,16,24,32])
        self.assertEqual(choices,[*cls.LINE_PRESETS,'自由に指定'])
        for label,count in cls.LINE_PRESETS.items():
            self.assertEqual(cls().create('歌',label,7,123)['lyric_lines'],count)
        self.assertEqual(cls().create('歌','自由に指定',7,123)['lyric_lines'],7)
        with self.assertRaises(ValueError):cls().create('歌','unknown',7,123)
    def test_planner_notifications(self):
        source=ast.parse((ROOT/'custom_nodes/comfyui-yue2-local/__init__.py').read_text())
        classes=[n for n in source.body if isinstance(n,ast.ClassDef) and n.name in ('YuE2JapanesePlanner','YuE2LyricPlanner')]
        events=[]
        plan={'title':'雨','style':'Japanese pop','lyrics':'[Verse]\n雨の道'}
        def generate(*args,**kwargs):
            kwargs['progress']('LM Studio: LLMをGPUへ読み込んでいます')
            kwargs['progress']('LM Studio: 作詞・曲調を生成しています')
            kwargs['progress']('LM Studio: GPUメモリを解放しています')
            return plan,{}
        mod=types.SimpleNamespace(plan_song=generate,validate=planner.validate,duration_plan=planner.duration_plan,title_song=lambda p,s,progress:(dict(p,title='AIの曲名'),{'model':'test','llm_called':True,'title_only':True}))
        spec=importlib.util.spec_from_file_location('options',ROOT/'runtime/song_options.py');options=importlib.util.module_from_spec(spec);spec.loader.exec_module(options)
        scope={'json':json,'mm':types.SimpleNamespace(throw_exception_if_processing_interrupted=lambda:None,unload_all_models=lambda:None,soft_empty_cache=lambda:None),'ProgressBar':lambda n:types.SimpleNamespace(update_absolute=lambda *a:None),'planner_module':lambda:mod,'runtime_module':lambda n:options,'notify_planner':lambda *a:events.append(a)}
        exec(compile(ast.Module(body=classes,type_ignores=[]),'actual-planners','exec'),scope)
        node=scope['YuE2LyricPlanner']()
        node.create('雨の歌','8行',7,123,unique_id='2')
        self.assertEqual([e[1] for e in events],['running']*4+['complete'])
        self.assertTrue(all(e[0]=='2' for e in events))
        events.clear()
        def fail(*a,**k):raise RuntimeError('test failure')
        mod.plan_song=fail
        with self.assertRaises(RuntimeError):node.create('雨の歌','8行',7,123,unique_id='2')
        self.assertEqual([e[1] for e in events],['running','error'])
        events.clear()
        manual_result=json.loads(node.create('unused','8行',7,123,settings=options.settings(use_presets=False,use_manual=True),manual=plan,unique_id='2')[0])
        self.assertEqual([e[1] for e in events],['running','complete'])
        self.assertEqual(manual_result['plan']['lyrics'],plan['lyrics']);self.assertEqual(manual_result['plan']['title'],'AIの曲名')
        captured={}
        def visual_generate(brief,**kwargs):captured.update(kwargs);captured['brief']=brief;return plan,{'image_reading':'学食のオチ'}
        mod.plan_song=visual_generate
        visual_result=json.loads(node.create('ignored','8行',7,123,settings=options.settings(voice='男性・力強い',timing='ぴったり尺（編集）',use_presets=True,use_manual=True),manual=plan,visual={'enabled':True,'image_url':'data:image/jpeg;base64,test','kind':'4コマ漫画'},unique_id='2')[0])
        self.assertEqual(captured['duration_mode'],planner.FULL_SONG);self.assertEqual(captured['visual']['kind'],'4コマ漫画')
        self.assertEqual(visual_result['settings']['style'],'');self.assertFalse(visual_result['settings']['use_manual'])
        self.assertNotIn('男性・力強い',captured['brief'])
    def test_explicit_lyric_lines(self):
        for total in (1,4,7,16,64):
            d=planner.duration_plan(True,'秒数を指定（目安）',30,total)
            self.assertEqual(d['lyric_lines'],total)
            self.assertEqual(d['target_seconds'],30)
            counts=planner.section_counts(True,total)
            self.assertEqual(sum(counts.values()),total)
            self.assertTrue(all(n>0 for n in counts.values()))
            raw={'title':'検証','style':'Japanese pop','lyrics':{k:['歌の言葉']*n for k,n in counts.items()}}
            plan=planner.compile_plan(raw,True,total)
            self.assertEqual(sum(bool(x) and not x.startswith('[') for x in plan['lyrics'].splitlines()),total)
        for invalid in (0,65,True,7.5,'7'):
            with self.assertRaises(ValueError):planner.duration_plan(True,'歌詞量で指定（従来）',30,invalid)
    def test_structured_lyrics_normal_and_abnormal(self):
        raw={'title':'雨','style':'J-pop','lyrics':{'verse':['雨の道','街の灯り'],'chorus':['明日へ行こう','君と歩く']}}
        plan=planner.compile_plan(raw,True);self.assertEqual(plan['lyrics'].count('\n'),6)
        self.assertTrue(plan['style'].startswith('Japanese vocals'))
        for bad in ({'verse':['一行'],'chorus':['三行','四行']},{'verse':['一行\n二行','三行'],'chorus':['四行','五行']}):
            with self.assertRaises(ValueError):planner.compile_plan(dict(raw,lyrics=bad),True)
        for total in (2,4,6,12,24):
            counts=planner.section_counts(True,total)
            candidate=dict(raw,lyrics={k:['歌の言葉']*n for k,n in counts.items()})
            result=planner.compile_plan(candidate,True,total)
            self.assertEqual(len([l for l in result['lyrics'].splitlines() if l and not l.startswith('[')]),total)
    def test_public_validation(self):
        good={'title':'雨','style':'Japanese pop','lyrics':'[Verse]\n雨の道'}
        self.assertEqual(planner.validate(good),good)
        for bad in (dict(good,title=''),dict(good,extra='x'),dict(good,lyrics='no section'),dict(good,lyrics='[Verse]<think>x'),dict(good,style='x'*3001)):
            with self.assertRaises(ValueError):planner.validate(bad)
    def test_workflow_models_and_connection(self):
        w=json.loads(next((ROOT/'workflows').glob('*.json')).read_text());nodes={n['id']:n for n in w['nodes']}
        self.assertEqual(w['links'][0],[1,2,0,12,0,'YUE2_PLAN'])
        self.assertTrue(any(x[1:6]==[12,0,3,0,'YUE2_PLAN'] for x in w['links']))
        self.assertEqual(nodes[3]['properties']['models'],json.loads((ROOT/'models.json').read_text()))
        self.assertIsInstance(nodes[3]['widgets_values'][0],int)
        self.assertEqual(nodes[3]['widgets_values'][2:4],['YuE2-3B/model.safetensors','YuE2-Vae/model.safetensors'])
        self.assertEqual(sum(n['type']=='MarkdownNote' for n in w['nodes']),1)
        self.assertLess(nodes[1]['pos'][0]+nodes[1]['size'][0],nodes[2]['pos'][0])
if __name__=='__main__':unittest.main()

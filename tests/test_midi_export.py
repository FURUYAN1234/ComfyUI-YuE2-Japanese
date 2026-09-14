import importlib.util
import tempfile
import unittest
from pathlib import Path

class MidiLyricsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            spec=importlib.util.spec_from_file_location('yue2_midi_test',Path(__file__).resolve().parents[1]/'runtime/midi_export.py')
            cls.export=importlib.util.module_from_spec(spec);spec.loader.exec_module(cls.export)
        except ImportError as exc:raise unittest.SkipTest('Run with the isolated YuE2 Python: '+str(exc))

    def test_lyrics_roundtrip_preserves_note_timing(self):
        m=self.export.mido;mf=m.MidiFile();mf.tracks.append(m.MidiTrack());track=m.MidiTrack();mf.tracks.append(track)
        for pitch in (60,62,64):
            track.append(m.Message('note_on',note=pitch,velocity=80,time=120));track.append(m.Message('note_off',note=pitch,time=240))
        def positions(t):
            tick=0;out=[]
            for event in t:
                tick+=event.time
                if not event.is_meta:out.append((tick,event.type,event.note))
            return out
        before=positions(track);report=self.export.add_lyrics(mf,'[Verse]\nあした')
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'song.mid';mf.save(p);actual=m.MidiFile(p,charset='utf-8')
        self.assertEqual(before,positions(actual.tracks[1]))
        self.assertEqual(['あ','し','た'],[x.text for x in actual.tracks[1] if x.type=='lyrics'])
        self.assertEqual(3,report['lyric_events'])

    def test_instrumental_first_voice_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp)/'score.abc').write_text('X:1\nV: Ins\nK:C\nC4|')
            with self.assertRaisesRegex(ValueError,'Vocal'):self.export.prepare(tmp)

    def test_lyric_timeline_follows_tempo_changes(self):
        m=self.export.mido;mf=m.MidiFile(ticks_per_beat=480,charset='utf-8');t=m.MidiTrack();mf.tracks.append(t)
        t.extend([m.MetaMessage('set_tempo',tempo=500000),m.MetaMessage('lyrics',text='あ',time=480),m.MetaMessage('set_tempo',tempo=1000000),m.MetaMessage('lyrics',text='い',time=480)])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'timed.mid';mf.save(p);events=self.export.lyric_timeline(p)
        self.assertEqual(events,[{'seconds':.5,'text':'あ'},{'seconds':1.5,'text':'い'}])

    def test_empty_lyrics_are_rejected(self):
        with self.assertRaises(ValueError):self.export.add_lyrics(self.export.mido.MidiFile(),'[Intro]\n')

if __name__=='__main__':unittest.main()
import argparse, json, os, time, traceback
from pathlib import Path
p=Path(__file__).resolve().parent
parser=argparse.ArgumentParser();parser.add_argument('--request',required=True);parser.add_argument('--output',required=True);parser.add_argument('--model-dir');parser.add_argument('--vae-dir');args=parser.parse_args()
out=Path(args.output);out.mkdir(parents=True,exist_ok=False)
start=time.perf_counter()
state={'pid':os.getpid(),'started_at':time.strftime('%Y-%m-%dT%H:%M:%S%z'),'status':'starting','output':str(out)}
def save(): out.with_suffix('.state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2))
save()
try:
 import torch
 from yue2 import YuE2Pipeline
 req=json.loads(Path(args.request).read_text(encoding='utf-8-sig'))
 models={'m-a-p/YuE2-3B':args.model_dir,'m-a-p/YuE2-Vae':args.vae_dir} if args.model_dir and args.vae_dir else json.loads((p/'model_paths.json').read_text())
 state.update(status='loading',torch=torch.__version__,cuda=torch.version.cuda,gpu=torch.cuda.get_device_name());save()
 with YuE2Pipeline.from_pretrained(models['m-a-p/YuE2-3B'],vae=models['m-a-p/YuE2-Vae'],device='cuda',memory_budget_gib=14,vae_core_frames=512,offload_ar=True) as pipe:
  state['status']='generating';save()
  song=pipe(**req)
  song.save_artifacts(out)
  state.update(status='complete',truncated=song.truncated,audio_seconds=len(song.audio)/song.sample_rate,peak_allocated_gib=torch.cuda.max_memory_allocated()/2**30,peak_reserved_gib=torch.cuda.max_memory_reserved()/2**30)
except Exception as e:
 state.update(status='failed',error=str(e),traceback=traceback.format_exc());traceback.print_exc();raise
finally:
 state['elapsed_seconds']=time.perf_counter()-start;save()

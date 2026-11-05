"""Check the existing GPU installation using only workspace-local writable caches."""
import prepare_delivery as scope
import hashlib
import importlib.metadata
import json
import shutil
import sys
import psutil
import torch
import torchvision

ROOT=scope.ROOT
weight=scope.Path(r'D:\Desktop\7215\project\baseline\weights\yolov8n.pt')
expected='f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36'
if scope.sha(weight)!=expected:raise ValueError('Official initialization weight digest mismatch')
local=ROOT/'yolov8n.pt'
shutil.copy2(weight,local)
if not torch.cuda.is_available():raise RuntimeError('CUDA is unavailable')
tensor=torch.rand((128,128),device='cuda');product=tensor@tensor.T
boxes=torch.tensor([[0.,0.,10.,10.],[1.,1.,9.,9.]],device='cuda')
scores=torch.tensor([.9,.8],device='cuda')
keep=torchvision.ops.nms(boxes,scores,.5).tolist()
if keep!=[0]:raise RuntimeError('Unexpected CUDA NMS result')
properties=torch.cuda.get_device_properties(0)
info={'python':sys.version,'executable':sys.executable,'torch':torch.__version__,
      'torchvision':torchvision.__version__,'ultralytics':importlib.metadata.version('ultralytics'),
      'gpu':properties.name,'vram_GB':properties.total_memory/1024**3,
      'cuda':torch.version.cuda,'cuda_matmul_finite':bool(torch.isfinite(product).all()),
      'cuda_nms':keep,'initialization_sha256':expected,'initialization_local':str(local)}
info['available_RAM_GB']=psutil.virtual_memory().available/1024**3
scope.save(ROOT/'gpu_preflight.json',info)
print(json.dumps(info,ensure_ascii=False,indent=2),flush=True)

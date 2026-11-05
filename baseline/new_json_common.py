"""Shared scoped runtime and evidence helpers for member 04's new-JSON baseline."""
import os
from pathlib import Path
def _project_root():
    override=os.environ.get('IDAT7215_PROJECT_ROOT')
    if override:return Path(override).expanduser().resolve()
    here=Path(__file__).resolve()
    for candidate in here.parents:
        if (candidate/'run_project.py').is_file() and (candidate/'datasets/current/data.yaml').is_file():return candidate
    reference=here.with_name('project_reference.json')
    if reference.is_file():
        import json
        candidate=Path(json.loads(reference.read_text(encoding='utf-8-sig'))['project_root'])
        if (candidate/'datasets/current/data.yaml').is_file():return candidate.resolve()
    raise RuntimeError('Set IDAT7215_PROJECT_ROOT to the project root containing datasets/current/data.yaml')
ROOT=_project_root()
BASE=ROOT/'baseline'
RUNTIME=ROOT/'.runtime/new_json_baseline'
def configure():
    mapping={'TEMP':'tmp','TMP':'tmp','YOLO_CONFIG_DIR':'yolo','MPLCONFIGDIR':'mpl','TORCH_HOME':'torch','XDG_CACHE_HOME':'cache','APPDATA':'appdata','LOCALAPPDATA':'localappdata','CUDA_CACHE_PATH':'cuda','NUMBA_CACHE_DIR':'numba','USERPROFILE':'home','HF_HOME':'hf'}
    for key,folder in mapping.items():
        p=RUNTIME/folder;p.mkdir(parents=True,exist_ok=True);os.environ[key]=str(p)
    for key,value in {'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','PYTHONUNBUFFERED':'1','CUBLAS_WORKSPACE_CONFIG':':4096:8','OMP_NUM_THREADS':'4','MKL_NUM_THREADS':'4','WANDB_DISABLED':'true','YOLO_AUTOINSTALL':'false'}.items():os.environ[key]=value
configure()
import csv,hashlib,json,math
from datetime import datetime,timezone,timedelta
NAMES=['Cracking','Layer_shifting','Off_platform','Stringing','Warping']
DATA=ROOT/'datasets/current/data.yaml'
MANIFEST=ROOT/'datasets/current/frozen_split_manifest.csv'
REPORT=ROOT/'reports/new_json_20261105'
INITIAL=BASE/'weights/yolov8n.pt'
INITIAL_SHA='f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36'
SEMANTIC_SHA='ec8385ce1b86748b7a49268f160084609d4ffa1ce5f275d83711be8569afca2c'
def now():return datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds')
def load(p):return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def save(p,value):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8');temp.replace(p)
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(1048576),b''):h.update(chunk)
    return h.hexdigest()
def manifest():
    with MANIFEST.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))
def assert_dataset():
    from collections import Counter
    rows=manifest()
    assert len(rows)==1713 and Counter(r['split'] for r in rows)=={'train':1371,'val':171,'test':171}
    assert hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest()==SEMANTIC_SHA
    assert sha(INITIAL)==INITIAL_SHA,'Official initialization hash mismatch'
    for r in rows:
        assert (DATA.parent/r['image']).is_file(),r['image']
        assert sha(DATA.parent/r['label'])==r['label_sha256'],r['label']
    audit=load(REPORT/'current_data_audit.json');assert audit['status']=='passed'
    return rows

def environment():
    import sys,torch,torchvision,ultralytics,cv2,numpy,psutil
    return {'python':sys.version,'executable':sys.executable,'torch':torch.__version__,'torchvision':torchvision.__version__,'ultralytics':ultralytics.__version__,'opencv':cv2.__version__,'numpy':numpy.__version__,'cuda_runtime':torch.version.cuda,'cuda_available':torch.cuda.is_available(),'gpu':torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,'vram_bytes':torch.cuda.get_device_properties(0).total_memory if torch.cuda.is_available() else None,'available_ram_bytes':psutil.virtual_memory().available,'settings_and_caches':str(RUNTIME)}

def quiet_integrations():
    from ultralytics import settings
    settings.update({k:False for k in ['wandb','mlflow','comet','tensorboard','sync','clearml','dvc','hub'] if k in settings})



def resolve_project_path(value):
    p=Path(value)
    return p if p.is_absolute() else ROOT/p

def current_model():
    value=load(BASE/'current_model.json')
    return {**value,**{key:str(resolve_project_path(value[key])) for key in ('run_directory','best','last')}}

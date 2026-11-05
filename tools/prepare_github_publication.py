"""Prepare portable project entry points while retaining historical run artifacts."""
import os,json,re,shutil
from pathlib import Path
ROOT=Path(r'D:\Desktop\7215\project')
BACKUP=ROOT/'reports/history/before_github_20261105'
BACKUP.mkdir(parents=True,exist_ok=True)
paths=['baseline/new_json_common.py','baseline/train_baseline.py','baseline/post_training.py','baseline/build_handoff.py','baseline/finish_project.py','run_project.py','baseline/current_model.json','datasets/current/data.yaml','baseline/configs/new_json_100epochs.json','README.md']
for rel in paths:
    src=ROOT/rel;dst=BACKUP/rel;dst.parent.mkdir(parents=True,exist_ok=True)
    if src.is_file() and not dst.exists():shutil.copy2(src,dst)
p=ROOT/'baseline/new_json_common.py';text=p.read_text(encoding='utf-8-sig')
a=text.index('_default_root=');b=text.index("BASE=ROOT/'baseline'")
replacement='''def _project_root():
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
'''
text=text[:a]+replacement+text[b:]
text+='''

def resolve_project_path(value):
    p=Path(value)
    return p if p.is_absolute() else ROOT/p

def current_model():
    value=load(BASE/'current_model.json')
    return {**value,**{key:str(resolve_project_path(value[key])) for key in ('run_directory','best','last')}}
'''
p.write_text(text,encoding='utf-8')
for rel in ['baseline/post_training.py','baseline/build_handoff.py','baseline/finish_project.py']:
    p=ROOT/rel;t=p.read_text(encoding='utf-8-sig');t=t.replace("c.load(c.BASE/'current_model.json')","c.current_model()");p.write_text(t,encoding='utf-8')
p=ROOT/'run_project.py';t=p.read_text(encoding='utf-8-sig').replace("c.load(c.BASE/'current_model.json')['best']","c.current_model()['best']");p.write_text(t,encoding='utf-8')
p=ROOT/'baseline/train_baseline.py';t=p.read_text(encoding='utf-8-sig');t=t.replace("config=c.load(c.BASE/'configs/new_json_100epochs.json')", "config=c.load(c.BASE/'configs/new_json_100epochs.json')\n        config.update(data_yaml=str(c.DATA),initialization_path=str(c.INITIAL),execution_root=str(c.ROOT))")
t=t.replace("'run_directory':str(run),'best':str(run/'weights/best.pt'),'last':str(run/'weights/last.pt')", "'run_directory':run.relative_to(c.ROOT).as_posix(),'best':(run/'weights/best.pt').relative_to(c.ROOT).as_posix(),'last':(run/'weights/last.pt').relative_to(c.ROOT).as_posix()")
p.write_text(t,encoding='utf-8')
p=ROOT/'baseline/current_model.json';j=json.loads(p.read_text(encoding='utf-8-sig'))
for key in ['run_directory','best','last']:j[key]=Path(j[key]).relative_to(ROOT).as_posix()
p.write_text(json.dumps(j,indent=2),encoding='utf-8')
p=ROOT/'baseline/configs/new_json_100epochs.json';j=json.loads(p.read_text(encoding='utf-8-sig'));j.update(data_yaml='datasets/current/data.yaml',initialization_path='baseline/weights/yolov8n.pt');p.write_text(json.dumps(j,indent=2),encoding='utf-8')
for rel in ['datasets/current/data.yaml','deliverables/member04_baseline/dataset_labels/data.yaml']:
    p=ROOT/rel;t=p.read_text(encoding='utf-8-sig');t=re.sub(r'^path:.*\n','',t,count=1,flags=re.MULTILINE);p.write_text(t,encoding='utf-8')
for name in ['train_baseline.py','new_json_common.py','evaluate_baseline.py','predict_baseline.py','post_training.py','build_handoff.py','finish_project.py','convert_annotations.py','resource_preflight.py']:
    shutil.copy2(ROOT/'baseline'/name,ROOT/'deliverables/member04_baseline/code'/name)
shutil.copy2(ROOT/'run_project.py',ROOT/'deliverables/member04_baseline/code/run_project.py')
print('Portable project discovery, current model references and data YAML prepared. Frozen CSV/label bytes and trained weights unchanged.')

"""Organize receipts by owner; delete only explicitly verified source archives."""
import datetime,hashlib,json,stat
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JOURNAL=ROOT/'diagnostics/FILE_OPERATIONS_20261102.json'
AUDIT=ROOT/'diagnostics/NEW_MEMBER2_COMPARISON_20261102.json'
report=json.loads(AUDIT.read_text(encoding='utf8'))
if not report['safe_for_source_archive_cleanup']:raise RuntimeError('Source verification did not pass')
events=json.loads(JOURNAL.read_text(encoding='utf8')) if JOURNAL.exists() else []
def record(action,**kw):
    events.append({'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),'action':action,**kw})
    JOURNAL.write_text(json.dumps(events,ensure_ascii=False,indent=2),encoding='utf8')
def safe(rel):
    p=(ROOT/rel).resolve()
    if p==ROOT.resolve() or ROOT.resolve() not in p.parents:raise RuntimeError('Outside project: '+str(p))
    return p
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def move(old,new):
    src,dst=safe(old),safe(new)
    if not src.exists():
        if dst.exists() and any(e['action']=='move_completed' and e.get('source')==old and e.get('target')==new for e in events):return
        raise RuntimeError('Missing move source: '+old)
    if dst.exists():raise RuntimeError('Refuse existing move target: '+new)
    dst.parent.mkdir(parents=True,exist_ok=True)
    record('move_planned',source=old,target=new)
    src.rename(dst)
    record('move_completed',source=old,target=new)
def remove_empty(rel):
    p=safe(rel)
    if p.is_dir() and not any(p.iterdir()):p.rmdir();record('removed_empty_directory',path=rel)
record('organization_started',audit=str(AUDIT))
move('yolo/yolo','sources/member_02/yolo_dataset')
remove_empty('yolo')
move('reference_models/pre_train_model','sources/member_02/reference_models/pre_train_model')
remove_empty('reference_models')
for name in ('prepare_data','check_label','split_manifest'):
    old=name+'(1).py';new='sources/member_03/scripts/'+old
    move(old,new)
    duplicate='reference_inputs/'+name+'(1)(1).py'
    if safe(duplicate).exists():
        if digest(safe(duplicate))==digest(safe(new)):
            p=safe(duplicate);n=p.stat().st_size;h=digest(p)
            record('duplicate_delete_planned',path=duplicate,retained_path=new,sha256=h,bytes=n)
            p.unlink();record('duplicate_deleted',path=duplicate,retained_path=new,sha256=h,bytes=n)
        else:move(duplicate,'sources/member_03/scripts/'+name+'(1)(1).py')
for old,new in (
 ('reference_inputs/IDAT7215 Group Project Guidelines.pdf','sources/shared/course/Group_Project_Guidelines.pdf'),
 ('reference_inputs/IDAT7215_Topic3_八人分工与交接表(1).pdf','sources/shared/course/Topic3_Team_Handoff.pdf'),
 ('reference_inputs/List of projects -HKU (IDAT7215).pdf','sources/shared/course/Project_Topics.pdf'),
 ('GPU_MIGRATION_STATUS.md','reports/history/GPU_MIGRATION_STATUS.md'),
 ('DATA_ACCEPTANCE_20261102.md','reports/DATA_ACCEPTANCE_20261102.md'),
 ('examples','reports/examples')):move(old,new)
for p in list(safe('reference_inputs').glob('*.png')):move(p.relative_to(ROOT).as_posix(),'sources/shared/chat/'+p.name)
# Every deleted archive has a byte-identical extracted equivalent and a fresh archive digest.
for rec in report['archive_records']:
    p=safe(rec['path'])
    if not p.exists() and any(e['action']=='verified_archive_deleted' and e.get('path')==rec['path'] and e.get('sha256')==rec['sha256'] for e in events):continue
    if not p.is_file() or p.stat().st_size!=rec['bytes'] or digest(p)!=rec['sha256']:
        raise RuntimeError('Archive changed since audit: '+rec['path'])
    # Weight files were moved, so verify their retained bytes at the new location again.
    for ar in report['reference_model_archives']:
        if ar['path']==rec['path']:
            for entry in ar['entries']:
                retained=safe(entry['retained_path'].replace('reference_models/pre_train_model','sources/member_02/reference_models/pre_train_model',1))
                if digest(retained)!=entry['sha256']:raise RuntimeError('Retained reference model changed')
    if rec['type']=='member2_labels':
        for entry in json.loads(safe('diagnostics/member2_labels_extraction_manifest.json').read_text(encoding='utf8')):
            if digest(safe(entry['path']))!=entry['sha256']:raise RuntimeError('Retained label changed')
    record('verified_archive_delete_planned',**rec)
    if getattr(p.stat(),'st_file_attributes',0) & 1:
        record('readonly_attribute_cleared_for_authorized_delete',path=rec['path'])
        p.chmod(p.stat().st_mode | stat.S_IWRITE)
    p.unlink();record('verified_archive_deleted',**rec)
remove_empty('reference_inputs')
record('organization_completed',deleted_archive_bytes=sum(x['bytes'] for x in report['archive_records']))
print(json.dumps({'status':'completed','source_archives_deleted':len(report['archive_records']),'freed_archive_bytes':sum(x['bytes'] for x in report['archive_records']),'journal':str(JOURNAL)},ensure_ascii=False,indent=2))

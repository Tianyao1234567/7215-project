"""Verify member 2 receipts against member 3 delivery; preserve all source bytes."""
import collections, datetime, hashlib, json, os, stat, zipfile
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'diagnostics'
SOURCE=ROOT/'sources'
PROGRESS=OUT/'new_member2_audit_progress.json'
def save(path,obj): path.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf8')
def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def checked_path(path):
    result=path.resolve()
    if result==ROOT.resolve() or ROOT.resolve() not in result.parents: raise RuntimeError('Outside project: '+str(result))
    return result
state={'status':'running','stage':'start','checked_files':0}
def stage(text): state['stage']=text;save(PROGRESS,state)
def relative(path): return path.relative_to(ROOT).as_posix()
def extract_one(z,info,destination):
    pp=PurePosixPath(info.filename.replace('\\','/'))
    if pp.is_absolute() or '..' in pp.parts or ':' in str(pp):raise RuntimeError('Unsafe ZIP entry')
    if stat.S_ISLNK(info.external_attr>>16):raise RuntimeError('ZIP symlink')
    target=checked_path(destination.joinpath(*pp.parts))
    data=z.read(info)
    if target.exists():
        if target.read_bytes()!=data:raise RuntimeError('Refusing overwrite: '+str(target))
    else:
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    return {'source_entry':info.filename,'path':relative(target),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
try:
    manifest=json.loads((OUT/'dataset_extraction_manifest.json').read_text(encoding='utf8'))
    expected={r['path'].split('/',1)[1]:r for r in manifest}
    report={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
      'ownership_basis':'User identified labels(1).zip and root yolo directory as newly received from member 2; previous four ZIP parts as member 3 handoff.',
      'interpretation_limit':'Identical files establish no delivered annotation revisions, not absence of review work or authorship of all originals.',
      'raw_received':{},'new_member2_yolo':{},'member2_labels':{},'archive_records':[],'cache_preservation':[],'reference_model_archives':[]}
    stage('verify existing member 3 extraction')
    oldroot=ROOT/'datasets/received_20261102/dataset'
    oldbad=[]
    for key,row in expected.items():
        p=oldroot/key
        if not p.is_file():oldbad.append({'path':key,'reason':'missing'})
        elif p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:oldbad.append({'path':key,'reason':'bytes changed'})
        state['checked_files']+=1
        if state['checked_files']%100==0:save(PROGRESS,state)
    report['raw_received']={'path':relative(oldroot),'expected_files':len(expected),'mismatches':oldbad,'verified':not oldbad}
    stage('verify new member 2 yolo directory')
    newroot=ROOT/'yolo/yolo'
    newfiles={p.relative_to(newroot).as_posix():p for p in newroot.rglob('*') if p.is_file()}
    compare={'path':relative(newroot),'file_count':len(newfiles),'same_as_member3':0,'changed':[],'missing':[],'extra':[],
      'images':sum(p.suffix.lower() in {'.jpg','.jpeg','.png'} for p in newfiles.values()),
      'labels':sum(p.suffix.lower()=='.txt' for p in newfiles.values()),
      'model_weights':[k for k in newfiles if Path(k).suffix.lower() in {'.pt','.onnx','.engine','.pth'}]}
    for key,row in expected.items():
        p=newfiles.get(key)
        if p is None:compare['missing'].append(key)
        else:
            digest=sha(p)
            if digest==row['sha256']:compare['same_as_member3']+=1
            else:compare['changed'].append({'path':key,'old_sha256':row['sha256'],'new_sha256':digest})
        state['checked_files']+=1
        if state['checked_files']%100==0:save(PROGRESS,state)
    compare['extra']=sorted(set(newfiles)-set(expected))
    compare['all_images_labels_yaml_identical']=compare['same_as_member3']==len(expected) and not compare['missing'] and not compare['changed'] and set(compare['extra']) <= {'labels/train.cache','labels/val.cache'}
    report['new_member2_yolo']=compare
    stage('extract and compare new member 2 labels archive')
    labels_archive=ROOT/'labels(1).zip'
    label_rows=[]
    with zipfile.ZipFile(labels_archive) as z:
        infos=[i for i in z.infolist() if not i.is_dir()]
        if len(infos)!=len({i.filename for i in infos}):raise RuntimeError('Duplicate ZIP paths')
        for info in infos:label_rows.append(extract_one(z,info,SOURCE/'member_02/labels_received_20261102'))
    rows=[r for r in label_rows if r['source_entry'].lower().endswith('.txt')]
    comparison={'archive':'labels(1).zip','extracted_root':'sources/member_02/labels_received_20261102','files':len(label_rows),'bbox_labels':len(rows),'same_as_member3':0,'changed':[],'new_paths':[],'missing_member3_labels':[]}
    label_seen=set()
    for row in rows:
        key=row['source_entry'];label_seen.add(key)
        if key not in expected:comparison['new_paths'].append(key)
        elif expected[key]['sha256']==row['sha256']:comparison['same_as_member3']+=1
        else:comparison['changed'].append({'path':key,'member2_sha256':row['sha256'],'member3_sha256':expected[key]['sha256']})
    comparison['missing_member3_labels']=sorted(k for k in expected if k.startswith('labels/') and k.endswith('.txt') and k not in label_seen)
    comparison['all_bbox_labels_identical']=comparison['same_as_member3']==2380 and not any(comparison[k] for k in ('changed','new_paths','missing_member3_labels'))
    report['member2_labels']=comparison
    save(OUT/'member2_labels_extraction_manifest.json',label_rows)
    stage('preserve original cache files and verify archive identity')
    inventory=json.loads((OUT/'dataset_archive_inventory.json').read_text(encoding='utf8'))
    archives=sorted({r['archive'] for r in inventory['entries']})
    for archive in archives:
        ap=ROOT/archive
        report['archive_records'].append({'path':archive,'bytes':ap.stat().st_size,'sha256':sha(ap),'type':'member3_dataset_part'})
        with zipfile.ZipFile(ap) as z:
            for info in z.infolist():
                if not info.is_dir() and info.filename.endswith('.cache'):
                    report['cache_preservation'].append(extract_one(z,info,SOURCE/'member_03/original_cache_files'))
    ap=ROOT/'yolo.zip'
    report['archive_records'].append({'path':'yolo.zip','bytes':ap.stat().st_size,'sha256':sha(ap),'type':'member3_forwarded_yolo_archive'})
    # Verify the currently supplied single ZIP against the preserved member 3 files.
    single={'files':0,'same':0,'changed':[],'missing_reference':[]}
    with zipfile.ZipFile(ap) as z:
        for info in z.infolist():
            if info.is_dir():continue
            key=info.filename.replace('\\','/').split('/',1)[1]
            if key in expected:
                digest=hashlib.sha256(z.read(info)).hexdigest(); wanted=expected[key]['sha256']
            else:
                preserved=SOURCE/'member_03/original_cache_files/dataset'/key
                if not preserved.is_file():single['missing_reference'].append(key);continue
                digest=hashlib.sha256(z.read(info)).hexdigest();wanted=sha(preserved)
            single['files']+=1
            if digest==wanted:single['same']+=1
            else:single['changed'].append(key)
    single['verified']=single['files']==4763 and single['same']==4763 and not single['changed'] and not single['missing_reference']
    report['single_yolo_archive_verification']=single
    for record in report['cache_preservation']:
        key=record['source_entry'].split('/',1)[1]
        record['new_member2_yolo_cache_identical']=sha(newroot/key)==record['sha256']
    report['archive_records'].append({'path':'labels(1).zip','bytes':labels_archive.stat().st_size,'sha256':sha(labels_archive),'type':'member2_labels'})
    stage('verify existing reference weight archives')
    for rel in ('pre_train_model(1).zip','reference_inputs/pre_train_model(1)(1).zip'):
        archive=ROOT/rel
        if not archive.exists():continue
        checked=[]
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                if info.is_dir():continue
                target=ROOT/'reference_models/pre_train_model'/Path(info.filename).name
                digest=hashlib.sha256(z.read(info)).hexdigest()
                checked.append({'entry':info.filename,'retained_path':relative(target),'sha256':digest,'verified':target.is_file() and sha(target)==digest})
        record={'path':rel,'bytes':archive.stat().st_size,'sha256':sha(archive),'type':'member2_reference_models','verified':bool(checked) and all(x['verified'] for x in checked),'entries':checked}
        report['reference_model_archives'].append(record)
        report['archive_records'].append({k:record[k] for k in ('path','bytes','sha256','type')})
    report['safe_for_source_archive_cleanup']=report['raw_received']['verified'] and report['new_member2_yolo']['all_images_labels_yaml_identical'] and report['member2_labels']['all_bbox_labels_identical'] and single['verified'] and all(r['verified'] for r in report['reference_model_archives'])
    save(OUT/'NEW_MEMBER2_COMPARISON_20261102.json',report)
    state.update(status='completed',stage='completed',safe_for_source_archive_cleanup=report['safe_for_source_archive_cleanup']);save(PROGRESS,state)
    print(json.dumps({k:report[k] for k in ('raw_received','new_member2_yolo','member2_labels','single_yolo_archive_verification','safe_for_source_archive_cleanup')},ensure_ascii=False,indent=2))
except Exception as e:
    state.update(status='failed',error=str(e));save(PROGRESS,state);raise

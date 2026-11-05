"""Verify the frozen new-JSON delivery and materialize one current D-drive dataset."""
import os
from pathlib import Path
ROOT=Path(r'D:\Desktop\7215\project')
for k,v in {'TEMP':'tmp','TMP':'tmp','YOLO_CONFIG_DIR':'yolo','MPLCONFIGDIR':'mpl','TORCH_HOME':'torch','XDG_CACHE_HOME':'cache','APPDATA':'appdata','LOCALAPPDATA':'localappdata','CUDA_CACHE_PATH':'cuda','NUMBA_CACHE_DIR':'numba','USERPROFILE':'home'}.items():
    p=ROOT/'.runtime/takeover_20261105'/v;p.mkdir(parents=True,exist_ok=True);os.environ[k]=str(p)
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import csv,hashlib,json,math,re,shutil,time
from collections import Counter,defaultdict
from datetime import datetime,timezone,timedelta
from PIL import Image,ImageDraw,ImageFont
OLD=Path(r'C:\Users\Z1234\.codex\.chatgpt-projects\g-p-6aacb7113054819184d6120451354a0c\work\new_delivery_20261105_105219')
EVIDENCE=ROOT/'reports/new_json_20261105/source_evidence'
REPORT=ROOT/'reports/new_json_20261105'
CURRENT=ROOT/'datasets/current'
ANNOTATION=ROOT/'datasets/annotation_source'
QUARANTINE=ROOT/'datasets/quarantine'
NAMES=['Cracking','Layer_shifting','Off_platform','Stringing','Warping']
EXPECTED='ec8385ce1b86748b7a49268f160084609d4ffa1ce5f275d83711be8569afca2c'
START=time.time()
def save(p,obj):
    p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(obj,ensure_ascii=False,indent=2),encoding='utf-8')
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def inventory():
    totals=Counter();counts=Counter();links=[]
    for parent,dirs,files in os.walk(ROOT,followlinks=False):
        for d in list(dirs):
            p=Path(parent)/d
            if p.is_symlink() or bool(p.stat().st_file_attributes & 0x400):
                links.append(str(p));dirs.remove(d)
        for name in files:
            p=Path(parent)/name;relative=p.relative_to(ROOT);key=relative.parts[0] if len(relative.parts)>1 else '[root]'
            totals[key]+=p.stat().st_size;counts[key]+=1
    return {'logical_bytes':sum(totals.values()),'bytes_by_top_directory':dict(totals),'files_by_top_directory':dict(counts),'reparse_paths_skipped':links,'disk_free_bytes':shutil.disk_usage(ROOT).free,'note':'Logical file lengths; hardlinked directory entries can count the same disk allocation more than once.'}
def norm(s):return re.sub(r'[\s_]+','',s.strip().lower())
def canonical(boxes):return sorted(tuple([int(b[0])]+[round(float(x),6) for x in b[1:]]) for b in boxes)
def ensure_link(src,dst):
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        if not os.path.samefile(src,dst) and sha(src)!=sha(dst):raise RuntimeError(f'Existing destination differs: {dst}')
    elif src.drive.lower()==dst.drive.lower():os.link(src,dst)
    else:shutil.copy2(src,dst)
def main():
    REPORT.mkdir(parents=True,exist_ok=True)
    before=REPORT/'disk_before.json'
    if not before.exists():save(before,inventory())
    EVIDENCE.mkdir(parents=True,exist_ok=True)
    for p in OLD.iterdir():
        if p.is_file() and p.suffix.lower() in {'.json','.csv','.py','.log','.md','.jpg'}:shutil.copy2(p,EVIDENCE/p.name)
    history=ROOT/'baseline/runs/history_35epochs_20261105'
    if not history.exists():shutil.copytree(OLD/'runs/yolov8n_new_json_baseline',history)
    audit=json.loads((EVIDENCE/'NEW_DELIVERY_AUDIT.json').read_text(encoding='utf-8'))
    records=json.loads((EVIDENCE/'converted_json_records.json').read_text(encoding='utf-8'))
    manifest_path=EVIDENCE/'frozen_split_manifest.csv'
    with manifest_path.open(encoding='utf-8-sig',newline='') as f:manifest=list(csv.DictReader(f))
    semantic=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    assert semantic==EXPECTED,(semantic,'Frozen semantic manifest identity changed')
    assert Counter(r['split'] for r in manifest)=={'train':1371,'val':171,'test':171}
    assert len({r['pixel_sha256'] for r in manifest})==1713
    families=defaultdict(set)
    for r in manifest:families[r['family_id_inferred']].add(r['split'])
    assert all(len(s)==1 for s in families.values())
    selected={Path(r['source_image']).stem:r for r in manifest}
    excluded={r['stem'] for g in audit['excluded_conflicts'] for r in g['variants']}|{r['stem'] for r in audit['excluded_related']}
    assert len(excluded)==48 and len(records)==1761
    assert set(selected).isdisjoint(excluded)
    assert set(selected)|excluded=={r['stem'] for r in records}
    mapping={norm(n):i for i,n in enumerate(NAMES)}
    summary=[];new_boxes=Counter();per_split_boxes=defaultdict(Counter);image_counts=defaultdict(Counter)
    previous=json.loads((REPORT/'verified_files.json').read_text(encoding='utf-8')) if (REPORT/'verified_files.json').exists() else []
    verified_cache={r['stem']:r for r in previous}
    for idx,rec in enumerate(records,1):
        stem=rec['stem'];jpath=OLD/'received/dataset'/rec['json']
        j=json.loads(jpath.read_text(encoding='utf-8-sig'))
        assert Path(j['imagePath']).name==stem+'.jpg'
        candidates=[ROOT/'yolo/yolo'/rec['image'],ROOT/'datasets/received_20261102/dataset'/rec['image']]
        src=next((p for p in candidates if p.is_file()),OLD/'received/dataset'/rec['image'])
        cached=verified_cache.get(stem);stat=src.stat()
        actual_sha=cached['image_sha256'] if cached and cached['bytes']==stat.st_size and cached['image_mtime_ns']==stat.st_mtime_ns else sha(src)
        assert actual_sha==rec['image_sha256'],f'Source image changed: {src}'
        with Image.open(src) as image:width,height=image.size
        assert (width,height)==(j['imageWidth'],j['imageHeight'])==(3072,2048)
        boxes=[]
        for s in j['shapes']:
            assert s['shape_type']=='rectangle' and len(s['points']) in (2,4)
            cls=mapping[norm(s['label'])]
            xs=[p[0] for p in s['points']];ys=[p[1] for p in s['points']];x0,x1=min(xs),max(xs);y0,y1=min(ys),max(ys)
            if len(s['points'])==4:assert set(map(tuple,s['points']))=={(x0,y0),(x1,y0),(x1,y1),(x0,y1)}
            assert all(math.isfinite(x) for x in (x0,x1,y0,y1))
            assert 0<=x0<x1<=width and 0<=y0<y1<=height
            boxes.append([cls,(x0+x1)/(2*width),(y0+y1)/(2*height),(x1-x0)/width,(y1-y0)/height])
            new_boxes[cls]+=1
        assert boxes and len(canonical(boxes))==len(set(canonical(boxes)))
        assert canonical(boxes)==canonical(rec['boxes']),f'JSON disagrees with previous conversion: {stem}'
        annotation_out=ANNOTATION/'json'/jpath.name;annotation_out.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(jpath,annotation_out)
        text=''.join(str(int(b[0]))+' '+' '.join(f'{v:.6f}' for v in b[1:])+'\n' for b in boxes)
        if stem in selected:
            row=selected[stem];target=CURRENT/row['image'];label=CURRENT/row['label'];split=row['split']
            blob=text.encode()
            if hashlib.sha256(blob).hexdigest()!=row['label_sha256']:blob=text.replace('\n','\r\n').encode()
            assert hashlib.sha256(blob).hexdigest()==row['label_sha256'],f'Label bytes differ: {stem}'
            for cls in {b[0] for b in boxes}:image_counts[split][cls]+=1
            per_split_boxes[split].update(b[0] for b in boxes)
        else:
            target=QUARANTINE/'images'/(stem+'.jpg');label=QUARANTINE/'labels_from_json'/(stem+'.txt');split='quarantine';blob=text.replace('\n','\r\n').encode()
            ensure_link(annotation_out,QUARANTINE/'json'/jpath.name)
        ensure_link(src,target);label.parent.mkdir(parents=True,exist_ok=True);label.write_bytes(blob)
        assert os.path.samefile(src,target) or sha(target)==actual_sha
        summary.append({'stem':stem,'status':split,'image':str(target.relative_to(ROOT)),'json':str(annotation_out.relative_to(ROOT)),'image_sha256':actual_sha,'json_sha256':sha(annotation_out),'bytes':target.stat().st_size,'image_mtime_ns':target.stat().st_mtime_ns,'label_sha256':sha(label),'boxes':len(boxes)})
        if idx%250==0:print(f'AUDIT {idx}/1761 image hashes, JSON conversion and destination verified',flush=True)
    assert {NAMES[k]:v for k,v in sorted(new_boxes.items())}==audit['json_boxes_per_class']
    for split in ('train','val','test'):
        assert len(list((CURRENT/'images'/split).glob('*.jpg')))==dict(train=1371,val=171,test=171)[split]
        assert len(list((CURRENT/'labels'/split).glob('*.txt')))==dict(train=1371,val=171,test=171)[split]
        assert {NAMES[k]:v for k,v in sorted(image_counts[split].items())}==audit['images_per_class'][split]
    yaml='path: '+json.dumps(CURRENT.as_posix())+'\ntrain: images/train\nval: images/val\ntest: images/test\nnc: 5\nnames: '+json.dumps(NAMES)+'\n'
    (CURRENT/'data.yaml').write_text(yaml,encoding='utf-8')
    shutil.copy2(manifest_path,CURRENT/'frozen_split_manifest.csv')
    save(ANNOTATION/'classes.json',{str(i):n for i,n in enumerate(NAMES)})
    save(QUARANTINE/'exclusion_details.json',{'excluded_conflicts':audit['excluded_conflicts'],'excluded_related':audit['excluded_related'],'reason':'Same decoded pixels have differing JSON rectangles; all conflicting and filename-related copies excluded pending member 03 decision.'})
    save(REPORT/'verified_files.json',summary)
    # Samples are selected from train/validation only; the test set remains unused for model development.
    tiles=[];colors=['#ff4040','#42dd55','#40cfff','#ffcc33','#ee55ff']
    try:font=ImageFont.truetype('arial.ttf',15)
    except OSError:font=ImageFont.load_default()
    sample_ids=[]
    for cls in range(5):
        candidates=sorted((r for r in records if r['stem'] in selected and selected[r['stem']]['split']!='test' and cls in r['classes']),key=lambda r:r['stem'])
        for fraction in (.25,.75):
            r=candidates[int((len(candidates)-1)*fraction)];row=selected[r['stem']]
            with Image.open(CURRENT/row['image']) as im:picture=im.convert('RGB');picture.thumbnail((768,512))
            tile=Image.new('RGB',(768,550),'white');tile.paste(picture,(0,38));draw=ImageDraw.Draw(tile)
            draw.text((6,4),r['stem'],fill='black',font=font)
            w,h=picture.size
            for c,x,y,bw,bh in r['boxes']:
                c=int(c);x0=(x-bw/2)*w;y0=38+(y-bh/2)*h
                draw.rectangle((x0,y0,(x+bw/2)*w,38+(y+bh/2)*h),outline=colors[c],width=3)
                draw.text((max(0,x0),max(38,y0-17)),NAMES[c],fill=colors[c],font=font)
            tiles.append(tile);sample_ids.append({'stem':r['stem'],'split':row['split'],'class_requested':NAMES[cls]})
    sheet=Image.new('RGB',(1536,2750),'white')
    for i,t in enumerate(tiles):sheet.paste(t,((i%2)*768,(i//2)*550))
    sheet.save(REPORT/'current_ground_truth_review.jpg',quality=92)
    save(REPORT/'visual_review_samples.json',sample_ids)
    # Read the actual course PDFs with the project's existing PyMuPDF, when available.
    snapshots=json.loads((ROOT/'diagnostics/project_requirements_pdf_text.json').read_text(encoding='utf-8-sig'))
    migration=json.loads((ROOT/'diagnostics/migration_manifest.json').read_text(encoding='utf-8-sig'))['files']
    courses=[]
    for name,old_name in [('Group_Project_Guidelines.pdf','IDAT7215 Group Project Guidelines.pdf'),('Topic3_Team_Handoff.pdf','IDAT7215_Topic3_八人分工与交接表(1).pdf')]:
        p=ROOT/'sources/shared/course'/name;digest=sha(p)
        original=next(r for r in migration if Path(r['source']).name==old_name)
        assert original['sha256']==digest,'Course PDF changed since recorded extraction'
        snapshot=next(r for r in snapshots if Path(r['file']).name==old_name)
        courses.append({'path':str(p),'sha256':digest,'pages':snapshot['pages'],'read_method':'Historical full text extraction reused after SHA256 equality with the preserved original PDF was verified.'})
    save(REPORT/'course_requirements_verified.json',courses)
    result={'status':'machine_verification_passed_pending_current_visual_review','updated_China':datetime.now(timezone(timedelta(hours=8))).isoformat(),'elapsed_seconds':round(time.time()-START,1),'dataset':str(CURRENT),'source':'New member03 train JSON; previous delivered TXT rejected','images':1761,'accepted':1713,'quarantined':48,'split_counts':dict(train=1371,val=171,test=171),'class_image_counts':{s:{NAMES[k]:v for k,v in sorted(c.items())} for s,c in image_counts.items()},'box_counts_by_split':{s:{NAMES[k]:v for k,v in sorted(c.items())} for s,c in per_split_boxes.items()},'frozen_manifest_semantic_sha256':semantic,'frozen_manifest_file_sha256':sha(manifest_path),'test_used_for_training_or_selection':False,'old_val_used':False,'inferred_family_no_overlap':True,'decoded_pixel_no_overlap':True,'limitation':'Filename grouping does not establish independent print-process generalization. Historical complete image decoding reused only after source byte hashes match; JSON and YOLO conversion rechecked for all 1761 images.'}
    save(REPORT/'current_data_audit.json',result)
    print(json.dumps(result,ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:
        save(REPORT/'preparation_error.json',{'error':repr(e)});raise




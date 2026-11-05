"""Audit the new delivery, convert its JSON, and freeze a TRAIN-only 80/10/10 split."""
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parent
for key, suffix in {'TEMP':'tmp','TMP':'tmp','YOLO_CONFIG_DIR':'yolo','MPLCONFIGDIR':'mpl',
                    'TORCH_HOME':'torch','XDG_CACHE_HOME':'cache','APPDATA':'appdata',
                    'CUDA_CACHE_PATH':'cuda','NUMBA_CACHE_DIR':'numba','USERPROFILE':'home'}.items():
    directory = ROOT / '.runtime' / suffix
    directory.mkdir(parents=True, exist_ok=True)
    os.environ[key] = str(directory)
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'
os.environ['PYTHONIOENCODING'] = 'utf-8'

from collections import Counter, defaultdict
import csv
import hashlib
import json
import math
import random
import re
import sys
import time
from PIL import Image

SOURCE = ROOT / 'received/dataset'
DATASET = ROOT / 'dataset_train_only_811'
NAMES = ['Cracking','Layer_shifting','Off_platform','Stringing','Warping']
SPLITS = ('train','val','test')
STATUS = ROOT / 'preparation_status.json'
START = time.time()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def progress(phase, **details):
    state = {'status':'running','phase':phase,'elapsed_seconds':round(time.time()-START,1),**details}
    save(STATUS,state)
    print(json.dumps(state,ensure_ascii=False),flush=True)


def sha(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def key(label):
    return re.sub('[^a-z0-9]','',str(label).lower())


def canonical(boxes):
    return tuple(sorted(tuple([int(row[0])]+[round(float(v),6) for v in row[1:]]) for row in boxes))


def parse_txt(path):
    return [[float(v) for v in line.split()] for line in path.read_text(encoding='utf-8-sig').splitlines() if line.strip()]


def boxes_match(first,second):
    if len(first)!=len(second): return False
    pending=list(second)
    for row in first:
        match=next((i for i,other in enumerate(pending) if int(row[0])==int(other[0]) and
                    all(abs(a-b)<=1.000001e-6 for a,b in zip(row[1:],other[1:]))),None)
        if match is None:return False
        pending.pop(match)
    return True


def split_targets(n):
    wanted=[n*.8,n*.1,n*.1]
    targets=[int(v) for v in wanted]
    for i in sorted(range(3),key=lambda i:(-(wanted[i]-targets[i]),i))[:n-sum(targets)]:targets[i]+=1
    return targets


def assign(groups,seed=42):
    n=sum(len(v) for v in groups.values())
    targets=split_targets(n)
    totals=Counter(c for rows in groups.values() for row in rows for c in row['classes'])
    best=None
    for attempt in range(256):
        ordered=list(groups.items());random.Random(seed+attempt).shuffle(ordered)
        ordered.sort(key=lambda item:-len(item[1]))
        assigned={s:[] for s in SPLITS};counts=[0,0,0];class_counts=[Counter(),Counter(),Counter()]
        for family,rows in ordered:
            gc=Counter(c for row in rows for c in row['classes'])
            candidates=[i for i in range(3) if counts[i]+len(rows)<=targets[i]] or list(range(3))
            def score(i):
                result=0.0
                for cls,amount in gc.items():
                    desired=max(1.,totals[cls]*targets[i]/n);before=class_counts[i][cls]
                    result+=((before+amount-desired)**2-(before-desired)**2)/desired
                desired=max(1.,targets[i]);before=counts[i]
                return result+3*((before+len(rows)-desired)**2-(before-desired)**2)/desired
            i=min(candidates,key=lambda i:(score(i),i))
            counts[i]+=len(rows);class_counts[i].update(gc);assigned[SPLITS[i]].extend(rows)
        missing=sum(class_counts[i][cls]==0 for i in range(3) for cls in range(5))
        size_error=sum(abs(counts[i]-targets[i]) for i in range(3))
        class_error=sum((class_counts[i][cls]-totals[cls]*targets[i]/n)**2/max(1.,totals[cls]*targets[i]/n)
                        for i in range(3) for cls in range(5))
        rank=(missing,size_error,class_error,attempt)
        if best is None or rank<best[0]:best=(rank,assigned)
    if best[0][0] or best[0][1]:raise ValueError(f'Unable to preserve grouping and split sizes: {best[0]}')
    return best[1]


def draw_review(rows):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    chosen=[]
    for cls in range(5):
        candidates=sorted((r for r in rows if cls in r['classes']),key=lambda r:r['stem'])
        # Spread examples through the filename order instead of selecting only the first frames.
        for fraction in (.25,.75):
            row=candidates[int((len(candidates)-1)*fraction)]
            if row not in chosen:chosen.append(row)
    fig,axes=plt.subplots(5,2,figsize=(14,21))
    for ax,row in zip(axes.flat,chosen):
        with Image.open(SOURCE/row['image']) as picture:
            image=picture.convert('RGB');image.thumbnail((1024,683));w,h=image.size
            ax.imshow(image)
        for cls,x,y,bw,bh in row['boxes']:
            color=plt.cm.tab10(int(cls))
            ax.add_patch(Rectangle(((x-bw/2)*w,(y-bh/2)*h),bw*w,bh*h,fill=False,edgecolor=color,linewidth=2))
            ax.text((x-bw/2)*w,max(0,(y-bh/2)*h-3),NAMES[int(cls)],color='white',fontsize=8,
                    bbox={'facecolor':color,'alpha':.8,'pad':1})
        ax.set_title(row['stem'],fontsize=8);ax.axis('off')
    fig.suptitle('New JSON annotations converted to YOLO — TRAIN only',fontsize=14)
    fig.tight_layout(rect=(0,0,1,.98));fig.savefig(ROOT/'ground_truth_review.jpg',dpi=130);plt.close(fig)


def main():
    extraction=json.loads((ROOT/'extraction_status.json').read_text(encoding='utf-8'))
    if extraction['status']!='completed':raise ValueError('Archive extraction has not completed')
    entries=json.loads((ROOT/'extraction_manifest.json').read_text(encoding='utf-8'))
    extracted={r['path'].removeprefix('dataset/'):r for r in entries}
    images=sorted((SOURCE/'images/train').glob('*.jpg'))
    json_files=sorted((SOURCE/'images/train').glob('*.json'))
    if {p.stem for p in images}!={p.stem for p in json_files}:raise ValueError('Train JPG/JSON pairing differs')
    mapping={key(name):i for i,name in enumerate(NAMES)}
    rows=[];comparisons=[];checked=Counter();review_status=Counter()
    old_roots=[Path(r'D:\Desktop\7215\project\yolo\yolo'),
               Path(r'D:\Desktop\7215\project\datasets\received_20261102\dataset')]
    for index,image in enumerate(images,1):
        stem=image.stem;jpath=image.with_suffix('.json');j=json.loads(jpath.read_text(encoding='utf-8-sig'))
        if Path(j['imagePath']).name!=image.name:raise ValueError(f'JSON imagePath differs: {stem}')
        width,height=j['imageWidth'],j['imageHeight']
        if not isinstance(width,int) or not isinstance(height,int) or min(width,height)<=0:raise ValueError(f'Invalid JSON dimensions: {stem}')
        boxes=[]
        for shape in j['shapes']:
            if shape.get('shape_type')!='rectangle':raise ValueError(f'Unrecognized geometry: {stem}')
            cls=mapping[key(shape['label'])]
            points=shape['points'];xs=[v[0] for v in points];ys=[v[1] for v in points]
            x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
            if not all(math.isfinite(v) for v in (x0,x1,y0,y1)) or not (0<=x0<x1<=width and 0<=y0<y1<=height):raise ValueError(f'Invalid rectangle: {stem}')
            boxes.append([cls,(x0+x1)/(2*width),(y0+y1)/(2*height),(x1-x0)/width,(y1-y0)/height])
            review_status[str(shape.get('review_status'))]+=1
        if not boxes:raise ValueError(f'Unconfirmed empty annotation: {stem}')
        if len(set(canonical(boxes)))!=len(boxes):raise ValueError(f'Duplicate JSON boxes: {stem}')
        checked[str(j.get('checked'))]+=1
        relative=image.relative_to(SOURCE).as_posix()
        row={'stem':stem,'image':relative,'json':jpath.relative_to(SOURCE).as_posix(),
             'image_sha256':extracted[relative]['sha256'],'boxes':boxes,
             'classes':sorted({int(b[0]) for b in boxes}),'family':re.sub(r'_(?:original|aug)$','',stem)}
        old_label=SOURCE/'labels/train'/(stem+'.txt');export=SOURCE/'images/labels'/(stem+'.txt')
        old_boxes=parse_txt(old_label);export_boxes=parse_txt(export)
        comparison={'stem':stem,'old_labels_train_matches_json':boxes_match(old_boxes,boxes),
                    'extra_export_matches_json':boxes_match(export_boxes,boxes),'extra_export_empty':not export_boxes}
        for number,oldroot in enumerate(old_roots,1):
            comparison[f'new_json_differs_from_version_{number}']=not boxes_match(parse_txt(oldroot/'labels/train'/(stem+'.txt')),boxes)
            comparison[f'old_txt_unchanged_vs_version_{number}']=old_label.read_bytes()==(oldroot/'labels/train'/(stem+'.txt')).read_bytes()
            old_image=oldroot/'images/train'/image.name
            comparison[f'photo_unchanged_vs_version_{number}']=old_image.is_file() and sha(old_image)==row['image_sha256']
        with Image.open(image) as picture:
            picture.verify()
        with Image.open(image) as picture:
            picture.load();rgb=picture.convert('RGB')
            if rgb.size!=(width,height):raise ValueError(f'Image/JSON size differs: {stem}')
            row['pixel_sha256']=hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
        rows.append(row);comparisons.append(comparison)
        if index%250==0:progress('audit_images_and_json',checked=index,total=len(images))
    progress('group_and_freeze',checked=len(rows))
    save(ROOT/'per_image_comparison.json',comparisons)
    save(ROOT/'converted_json_records.json',rows)
    by_pixels=defaultdict(list)
    for row in rows:by_pixels[row['pixel_sha256']].append(row)
    accepted=[];conflicts=[];redundant=[]
    for digest,items in sorted(by_pixels.items()):
        if len({canonical(r['boxes']) for r in items})>1:
            conflicts.append({'pixel_sha256':digest,'variants':items});continue
        ordered=sorted(items,key=lambda r:(0 if r['stem'].endswith('_original') else 1,r['stem']))
        accepted.append(ordered[0]);redundant.extend({'omitted':r['image'],'retained':ordered[0]['image']} for r in ordered[1:])
    excluded_families={r['family'] for group in conflicts for r in group['variants']}
    related=[r for r in accepted if r['family'] in excluded_families]
    accepted=[r for r in accepted if r['family'] not in excluded_families]
    groups=defaultdict(list)
    for row in accepted:groups[row['family']].append(row)
    split=assign(groups)
    manifest=[]
    for name in SPLITS:
        (DATASET/'images'/name).mkdir(parents=True,exist_ok=True)
        (DATASET/'labels'/name).mkdir(parents=True,exist_ok=True)
        for row in sorted(split[name],key=lambda r:r['stem']):
            image_out=DATASET/'images'/name/(row['stem']+'.jpg')
            if not image_out.exists():os.link(SOURCE/row['image'],image_out)
            label_out=DATASET/'labels'/name/(row['stem']+'.txt')
            label_out.write_text(''.join(str(int(b[0]))+' '+' '.join(f'{v:.6f}' for v in b[1:])+'\n' for b in row['boxes']),encoding='utf-8')
            if not boxes_match(parse_txt(label_out),row['boxes']):raise ValueError('JSON conversion mismatch')
            row['split']=name
            manifest.append({'split':name,'image':image_out.relative_to(DATASET).as_posix(),
                             'label':label_out.relative_to(DATASET).as_posix(),'source_image':row['image'],
                             'source_json':row['json'],'family_id_inferred':row['family'],
                             'image_sha256':row['image_sha256'],'pixel_sha256':row['pixel_sha256'],
                             'label_sha256':sha(label_out),'class_ids':','.join(map(str,row['classes']))})
    with (ROOT/'frozen_split_manifest.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(manifest[0]));writer.writeheader();writer.writerows(manifest)
    yaml='path: '+json.dumps(DATASET.as_posix())+'\ntrain: images/train\nval: images/val\ntest: images/test\nnc: 5\nnames: '+json.dumps(NAMES)+'\n'
    (DATASET/'data.yaml').write_text(yaml,encoding='utf-8')
    families=defaultdict(set)
    for row in manifest:families[row['family_id_inferred']].add(row['split'])
    if any(len(v)>1 for v in families.values()):raise ValueError('Filename family crosses splits')
    if len({r['pixel_sha256'] for r in manifest})!=len(manifest):raise ValueError('Duplicate pixels in accepted dataset')
    signature=hashlib.sha256(json.dumps(manifest,sort_keys=True).encode()).hexdigest()
    totals={k:sum(bool(r[k]) for r in comparisons) for k in comparisons[0] if k!='stem'}
    report={'status':'prepared','train_images_received':len(rows),'json_files':len(json_files),
            'json_boxes_per_class':{NAMES[i]:sum(b[0]==i for r in rows for b in r['boxes']) for i in range(5)},
            'new_delivery_comparison':totals,'unique_decoded_images':len(by_pixels),
            'same_pixel_conflict_groups':len(conflicts),'consistent_duplicate_copies_omitted':len(redundant),
            'conflict_files_excluded':sum(len(g['variants']) for g in conflicts),'related_files_excluded':len(related),
            'accepted_images':len(accepted),'split_counts':{s:len(split[s]) for s in SPLITS},'seed':42,
            'images_per_class':{s:{NAMES[i]:sum(i in r['classes'] for r in split[s]) for i in range(5)} for s in SPLITS},
            'data_yaml':str(DATASET/'data.yaml'),'manifest_sha256':signature,
            'validation_from_delivery_used':False,'labels_source':'new per-image JSON; both delivered TXT locations rejected as training source',
            'group_status':'filename_original_aug_family_inferred_NOT_verified_print_process_ids',
            'metadata_checked_flags':dict(checked),'metadata_review_status':dict(review_status),
            'limitations':['Machine integrity and sampled visual review do not prove all annotations are semantically correct.',
                           'Filename-family grouping is not a verified independent-print split.',
                           'Metadata checked=false/review_status=pending do not independently prove human review.'],
            'excluded_conflicts':conflicts,'excluded_related':related,'deduplication':redundant,
            'D_project_modified':False,'formal_training_started':False}
    save(ROOT/'NEW_DELIVERY_AUDIT.json',report)
    draw_review(accepted)
    progress('completed',split_counts=report['split_counts'],accepted_images=len(accepted))
    save(STATUS,{'status':'completed','data_yaml':str(DATASET/'data.yaml'),'split_counts':report['split_counts'],
                 'elapsed_seconds':round(time.time()-START,1)})
    print(json.dumps({k:v for k,v in report.items() if k not in {'excluded_conflicts','excluded_related','deduplication'}},ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':
    try:main()
    except Exception as exc:
        save(STATUS,{'status':'failed','error':str(exc),'elapsed_seconds':round(time.time()-START,1)})
        raise

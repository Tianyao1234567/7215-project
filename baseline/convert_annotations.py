"""Reproduce the JSON-to-YOLO conversion using only the retained D-drive current data."""
import new_json_common as c
import argparse,json,math,re
from collections import Counter
from pathlib import Path
from PIL import Image

def convert(annotation,width,height):
    norm=lambda s:re.sub(r'[\s_]+','',s.strip().lower())
    mapping={norm(n):i for i,n in enumerate(c.NAMES)}
    if (annotation['imageWidth'],annotation['imageHeight'])!=(width,height):raise ValueError('JSON/image dimensions differ')
    boxes=[]
    for s in annotation['shapes']:
        if s['shape_type']!='rectangle' or len(s['points']) not in (2,4):raise ValueError('Expected two-corner or four-vertex rectangle')
        cls=mapping[norm(s['label'])];xs=[p[0] for p in s['points']];ys=[p[1] for p in s['points']]
        x0,x1,y0,y1=min(xs),max(xs),min(ys),max(ys)
        if not all(math.isfinite(v) for v in [x0,x1,y0,y1]) or not (0<=x0<x1<=width and 0<=y0<y1<=height):raise ValueError('Invalid or out-of-bounds rectangle')
        if len(s['points'])==4 and set(map(tuple,s['points']))!={(x0,y0),(x1,y0),(x1,y1),(x0,y1)}:raise ValueError('Four points do not form axis-aligned rectangle corners')
        boxes.append([cls,(x0+x1)/(2*width),(y0+y1)/(2*height),(x1-x0)/width,(y1-y0)/height])
    canonical=[(int(b[0]),*[round(v,6) for v in b[1:]]) for b in boxes]
    if not boxes or len(set(canonical))!=len(boxes):raise ValueError('Empty or duplicate rectangles')
    text=''.join(str(int(b[0]))+' '+' '.join(f'{v:.6f}' for v in b[1:])+'\r\n' for b in boxes)
    return text.encode('utf-8'),boxes

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--verify',action='store_true',help='Compare every retained label byte-for-byte without rewriting');ap.add_argument('--output-root',help='Optional new project-local directory for reproduced labels');args=ap.parse_args()
    if not args.verify and not args.output_root:ap.error('Choose --verify or --output-root')
    out=Path(args.output_root).resolve() if args.output_root else None
    if out and (not out.is_relative_to(c.ROOT) or out==c.ROOT):raise ValueError('Output must be a new directory strictly inside the project')
    if out and out.exists():raise FileExistsError('Choose a new output directory')
    rows={Path(r['source_image']).stem:r for r in c.manifest()};counts=Counter();boxes_total=Counter();index=[]
    for p in sorted((c.ROOT/'datasets/annotation_source/json').glob('*.json')):
        stem=p.stem;annotation=c.load(p)
        if Path(annotation['imagePath']).stem!=stem:raise ValueError('JSON imagePath/stem mismatch')
        if stem in rows:
            row=rows[stem];image=c.DATA.parent/row['image'];label=c.DATA.parent/row['label'];split=row['split']
        else:image=c.ROOT/'datasets/quarantine/images'/(stem+'.jpg');label=c.ROOT/'datasets/quarantine/labels_from_json'/(stem+'.txt');split='quarantine'
        with Image.open(image) as im:width,height=im.size
        blob,boxes=convert(annotation,width,height)
        if blob!=label.read_bytes():raise ValueError(f'Frozen conversion differs: {stem}')
        if out:
            dst=out/split/(stem+'.txt');dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(blob)
        counts[split]+=1;boxes_total.update(int(b[0]) for b in boxes)
        index.append({'image':stem,'split':split,'json_sha256':c.sha(p),'label_sha256':c.sha(label)})
    assert dict(counts)=={'val':171,'train':1371,'test':171,'quarantine':48} or (counts['train'],counts['val'],counts['test'],counts['quarantine'])==(1371,171,171,48)
    result={'status':'all_1761_retained_JSON_conversions_match','images_by_split':dict(counts),'boxes_by_class':{c.NAMES[k]:v for k,v in sorted(boxes_total.items())},'source_root':str(c.ROOT/'datasets/annotation_source/json'),'C_drive_dependency':False}
    if out:c.save(out/'conversion_audit.json',{**result,'files':index})
    print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()

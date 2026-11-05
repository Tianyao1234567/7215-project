"""Download and safely restore the exact 1761 images from the project GitHub release."""
import argparse,hashlib,json,os,sys,urllib.request,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def safe_target(name):
    rel=PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or any(':' in p for p in rel.parts):raise ValueError('Unsafe ZIP path')
    p=(ROOT/Path(*rel.parts)).resolve()
    if not p.is_relative_to(ROOT) or p==ROOT:raise ValueError('ZIP path escapes project')
    if not (name.startswith('datasets/current/images/') or name.startswith('datasets/quarantine/images/')):raise ValueError('Unexpected ZIP member')
    if p.suffix.lower()!='.jpg':raise ValueError('Expected JPG image')
    return p

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--verify-only',action='store_true');ap.add_argument('--keep-downloads',action='store_true');args=ap.parse_args()
    index=load(ROOT/'datasets/IMAGE_PACKAGES.json');inventory=load(ROOT/'datasets/image_inventory.json');expected={r['path']:r for r in inventory['files']}
    assert len(expected)==1761
    if args.verify_only:
        for i,(name,row) in enumerate(expected.items(),1):
            p=safe_target(name)
            if not p.is_file() or p.stat().st_size!=row['bytes'] or sha(p)!=row['sha256']:raise RuntimeError('Image missing or changed: '+name)
            if i%250==0:print(f'VERIFIED {i}/1761',flush=True)
        print('PASS: all 1761 images match the fixed delivery.');return
    cache=ROOT/'.runtime/dataset_downloads';cache.mkdir(parents=True,exist_ok=True)
    for number,asset in enumerate(index['assets'],1):
        if Path(asset['name']).name!=asset['name']:raise ValueError('Invalid asset filename')
        archive=cache/asset['name'];part=cache/(asset['name']+'.partial')
        if not archive.is_file() or archive.stat().st_size!=asset['bytes'] or sha(archive)!=asset['sha256']:
            print(f'DOWNLOAD {number}/{len(index["assets"])} {asset["name"]}',flush=True)
            request=urllib.request.Request(asset['url'],headers={'User-Agent':'IDAT7215-dataset-fetcher'})
            h=hashlib.sha256();count=0
            with urllib.request.urlopen(request,timeout=120) as src,part.open('wb') as dst:
                for block in iter(lambda:src.read(1048576),b''):h.update(block);count+=len(block);dst.write(block)
            if count!=asset['bytes'] or h.hexdigest()!=asset['sha256']:raise RuntimeError('Download checksum mismatch: '+asset['name'])
            part.replace(archive)
        with zipfile.ZipFile(archive) as z:
            if len(z.infolist())!=asset['images']:raise RuntimeError('Unexpected archive image count')
            for member in z.infolist():
                row=expected.get(member.filename)
                if row is None:raise ValueError('Unexpected image: '+member.filename)
                dst=safe_target(member.filename)
                if dst.exists():
                    if dst.stat().st_size==row['bytes'] and sha(dst)==row['sha256']:continue
                    raise FileExistsError('Existing image differs; preserve it and inspect before retrying: '+str(dst))
                dst.parent.mkdir(parents=True,exist_ok=True);temp=dst.with_name(dst.name+'.partial');h=hashlib.sha256();count=0
                with z.open(member) as src,temp.open('wb') as target:
                    for block in iter(lambda:src.read(1048576),b''):h.update(block);count+=len(block);target.write(block)
                if count!=row['bytes'] or h.hexdigest()!=row['sha256']:raise RuntimeError('Extracted image checksum differs: '+member.filename)
                temp.replace(dst)
        if not args.keep_downloads:archive.unlink()
        print('RESTORED '+asset['name'],flush=True)
    if any(not safe_target(name).is_file() for name in expected):raise RuntimeError('Images still missing')
    print('PASS: restored 1713 fixed-split images plus 48 quarantine backups; test remains unevaluated.')
if __name__=='__main__':main()

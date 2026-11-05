"""Build size-bounded image release packages, checking each original image SHA256 once."""
import os,sys,csv,json,hashlib,io,zipfile,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'baseline'))
import new_json_common as c
OUT=ROOT/'.runtime/github_publication/assets';OUT.mkdir(parents=True,exist_ok=True)
TAG='member04-baseline-20261105';BASE='https://github.com/Tianyao1234567/7215-project/releases/download/'+TAG
MAX=700*1024*1024
class HashWriter:
    def __init__(self,p):self.stream=p.open('wb');self.hash=hashlib.sha256();self.count=0
    def write(self,b):self.hash.update(b);self.count+=len(b);return self.stream.write(b)
    def tell(self):return self.count
    def seek(self,*args):raise io.UnsupportedOperation('streaming writer')
    def flush(self):self.stream.flush()
    def close(self):self.stream.close()
def digest(p):
    h=hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def main():
    raw=c.load(c.REPORT/'verified_files.json');assert len(raw)==1761
    files=[{'path':Path(r['image']).as_posix(),'bytes':r['bytes'],'sha256':r['image_sha256'],'split':r['status']} for r in raw]
    files.sort(key=lambda r:r['path'])
    index_path=ROOT/'datasets/IMAGE_PACKAGES.json'
    inventory={'images':1761,'accepted':1713,'quarantined':48,'split_counts':{'train':1371,'val':171,'test':171,'quarantine':48},'files':files}
    inventory_text=json.dumps(inventory,ensure_ascii=False,indent=2)
    inventory_hash=None
    c.save(ROOT/'datasets/image_inventory.json',inventory)
    inventory_hash=c.sha(ROOT/'datasets/image_inventory.json')
    groups=[];current=[];amount=0
    for row in files:
        if current and amount+row['bytes']>MAX:groups.append(current);current=[];amount=0
        current.append(row);amount+=row['bytes']
    if current:groups.append(current)
    previous=c.load(index_path) if index_path.exists() else {}
    previous_assets={a['name']:a for a in previous.get('assets',[])} if previous.get('image_inventory_sha256')==inventory_hash else {}
    assets=[]
    for i,group in enumerate(groups,1):
        name=f'dataset-images-{i:03d}-of-{len(groups):03d}.zip';target=OUT/name
        old=previous_assets.get(name)
        if old and target.exists() and target.stat().st_size==old['bytes'] and digest(target)==old['sha256']:
            assets.append(old);print(f'REUSED {i}/{len(groups)} {name}',flush=True);continue
        writer=HashWriter(target)
        try:
            with zipfile.ZipFile(writer,'w',compression=zipfile.ZIP_STORED,allowZip64=True) as z:
                for row in group:
                    p=ROOT/row['path'];assert p.stat().st_size==row['bytes'],str(p)
                    actual=hashlib.sha256();info=zipfile.ZipInfo(row['path'],(2026,11,5,0,0,0));info.compress_type=zipfile.ZIP_STORED
                    with p.open('rb') as src,z.open(info,'w',force_zip64=True) as dst:
                        for chunk in iter(lambda:src.read(1048576),b''):actual.update(chunk);dst.write(chunk)
                    assert actual.hexdigest()==row['sha256'],f'Image changed: {row["path"]}'
        finally:writer.close()
        item={'name':name,'url':BASE+'/'+name,'bytes':target.stat().st_size,'sha256':writer.hash.hexdigest(),'images':len(group),'uncompressed_image_bytes':sum(r['bytes'] for r in group)}
        with zipfile.ZipFile(target) as z:
            assert z.testzip() is None
            assert z.namelist()==[r['path'] for r in group]
        assets.append(item)
        c.save(OUT/'build_progress.json',{'completed':i,'total':len(groups),'assets':assets})
        print(f'PACKAGE_READY {i}/{len(groups)} {name} {item["bytes"]} bytes {len(group)} images',flush=True)
    assert sum(a['images'] for a in assets)==1761
    value={'version':1,'release_tag':TAG,'release_url':'https://github.com/Tianyao1234567/7215-project/releases/tag/'+TAG,'status':'prepared_for_upload','image_inventory_sha256':inventory_hash,'images':1761,'accepted':1713,'quarantined':48,'assets':assets,'extraction_root':'repository root','test_used':False,'notes':'Image files only. JSON, YOLO labels, frozen CSV, code and trained weights are versioned in the Git repository. All 48 excluded images are included as quarantine backups.'}
    c.save(index_path,value)
    c.save(OUT/'image_packages_prepared.json',{'status':'passed','inventory_sha256':inventory_hash,'asset_count':len(assets),'image_count':1761,'total_asset_bytes':sum(a['bytes'] for a in assets),'each_source_image_sha256_checked':True,'zip_crc_checked':True})
    print(json.dumps({k:value[k] for k in ['release_tag','images','accepted','quarantined']})+' assets='+str(len(assets)),flush=True)
if __name__=='__main__':main()


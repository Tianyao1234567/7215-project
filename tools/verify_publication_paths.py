import sys,hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'baseline'))
import new_json_common as c
p=root/'datasets/IMAGE_PACKAGES.json';j=c.load(p);j['image_inventory_sha256']=c.sha(root/'datasets/image_inventory.json');c.save(p,j)
p=root/'.runtime/github_publication/assets/image_packages_prepared.json';j=c.load(p);j['inventory_sha256']=c.sha(root/'datasets/image_inventory.json');c.save(p,j)
from ultralytics.data.utils import check_det_dataset
resolved=check_det_dataset(str(c.DATA),autodownload=False)
assert Path(resolved['path']).resolve()==c.DATA.parent.resolve(),resolved
assert Path(resolved['train']).resolve()==c.DATA.parent/'images/train'
c.assert_dataset()
assert c.sha(c.MANIFEST)=='ced1c4f7741e07be5bee21565d90fad6ffada852d0fc4a60843f19eea9124fab'
current=c.current_model();assert Path(current['best']).is_file()
model=c.load(root/'deliverables/member04_baseline/model_handoff.json')
assert c.sha(current['best'])==model['best_sha256'] and c.sha(current['last'])==model['last_sha256']
print('PASS: portable YAML resolves exact current data; split, labels and both checkpoint identities unchanged.')


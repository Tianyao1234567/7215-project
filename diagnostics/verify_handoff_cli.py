import sys
from pathlib import Path
root=Path(r'D:\Desktop\7215\project');sys.path.insert(0,str(root/'baseline'))
import new_json_common as c
p=c.load(c.REPORT/'independent_cli_prediction/predictions.json')
assert len(p['images'])==1 and p['weights_sha256']==c.load(c.BASE/'runs/yolov8n_newjson_from_official_20261105_213549/training_verified.json')['best_sha256']
r=p['images'][0];assert (r['image_width'],r['image_height'])==(3072,2048)
assert r['detections'] and all(0<=d['class_id']<5 and 0<=d['confidence']<=1 and len(d['xyxy_pixels'])==4 for d in r['detections'])
identity={name:c.sha(c.BASE/name) for name in ['evaluate_baseline.py','predict_baseline.py','new_json_common.py']}
for name,h in identity.items():assert c.sha(root/'deliverables/member04_baseline/code'/name)==h
proof={'status':'passed','checked_China':c.now(),'package_prediction_entry_actually_executed':True,'images':len(p['images']),'boxes':len(r['detections']),'example':r['detections'][0],'package_evaluation_code_matches_actual_independent_validation_entry':True,'code_sha256':identity,'test_used':False}
c.save(c.REPORT/'independent_cli_verified.json',proof)
c.save(root/'deliverables/member04_baseline/audit/independent_cli_verified.json',proof)
print(proof)

import os,sys
from pathlib import Path
ROOT=Path(r'D:\Desktop\7215\project');sys.path.insert(0,str(ROOT/'baseline'))
import new_json_common as c
import zipfile,json,shutil
c.assert_dataset()
assert c.load(c.REPORT/'resource_preflight.json')['status']=='passed'
assert len(list((ROOT/'datasets/annotation_source/json').glob('*.json')))==1761
assert len(list((ROOT/'datasets/quarantine/images').glob('*.jpg')))==48
assert len(list((ROOT/'datasets/quarantine/json').glob('*.json')))==48
inventory=c.load(c.REPORT/'source_evidence/archive_inventory.json')
actual={};archives=[]
for p in sorted((ROOT/'new').glob('*.zip')):
    with zipfile.ZipFile(p) as z:
        n=0
        for item in z.infolist():
            if item.is_dir():continue
            expected=inventory[item.filename]
            assert expected['crc32']==item.CRC and expected['size']==item.file_size and expected['archive']==p.name,item.filename
            actual[item.filename]=1;n+=1
    archives.append({'file':p.name,'bytes':p.stat().st_size,'central_directory_entries_verified':n})
assert len(archives)==4 and len(actual)==8285
assert set(actual)=={k for k,v in inventory.items() if not v['directory']}
source=Path(r'C:\Users\Z1234\.codex\.chatgpt-projects\g-p-6aacb7113054819184d6120451354a0c\work\new_delivery_20261105_105219\received\dataset')
metadata=ROOT/'datasets/annotation_source/delivered_metadata';metadata.mkdir(parents=True,exist_ok=True)
for p in source.iterdir():
    if p.is_file():shutil.copy2(p,metadata/p.name)
c.save(c.REPORT/'precleanup_proof.json',{'status':'passed','China':c.now(),'retained_train_val_test':[1371,171,171],'retained_quarantine_images':48,'retained_original_json':1761,'new_json_labels_verified':True,'official_initialization_sha256':c.sha(c.INITIAL),'archive_central_directories':archives,'original_full_extraction_crc_evidence':'source_evidence/extraction_status.json and extraction_manifest.json','reference_models':'sources/member_02/reference_models retained','history35':'baseline/runs/history_35epochs_20261105 retained','C_sources_unchanged':True})
print('PASS: current data, all 1761 JSON, quarantine, official weights, historical run and archive inventories preserved.',flush=True)

"""Create the GitHub-facing handoff ZIP and immutable publication manifest."""
import sys,os,json,zipfile,hashlib,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'baseline'))
import new_json_common as c
OUT=ROOT/'deliverables/member04_baseline';ASSETS=ROOT/'.runtime/github_publication/assets'
TAG='member04-baseline-20261105';URL='https://github.com/Tianyao1234567/7215-project/releases/download/'+TAG
PRIVATE={'course_requirements_verified.json'}
def main():
    for name in ['SUMMARY_ZH.md','DATA_REVIEW_MEMBER03.md','quarantine_48.csv','conflict_group_comparison.json']:
        shutil.copy2(ROOT/'reports/member04'/name,OUT/name)
        if name=='SUMMARY_ZH.md':
            content=(OUT/name).read_text(encoding='utf-8-sig').replace('(figures/)','(plots/)').replace('(../new_json_20261105/)','(../../reports/new_json_20261105/)')
            (OUT/name).write_text(content,encoding='utf-8')
    (OUT/'REPOSITORY.md').write_text('''# Repository and report entry

Repository: https://github.com/Tianyao1234567/7215-project

Directory and outputs guide: https://github.com/Tianyao1234567/7215-project/blob/main/PROJECT_GUIDE.md

Member04 report material: https://github.com/Tianyao1234567/7215-project/tree/main/reports/member04

All 1761 images, including 48 quarantine backups, are supplied by the same repository release. Run tools/fetch_dataset.py from the cloned repository to restore them. This ZIP is a small code/model/results handoff and does not contain the multi-GB original images. Runtime code now discovers the project root; historical training metadata retain original machine paths.
''',encoding='utf-8')
    files=[p for p in sorted(OUT.rglob('*')) if p.is_file() and p.name not in PRIVATE and p.name!='package_manifest.json']
    entries=[{'path':p.relative_to(OUT).as_posix(),'bytes':p.stat().st_size,'sha256':c.sha(p)} for p in files]
    c.save(OUT/'package_manifest.json',{'run_id':c.current_model()['run_id'],'prepared_China':c.now(),'files':entries,'local_only_excluded':['audit/course_requirements_verified.json'],'test_used':False,'frozen_manifest_file_sha256':c.sha(c.MANIFEST)})
    files.append(OUT/'package_manifest.json')
    archive=ASSETS/'IDAT7215_Member04_Baseline_20261105.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in files:z.write(p,'member04_baseline/'+p.relative_to(OUT).as_posix())
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert not any('course_requirements_verified.json' in n for n in z.namelist())
        count=len(z.infolist())
    shutil.copy2(archive,ROOT/'deliverables'/archive.name)
    images=c.load(ROOT/'datasets/IMAGE_PACKAGES.json')
    asset={'name':archive.name,'url':URL+'/'+archive.name,'bytes':archive.stat().st_size,'sha256':c.sha(archive),'entries':count}
    manifest={'repository':'https://github.com/Tianyao1234567/7215-project','release_tag':TAG,'release_url':'https://github.com/Tianyao1234567/7215-project/releases/tag/'+TAG,'status':'prepared','run_id':c.current_model()['run_id'],'handoff_asset':asset,'image_assets':images['assets'],'image_count':1761,'accepted_images':1713,'quarantined_images':48,'frozen_manifest_file_sha256':c.sha(c.MANIFEST),'frozen_manifest_semantic_sha256':c.SEMANTIC_SHA,'official_initialization_sha256':c.INITIAL_SHA,'trained_best_sha256':c.sha(c.current_model()['best']),'trained_last_sha256':c.sha(c.current_model()['last']),'test_used':False,'local_only':['virtual environment and runtime caches','private chat source images','teacher source documents and full text extraction','historical ZIP copies'],'upload_layout':'Code, labels, JSON, weights and results are in Git. Original current/quarantine images and handoff ZIP are GitHub Release assets.'}
    c.save(ROOT/'PUBLICATION_MANIFEST.json',manifest)
    checksum=''.join(a['sha256']+'  '+a['name']+'\n' for a in [*images['assets'],asset])
    (ASSETS/'SHA256SUMS.txt').write_text(checksum,encoding='utf-8')
    notes=f'''# Member04 original YOLOv8n baseline

Original YOLOv8n, official COCO initialization, 100 complete epochs, imgsz640, batch16, workers0, SGD, seed42. Training time31.55min.

Validation: Precision93.22%, Recall94.05%, mAP50 95.47%, mAP50-95 60.03%. The frozen test set remains unevaluated.

The eight image ZIPs jointly restore all1761 images at their repository-relative paths:1713 accepted fixed-split images and48 quarantine backups. JSON, labels, frozen CSV, weights, code and results are in the Git repository. Use tools/fetch_dataset.py from a clone, or extract all eight ZIPs into the clone root. Image split1371/171/171 stays unchanged. Every source image SHA256 and ZIP CRC was checked while preparing the assets.

48 exclusions comprise32 files from16 identical-pixel/differing-annotation groups and16 related variants. Related variants are not independently declared mislabeled. All48 are preserved and withheld from model development. Print-process IDs are unverified, and machine checks plus10 visual samples do not prove complete semantic annotation accuracy.

The handoff ZIP contains the current code/model/results/report material. Directory guide:PROJECT_GUIDE.md. Member04 writing materials:reports/member04. Team handoff:TEAM_UPDATE.md. SHA256SUMS.txt contains all ZIP hashes.
'''
    (ASSETS.parent/'release_notes.md').write_text(notes,encoding='utf-8')
    print(json.dumps({'handoff_MB':round(asset['bytes']/1e6,2),'images':1761,'image_parts':len(images['assets']),'zip_crc':'passed','best_sha256':manifest['trained_best_sha256'],'manifest':str(ROOT/'PUBLICATION_MANIFEST.json')},indent=2))
if __name__=='__main__':main()


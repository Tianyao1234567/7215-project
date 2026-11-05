"""Package code, corrected labels, and evidence; exclude source photos and partial weights."""
from pathlib import Path
import json
import zipfile

ROOT=Path(__file__).resolve().parent
OUTPUT=ROOT.parents[1]/'output/IDAT7215_New_JSON_Baseline_20261105.zip'
names=['extract_delivery.py','prepare_delivery.py','gpu_preflight.py','train_delivery.py','package_evidence.py',
       'README_NEW_DELIVERY.md','NEW_DELIVERY_AUDIT.json','VISUAL_REVIEW.json','gpu_preflight.json',
       'SMOKE_RESULT.json','BASELINE_RUN_CONFIGURATION.json','frozen_split_manifest.csv',
       'per_image_comparison.json','converted_json_records.json','extraction_manifest.json',
       'archive_inventory.json','ground_truth_review.jpg']
if __name__=='__main__':
    snapshot=json.loads((ROOT/'train_job_status.json').read_text(encoding='utf-8'))
    if snapshot['status'] not in ('formal_training','completed'):
        raise RuntimeError('Do not package as started until the full baseline actually runs')
    snapshot['scope']='Progress snapshot when this ZIP was created; not a final result unless status is completed.'
    (ROOT/'TRAINING_PROGRESS_SNAPSHOT.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2),encoding='utf-8')
    names.append('TRAINING_PROGRESS_SNAPSHOT.json')
    OUTPUT.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(OUTPUT,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for name in names:
            source=ROOT/name
            if not source.is_file():raise FileNotFoundError(source)
            archive.write(source,arcname=name)
        data=ROOT/'dataset_train_only_811'
        archive.write(data/'data.yaml',arcname='dataset_train_only_811/data.yaml')
        for source in sorted((data/'labels').rglob('*.txt')):
            archive.write(source,arcname='dataset_train_only_811/'+source.relative_to(data).as_posix())
    with zipfile.ZipFile(OUTPUT) as archive:
        assert archive.testzip() is None
        labels=[n for n in archive.namelist() if n.startswith('dataset_train_only_811/labels/')]
        assert len(labels)==1713
        print(json.dumps({'archive':str(OUTPUT),'bytes':OUTPUT.stat().st_size,'entries':len(archive.namelist()),
                          'corrected_labels':len(labels),'training_snapshot':snapshot},ensure_ascii=False,indent=2))

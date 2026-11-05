"""Build a reviewable member04 handoff from completed, independently checked artifacts."""
import new_json_common as c
import csv,json,os,shutil,sys
from pathlib import Path
from handoff_text import write_texts

def link_or_copy(src,dst):
    src=Path(src);dst=Path(dst);dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():
        if c.sha(src)!=c.sha(dst):shutil.copy2(src,dst)
    else:os.link(src,dst)

def main():
    pointer=c.current_model();run=Path(pointer['run_directory'])
    verified=c.load(run/'training_verified.json');assert verified['csv_rows']==100
    assert c.load(run/'post_training_verified.json')['status']=='passed'
    metrics=c.load(run/'independent_validation/validation_metrics.json');analysis=c.load(run/'validation_predictions/error_analysis.json');cleanup=c.load(c.REPORT/'cleanup_record.json')
    assert cleanup['status']=='completed' and metrics['weights_sha256']==verified['best_sha256']
    out=c.ROOT/'deliverables/member04_baseline';out.mkdir(parents=True,exist_ok=True)
    code=out/'code';code.mkdir(exist_ok=True)
    for name in ['train_baseline.py','evaluate_baseline.py','predict_baseline.py','convert_annotations.py','new_json_common.py','resource_preflight.py','post_training.py','build_handoff.py','handoff_text.py','finish_project.py','start_training.ps1']:
        shutil.copy2(c.BASE/name,code/name)
    c.save(code/'project_reference.json',{'project_root':str(c.ROOT),'override':'Set process environment IDAT7215_PROJECT_ROOT when relocating the project.'})
    for name in ['best.pt','last.pt']:link_or_copy(run/'weights'/name,out/name)
    for src,dst in [(run/'results.csv',out/'results.csv'),(run/'args.yaml',out/'config.yaml'),(run/'environment.json',out/'environment.json'),(run/'protocol.json',out/'config.json'),(run/'training.log',out/'training.log'),(run/'training_verified.json',out/'training_verified.json'),(run/'epoch_observations.json',out/'epoch_observations.json'),(c.MANIFEST,out/'split_manifest.csv'),(run/'independent_validation/validation_metrics.json',out/'validation_metrics.json')]:shutil.copy2(src,dst)
    c.save(out/'classes.json',{str(i):name for i,name in enumerate(c.NAMES)})
    link_or_copy(c.INITIAL,out/'initialization/yolov8n.pt')
    c.save(out/'initialization/source.json',{'url':'https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt','sha256':c.INITIAL_SHA,'purpose':'Official COCO initialization only; distinct from the trained best and last weights.'})
    for row in c.manifest():
        dest=out/'dataset_labels'/row['label'];dest.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(c.DATA.parent/row['label'],dest)
    shutil.copy2(c.DATA,out/'dataset_labels/data.yaml')
    plot_root=out/'plots';plot_root.mkdir(exist_ok=True)
    for prefix,folder in [('training',run),('validation',run/'independent_validation')]:
        for p in folder.iterdir():
            if p.is_file() and p.suffix.lower() in {'.png','.jpg'}:link_or_copy(p,plot_root/(prefix+'_'+p.name))
    pred=out/'predictions';pred.mkdir(exist_ok=True)
    for p in (run/'validation_predictions').iterdir():
        if p.is_file():link_or_copy(p,pred/p.name)
    evidence=out/'audit';evidence.mkdir(exist_ok=True)
    for name in ['current_data_audit.json','verified_files.json','visual_review_samples.json','current_ground_truth_review.jpg','resource_preflight.json','cleanup_record.json','precleanup_proof.json','course_requirements_verified.json','disk_before.json','gpu_observation.json','visible_terminal_verification.json','data_tool_regression.log']:
        shutil.copy2(c.REPORT/name,evidence/name)
    for name in ['NEW_DELIVERY_AUDIT.json','extraction_status.json','archive_inventory.json','per_image_comparison.json']:
        shutil.copy2(c.REPORT/'source_evidence'/name,evidence/name)
    c.save(out/'dataset_reference.json',{'dataset_root':str(c.DATA.parent),'data_yaml':str(c.DATA),'annotation_source':str(c.ROOT/'datasets/annotation_source/json'),'quarantine':str(c.ROOT/'datasets/quarantine'),'split_counts':{'train':1371,'val':171,'test':171},'manifest_csv_sha256':c.sha(c.MANIFEST),'manifest_semantic_sha256':c.SEMANTIC_SHA,'images_included_in_package':False,'instructions':'Images remain in the sole current project dataset. Keep this split unchanged when transferring them. Test is withheld.'})
    shutil.copy2(c.ROOT/'environment/SETUP.md',out/'environment_setup.md')
    import importlib.metadata as metadata
    requirements=[]
    for name in ['torch','torchvision','ultralytics','numpy','opencv-python','matplotlib','Pillow','psutil','PyYAML']:
        requirements.append(name+'=='+metadata.version(name))
    (out/'requirements.txt').write_text('\n'.join(requirements)+'\n',encoding='utf-8')
    c.save(out/'model_handoff.json',{'run_id':run.name,'status':'training_validation_predictions_verified','initialization':'official COCO YOLOv8n','initialization_sha256':c.INITIAL_SHA,'best_file':'best.pt','last_file':'last.pt','best_sha256':verified['best_sha256'],'last_sha256':verified['last_sha256'],'epochs':100,'training_seconds':verified['training_seconds'],'batch':16,'workers':0,'imgsz':640,'original_run':str(run),'dataset':str(c.DATA),'manifest_file_sha256':c.sha(c.MANIFEST),'manifest_semantic_sha256':c.SEMANTIC_SHA,'classes':c.NAMES,'validation':metrics,'test_used':False,'speed_benchmark_completed':False,'deployment_export_completed':False,'parameter_count_unfused':analysis['model_info']['unfused_parameters'],'weights_link_note':'best.pt and last.pt are NTFS hardlinks to preserved run weights. Treat them as immutable.'})
    word_counts=write_texts(out,run,metrics,analysis,verified,cleanup)
    sample=next(e for e in analysis['examples'] if e['kind']=='class_representative')
    sample_path=c.DATA.parent/'images/val'/(sample['image_id']+'.jpg')
    python=c.ROOT/'environment/.venv_gpu/Scripts/python.exe'
    readme=f'''# Member 04 original YOLOv8n baseline

Run {run.name} completed 100 epochs from official COCO weights, and best.pt was reloaded for independent validation and prediction. No frozen test evaluation was performed. model_handoff.json, validation_metrics.json and results.csv are the machine-readable result records.

## Start here

This package contains the trained best.pt and last.pt, code, exact configuration, environment versions, frozen split, complete training log, curves, representative predictions and report material. All 1713 converted YOLO labels are included in dataset_labels/labels, and official initialization weights with provenance are in initialization. Multi-GB source images remain at {c.DATA.parent}. All 1761 original JSON remain at {c.ROOT/'datasets/annotation_source/json'}, and all 48 excluded images with their JSON remain at {c.ROOT/'datasets/quarantine'}.

The authoritative project is {c.ROOT}. Open PowerShell there and use its verified interpreter. The existing .venv_gpu reuses the machine's installed GPU PyTorch and is not a portable environment. requirements.txt records versions, and {c.ROOT/'environment/SETUP.md'} documents the existing GPU setup. No global Python, driver or BIOS changes were made.

## Independent evaluation for member 06

```powershell
Set-Location -LiteralPath '{c.ROOT}'
& '{python}' -B '.\\deliverables\\member04_baseline\\code\\evaluate_baseline.py' --weights '.\\deliverables\\member04_baseline\\best.pt' --split val --output ('.\\baseline\\runs\\validation_check_'+(Get-Date -Format yyyyMMdd_HHmmss))
```

The code snapshot uses code/project_reference.json to find the existing project dataset. On another machine set $env:IDAT7215_PROJECT_ROOT to the relocated project root and update datasets/current/data.yaml's path. Transfer the current images with the supplied split manifest, and place dataset_labels/labels under the relocated datasets/current folder. Put initialization/yolov8n.pt under baseline/weights when recreating the project structure. The test entry requires the explicit --split test --final-test flags. Use it only after model and protocol freeze under member06's final evaluation plan, without selecting settings from test results.

## Image inference for member 07

```powershell
Set-Location -LiteralPath '{c.ROOT}'
& '{python}' -B '.\\deliverables\\member04_baseline\\code\\predict_baseline.py' --weights '.\\deliverables\\member04_baseline\\best.pt' --source '{sample_path}' --conf 0.25 --output ('.\\baseline\\runs\\prediction_check_'+(Get-Date -Format yyyyMMdd_HHmmss))
```

predictions.json reports class_id, class_name, confidence and xyxy_pixels on the original image. The four coordinates are x1, y1, x2, y2, in pixels, not normalized centre coordinates. conf 0.25 is an illustration threshold and is not the validation AP collection threshold. The saved prediction images label class and confidence. The five classes use IDs 0 through 4 in classes.json.

## Fresh 100-epoch reproduction

```powershell
Set-Location -LiteralPath '{c.ROOT}'
.\\baseline\\start_training.ps1
```

This opens a new run through the current visible terminal and uses official baseline/weights/yolov8n.pt with resume=False, 100 epochs and patience=0. Never initialize a new baseline from this package's trained best.pt. The final protocol is config.json, and config.yaml captures the full framework arguments. Batch16 and workers0 passed the real-data resource check. The framework warns that RAM caching with deterministic=True does not guarantee bitwise-identical runs. Member05 should use the same fixed split, image size and experiment budget for the intended comparison. This user-authorized protocol is supplied for team alignment and does not claim a completed team agreement.

## Evidence and materials

- results.csv, training.log and training_verified.json verify epochs 1 through 100 and contain no nonfinite numeric values.
- plots contains the training curves, validation PR/confidence curves and confusion matrices. Raw run files remain at {run}.
- predictions contains all 171 validation-image JSON outputs, class representatives and available error examples. error_analysis.json documents fixed-confidence matching and links each example to its image ID.
- audit records the data conversion, source comparisons, source ZIP metadata, sample review, resource check and actual cleanup.
- baseline_method_300words.md contains approximately 300 method words. personal_contribution.md contains {word_counts['contribution_words']} words for Tianyao Zhang to verify. baseline_report.md includes results, figure captions and references. presentation_notes.md and member04_baseline_slides.pptx supply two slides for member08.

## Limits and ownership

Only the revised train JSON supplied the current labels. The former 619-image validation split was not used. The frozen 1371/171/171 split has no exact decoded duplicate or inferred original/augmented family across sets. Verified printing-process IDs remain unavailable, so adjacent frames may still create dependence. Off_platform has nine validation objects. Format checks and ten visual examples do not establish complete semantic annotation correctness, normal-only false-alarm performance, or independent-print generalization.

Member03 still needs to resolve 16 inconsistent same-pixel groups and supply true object/batch/process identifiers. The complete exclusion records remain in audit/NEW_DELIVERY_AUDIT.json and the project quarantine folder. Full photo re-upload is unnecessary for these decisions.

Ultralytics provides the original model, training engine, losses, augmentation, validation metrics and built-in plots. The project wrappers, JSON conversion, audit, data materialization and handoff packaging are project-specific and used AI assistance. Member05 owns the lightweight head, member06 unified evaluation and timing, member07 the demo, and member08 the assembled report. No member messages were sent. GPU power, a unified FPS benchmark and deployment export were not measured or claimed.

## Disk cleanup

The project initially contained {c.load(c.REPORT/'disk_before.json')['logical_bytes']/1e9:.2f} GB of logical file lengths. The recorded cleanup increased available disk space by {cleanup['observed_free_bytes_increase']/1e9:.2f} GB. Logical path totals can count hardlinks more than once and differ from physical allocation. cleanup_record.json lists each actual deletion and all retained categories. C-drive historical files were left unchanged. A final project size snapshot is saved separately after all outputs are complete.
'''
    readme+='''
## Recreating the required directories on another computer

Use a compatible Python 3.10 GPU environment with the recorded versions, set IDAT7215_PROJECT_ROOT to the new project root, and use that environment's Python. environment_setup.md describes this computer's setup for reference; its absolute base-Python path and .venv_gpu are not portable.

Copy code/*.py to the new baseline folder, except run_project.py which belongs at the project root. Copy start_training.ps1 to baseline. Copy config.json to baseline/configs/new_json_100epochs.json, official initialization/yolov8n.pt to baseline/weights/yolov8n.pt, and split_manifest.csv to datasets/current/frozen_split_manifest.csv. Copy dataset_labels/labels into datasets/current/labels and preserve the train/val/test subfolders. Copy audit/current_data_audit.json to reports/new_json_20261105/current_data_audit.json so the evaluator can verify its observed class counts.

Transfer the matching current images separately into datasets/current/images/train, val and test. Create datasets/current/data.yaml using the supplied dataset_labels/data.yaml with its path updated to the new datasets/current location. The names, splits and all label bytes stay unchanged. Update config.json's data_yaml and initialization_path when placing the relocated configuration, while retaining its training settings and identity hashes.

For evaluation and inference, use the packaged best.pt. For fresh training, use the official initialization checkpoint. The JSON conversion verification command additionally needs the original datasets/annotation_source/json and datasets/quarantine retained in the full source project. This small package supplies the frozen training labels but does not duplicate the full original photo and annotation-source folders.
'''
    (out/'README.md').write_text(readme,encoding='utf-8')
    pending=c.load(c.REPORT/'source_evidence/NEW_DELIVERY_AUDIT.json')
    lines=['# Questions for member 03','', 'Resolve these 16 groups of identical decoded images with different JSON rectangles. All 32 copies and 16 filename-related images remain excluded. Supply authoritative corrected annotations and actual print-object/batch/process IDs. Do not delete or average alternative rectangles.','']
    for i,g in enumerate(pending['excluded_conflicts'],1):lines.append(str(i)+'. '+', '.join(r['stem'] for r in g['variants']))
    (out/'member03_pending.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    c.save(c.REPORT/'BASELINE_MODEL_HANDOFF.json',c.load(out/'model_handoff.json'))
    print(json.dumps({'package_directory':str(out),'word_counts':word_counts,'validation':metrics['overall']},ensure_ascii=False,indent=2),flush=True)
if __name__=='__main__':main()





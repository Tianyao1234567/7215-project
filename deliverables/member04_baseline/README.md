# Member 04 original YOLOv8n baseline

Run yolov8n_newjson_from_official_20261105_213549 completed 100 epochs from official COCO weights, and best.pt was reloaded for independent validation and prediction. No frozen test evaluation was performed. model_handoff.json, validation_metrics.json and results.csv are the machine-readable result records.

## Start here

This package contains the trained best.pt and last.pt, code, exact configuration, environment versions, frozen split, complete training log, curves, representative predictions and report material. All 1713 converted YOLO labels are included in dataset_labels/labels, and official initialization weights with provenance are in initialization. Multi-GB source images remain at D:\Desktop\7215\project\datasets\current. All 1761 original JSON remain at D:\Desktop\7215\project\datasets\annotation_source\json, and all 48 excluded images with their JSON remain at D:\Desktop\7215\project\datasets\quarantine.

The authoritative project is D:\Desktop\7215\project. Open PowerShell there and use its verified interpreter. The existing .venv_gpu reuses the machine's installed GPU PyTorch and is not a portable environment. requirements.txt records versions, and D:\Desktop\7215\project\environment\SETUP.md documents the existing GPU setup. No global Python, driver or BIOS changes were made.

## Independent evaluation for member 06

```powershell
Set-Location -LiteralPath 'D:\Desktop\7215\project'
& 'D:\Desktop\7215\project\environment\.venv_gpu\Scripts\python.exe' -B '.\deliverables\member04_baseline\code\evaluate_baseline.py' --weights '.\deliverables\member04_baseline\best.pt' --split val --output ('.\baseline\runs\validation_check_'+(Get-Date -Format yyyyMMdd_HHmmss))
```

The code snapshot uses code/project_reference.json to find the existing project dataset. On another machine set $env:IDAT7215_PROJECT_ROOT to the relocated project root and update datasets/current/data.yaml's path. Transfer the current images with the supplied split manifest, and place dataset_labels/labels under the relocated datasets/current folder. Put initialization/yolov8n.pt under baseline/weights when recreating the project structure. The test entry requires the explicit --split test --final-test flags. Use it only after model and protocol freeze under member06's final evaluation plan, without selecting settings from test results.

## Image inference for member 07

```powershell
Set-Location -LiteralPath 'D:\Desktop\7215\project'
& 'D:\Desktop\7215\project\environment\.venv_gpu\Scripts\python.exe' -B '.\deliverables\member04_baseline\code\predict_baseline.py' --weights '.\deliverables\member04_baseline\best.pt' --source 'D:\Desktop\7215\project\datasets\current\images\val\Cracking_Image_20231128195336980.jpg' --conf 0.25 --output ('.\baseline\runs\prediction_check_'+(Get-Date -Format yyyyMMdd_HHmmss))
```

predictions.json reports class_id, class_name, confidence and xyxy_pixels on the original image. The four coordinates are x1, y1, x2, y2, in pixels, not normalized centre coordinates. conf 0.25 is an illustration threshold and is not the validation AP collection threshold. The saved prediction images label class and confidence. The five classes use IDs 0 through 4 in classes.json.

## Fresh 100-epoch reproduction

```powershell
Set-Location -LiteralPath 'D:\Desktop\7215\project'
.\baseline\start_training.ps1
```

This opens a new run through the current visible terminal and uses official baseline/weights/yolov8n.pt with resume=False, 100 epochs and patience=0. Never initialize a new baseline from this package's trained best.pt. The final protocol is config.json, and config.yaml captures the full framework arguments. Batch16 and workers0 passed the real-data resource check. The framework warns that RAM caching with deterministic=True does not guarantee bitwise-identical runs. Member05 should use the same fixed split, image size and experiment budget for the intended comparison. This user-authorized protocol is supplied for team alignment and does not claim a completed team agreement.

## Evidence and materials

- results.csv, training.log and training_verified.json verify epochs 1 through 100 and contain no nonfinite numeric values.
- plots contains the training curves, validation PR/confidence curves and confusion matrices. Raw run files remain at D:\Desktop\7215\project\baseline\runs\yolov8n_newjson_from_official_20261105_213549.
- predictions contains all 171 validation-image JSON outputs, class representatives and available error examples. error_analysis.json documents fixed-confidence matching and links each example to its image ID.
- audit records the data conversion, source comparisons, source ZIP metadata, sample review, resource check and actual cleanup.
- baseline_method_300words.md contains approximately 300 method words. personal_contribution.md contains 436 words for Tianyao Zhang to verify. baseline_report.md includes results, figure captions and references. presentation_notes.md and member04_baseline_slides.pptx supply two slides for member08.

## Limits and ownership

Only the revised train JSON supplied the current labels. The former 619-image validation split was not used. The frozen 1371/171/171 split has no exact decoded duplicate or inferred original/augmented family across sets. Verified printing-process IDs remain unavailable, so adjacent frames may still create dependence. Off_platform has nine validation objects. Format checks and ten visual examples do not establish complete semantic annotation correctness, normal-only false-alarm performance, or independent-print generalization.

Member03 still needs to resolve 16 inconsistent same-pixel groups and supply true object/batch/process identifiers. The complete exclusion records remain in audit/NEW_DELIVERY_AUDIT.json and the project quarantine folder. Full photo re-upload is unnecessary for these decisions.

Ultralytics provides the original model, training engine, losses, augmentation, validation metrics and built-in plots. The project wrappers, JSON conversion, audit, data materialization and handoff packaging are project-specific and used AI assistance. Member05 owns the lightweight head, member06 unified evaluation and timing, member07 the demo, and member08 the assembled report. No member messages were sent. GPU power, a unified FPS benchmark and deployment export were not measured or claimed.

## Disk cleanup

The project initially contained 31.71 GB of logical file lengths. The recorded cleanup increased available disk space by 25.49 GB. Logical path totals can count hardlinks more than once and differ from physical allocation. cleanup_record.json lists each actual deletion and all retained categories. C-drive historical files were left unchanged. A final project size snapshot is saved separately after all outputs are complete.

## Recreating the required directories on another computer

Use a compatible Python 3.10 GPU environment with the recorded versions, set IDAT7215_PROJECT_ROOT to the new project root, and use that environment's Python. environment_setup.md describes this computer's setup for reference; its absolute base-Python path and .venv_gpu are not portable.

Copy code/*.py to the new baseline folder, except run_project.py which belongs at the project root. Copy start_training.ps1 to baseline. Copy config.json to baseline/configs/new_json_100epochs.json, official initialization/yolov8n.pt to baseline/weights/yolov8n.pt, and split_manifest.csv to datasets/current/frozen_split_manifest.csv. Copy dataset_labels/labels into datasets/current/labels and preserve the train/val/test subfolders. Copy audit/current_data_audit.json to reports/new_json_20261105/current_data_audit.json so the evaluator can verify its observed class counts.

Transfer the matching current images separately into datasets/current/images/train, val and test. Create datasets/current/data.yaml using the supplied dataset_labels/data.yaml with its path updated to the new datasets/current location. The names, splits and all label bytes stay unchanged. Update config.json's data_yaml and initialization_path when placing the relocated configuration, while retaining its training settings and identity hashes.

For evaluation and inference, use the packaged best.pt. For fresh training, use the official initialization checkpoint. The JSON conversion verification command additionally needs the original datasets/annotation_source/json and datasets/quarantine retained in the full source project. This small package supplies the frozen training labels but does not duplicate the full original photo and annotation-source folders.

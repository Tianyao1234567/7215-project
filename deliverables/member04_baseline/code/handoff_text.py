"""Write member 04 report prose from verified run artifacts."""
from pathlib import Path
import new_json_common as c

def write_texts(out,run,metrics,analysis,verified,cleanup):
    overall=metrics['overall'];pct=lambda v:f'{100*v:.2f}%'
    p=pct(overall['metrics/precision(B)']);r=pct(overall['metrics/recall(B)']);a=pct(overall['metrics/mAP50(B)']);b=pct(overall['metrics/mAP50-95(B)'])
    methods='''We implemented the original YOLOv8n detector as the reference baseline for five FDM printing defect classes: Cracking, Layer_shifting, Off_platform, Stringing, and Warping. We used Ultralytics 8.2.103 and its official COCO pretrained yolov8n.pt checkpoint. YOLOv8 uses an anchor-free detection head [1], [2]. We preserved the original nano architecture and adapted the output to five classes. The run started from epoch one with resume disabled and did not reuse the earlier 35-epoch experiment or another member's trained model.

The authoritative annotation source was the revised per-image JSON supplied for the 1,761 training photographs. Both delivered TXT exports were unsuitable as direct training inputs. We converted each axis-aligned rectangle to normalized YOLO centre coordinates and dimensions using the actual 3,072 by 2,048 image size. Automated checks covered image pairing, source hashes, class mapping, finite coordinates, bounds, duplicate rectangles, and agreement with the frozen labels. A visual sample covered ten training or validation images across all five classes. We excluded 32 images from 16 groups with identical pixels but inconsistent rectangles, together with 16 related filename variants. All original JSON and these 48 images remain available for review.

We reused the frozen seed-42 split of 1,371 training, 171 validation, and 171 test images. Pixel duplicates and inferred original/augmented filename families do not cross splits. Verified printing-process identifiers were unavailable, so this grouping does not establish generalization to independent print runs.

Training used 640-pixel inputs for 100 complete epochs, SGD, initial learning rate 0.01, final learning-rate fraction 0.01, momentum 0.937, weight decay 0.0005, and three warm-up epochs. Batch size was 16 with zero loader workers, automatic mixed precision, and RAM caching. Mosaic augmentation closed for the final ten epochs. We reloaded the saved best checkpoint for validation and exported confidence-scored predictions. Test images remained withheld from model selection and evaluation.'''
    contribution=f'''I was responsible for the original YOLOv8n baseline for Topic 3 and for preparing the model interface required by members 06 and 07. My contribution covered the data acceptance checks, the training workflow, retention of experimental evidence, and baseline material for member 08. I used AI assistance to prepare and review code and documentation, and I have separated that assistance and the reused open-source framework from the project-specific work.

For data acceptance, I organised the revised delivery around its 1,761 per-image JSON annotations. The previous TXT locations could not serve as the current ground truth because one retained the old annotations and the other contained incomplete exports. The project scripts rebuilt the normalized YOLO rectangles and checked class IDs, image dimensions, coordinate bounds, source image hashes, and frozen label hashes. The audit and ten-image visual sample are documented in reports/new_json_20261105. These checks support the reported scope of acceptance without claiming that every annotation received a complete manual review.

I retained the existing 1,371/171/171 split rather than generating a new random split. I preserved all original JSON and isolated 48 conflicting or related images in datasets/quarantine. This maintained the exclusion policy while keeping the evidence available for member 03 to resolve. I also documented that inferred filename families do not establish independent printing-process groups.

For the baseline experiment, I prepared train_baseline.py, evaluate_baseline.py, predict_baseline.py, and the shared project runtime configuration. A real-data resource check verified training, checkpoint saving, reloading, validation, and prediction before the formal run. The formal experiment, {run.name}, started from official COCO weights and completed all 100 epochs with batch size 16 and 640-pixel inputs. Its results.csv, complete terminal log, configuration, environment details, and separate best.pt and last.pt are retained. The saved best checkpoint was then reloaded for validation on 171 images. Its mAP50 was {a} and mAP50-95 was {b}.

I prepared a handoff package with class mappings, frozen split manifests, independent evaluation and prediction commands, training curves, validation plots, and representative outputs. The error examples identify unmatched predictions and annotations at a fixed confidence threshold rather than presenting selected images as a substitute for evaluation. I also organised the D-drive project, preserved the reference models and historical run, and recorded each removed redundant dataset or archive. This released approximately {cleanup['observed_free_bytes_increase']/1e9:.2f} GB of disk space during cleanup.

My baseline provides a reproducible reference for the lightweight model comparison. Member 05 remains responsible for the lightweight detector, member 06 for unified accuracy and speed comparisons, and member 07 for the demonstration. The frozen test set remains available to that evaluation workflow. These deliverables allow the team to reproduce the baseline and compare it under a stated protocol.'''
    table='| Class | Validation images | Objects | Precision | Recall | AP50 | AP50–95 |\n|---|---:|---:|---:|---:|---:|---:|\n'
    audit=c.load(c.REPORT/'current_data_audit.json')
    for row in metrics['per_class']:
        name=row['name'];table+=f"| {name} | {audit['class_image_counts']['val'][name]} | {audit['box_counts_by_split']['val'][name]} | {pct(row['precision'])} | {pct(row['recall'])} | {pct(row['mAP50'])} | {pct(row['mAP50_95'])} |\n"
    references='''[1] Ultralytics, “Ultralytics YOLO,” version 8.2.103, GitHub. [Online]. Available: https://github.com/ultralytics/ultralytics/tree/v8.2.103. Accessed: Nov. 5, 2026.

[2] Ultralytics, “Explore Ultralytics YOLOv8.” [Online]. Available: https://docs.ultralytics.com/models/yolov8/. Accessed: Nov. 5, 2026.

Official initialization artifact: https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt. Its SHA256 is recorded in config.json and model_handoff.json. Results in this report come from the saved local run, not the documentation's COCO benchmarks.'''
    report=f'''# Original YOLOv8n baseline

The original YOLOv8n baseline completed 100 epochs in {verified['training_seconds']/60:.2f} minutes. Independent validation of the reloaded best checkpoint on the fixed 171-image validation set produced precision {p}, recall {r}, mAP50 {a}, and mAP50–95 {b}. This is validation evidence for the current annotation version. The test set remains withheld.

## Method and training settings

{methods}

## Validation results

{table}

The table's image counts indicate class presence and can overlap across classes. Object counts are annotation rectangles. Precision and recall use the Ultralytics validation F1-curve operating point. AP50 and AP50–95 integrate the detection confidence curve and use the stated IoU criteria. The independent validation used imgsz 640, confidence 0.001 for AP collection, NMS IoU 0.7, batch 16, device 0, and FP32 validation. Best-checkpoint selection used the same validation split during training, so these are not untouched test results.

At confidence 0.25 and class-aware matching IoU 0.5, the illustrative validation prediction pass found {analysis['true_positive_boxes']} matched detections, {analysis['false_positive_boxes']} unmatched predictions, and {analysis['false_negative_boxes']} unmatched annotations. These counts use a different operating point from the table's precision and recall. predictions/error_analysis.json gives the matching rule and exact image references. The examples include each class and the available false-positive and false-negative cases.

## Interpretation and limits

The current split contains no duplicate decoded pixels or inferred original/augmented filename family across sets. Adjacent photographs from the same real print may still cross sets because verified process IDs were not supplied. High validation accuracy therefore cannot establish independent-print generalization. Off_platform has only nine validation objects, so its per-class estimate is based on a small sample. This dataset does not establish performance on normal print-only inputs or a production false-alarm rate.

Machine integrity checks and ten sampled visual checks cannot establish complete semantic annotation correctness. Member 03 still needs to resolve the 16 groups with inconsistent rectangles and supply verified object, batch, or process identifiers. The isolated samples remain excluded from this experiment. No test results, lightweight-model comparison, verified deployment export, or unified speed benchmark are claimed here. Validator timing is retained only as framework diagnostic output. GPU power was not measured. RAM caching is recorded alongside deterministic=True, but the framework warns that it does not guarantee bitwise-identical reproduction.

## Reproduction and ownership

Run ID: {run.name}. The exact settings, environment, hashes, configuration and split files accompany this report. training.log and results.csv verify 100 consecutive completed epochs. Official initialization SHA256: {c.INITIAL_SHA}. Frozen manifest semantic SHA256: {c.SEMANTIC_SHA}. The CSV file hash is separately recorded in model_handoff.json.

Ultralytics supplies the detector, losses, augmentation engine, validation metrics and plot generation. Project-specific work consists of the JSON conversion and audit, frozen-split materialization, scoped runtime and training wrappers, checkpoint verification, prediction serialization, example matching, and delivery packaging. AI assisted the implementation review and draft prose.

## Figure captions

Training curves: 100 consecutive epochs of the original YOLOv8n baseline on the new JSON-derived annotations. Validation values come from the same fixed split used for checkpoint selection.

Precision–recall and confusion plots: independent reload validation of best.pt on 171 validation images. Consult validation_metrics.json for the complete settings.

Representative detections: fixed-confidence predictions on validation photographs, labelled with class and confidence. Coordinates in predictions.json are pixel xyxy on the original 3072×2048 image. Examples illustrate model behaviour and do not estimate generalization.

## References

{references}
'''
    notes=f'''# Member 04 presentation material

Two slides accompany this text in member04_baseline_slides.pptx. The speaking allocation below is a team suggestion, not a teacher requirement.

## Slide 1 YOLOv8n baseline and fixed data

Original YOLOv8n with official COCO initialization. Five defect classes. Revised JSON converted to YOLO rectangles. Frozen split 1371 train / 171 validation / 171 test, seed42. Isolate 48 images from conflicting and related groups. Train 100 epochs at 640 with SGD, batch16, AMP and zero workers. Runtime: {verified['training_seconds']/60:.2f} minutes on RTX3080 Laptop GPU.

Speaker text, about 40 seconds: Our reference is the original nano detector. We rebuilt the labels from the revised JSON, kept the previous frozen split, and excluded conflicting copies. The training started from the official pretrained checkpoint and completed all 100 epochs. The log, checkpoints and exact settings are saved so the lightweight-model team can use the same conditions.

## Slide 2 Validation results and limits

Reloaded best.pt on 171 validation images: precision {p}, recall {r}, mAP50 {a}, mAP50–95 {b}.

{table}

Speaker text, about 45 seconds: These results come from an actual reload and validation of the saved model. The examples show each class and the available errors at confidence 0.25. The validation set also selected the checkpoint, and the test set remains untouched for the unified evaluation. Verified print-process IDs are still missing, and Off_platform has only nine validation objects. We therefore report this as the current baseline rather than evidence of independent-print generalization or production deployment speed.

Sources for both slides: this run's training_verified.json, validation_metrics.json, current_data_audit.json, and references [1]–[2] in baseline_report.md.
'''
    for name,text in [('baseline_method_300words.md',methods),('baseline_report.md',report),('personal_contribution.md',contribution),('presentation_notes.md',notes),('references.md',references)]:
        (out/name).write_text(text+'\n',encoding='utf-8')
    counts={'method_words':len(methods.split()),'contribution_words':len(contribution.split())}
    assert 280<=counts['method_words']<=350 and 300<=counts['contribution_words']<=600,counts
    c.save(out/'text_word_counts.json',counts)
    return counts



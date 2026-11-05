# Original YOLOv8n baseline

The original YOLOv8n baseline completed 100 epochs in 31.55 minutes. Independent validation of the reloaded best checkpoint on the fixed 171-image validation set produced precision 93.22%, recall 94.05%, mAP50 95.47%, and mAP50–95 60.03%. This is validation evidence for the current annotation version. The test set remains withheld.

## Method and training settings

We implemented the original YOLOv8n detector as the reference baseline for five FDM printing defect classes: Cracking, Layer_shifting, Off_platform, Stringing, and Warping. We used Ultralytics 8.2.103 and its official COCO pretrained yolov8n.pt checkpoint. YOLOv8 uses an anchor-free detection head [1], [2]. We preserved the original nano architecture and adapted the output to five classes. The run started from epoch one with resume disabled and did not reuse the earlier 35-epoch experiment or another member's trained model.

The authoritative annotation source was the revised per-image JSON supplied for the 1,761 training photographs. Both delivered TXT exports were unsuitable as direct training inputs. We converted each axis-aligned rectangle to normalized YOLO centre coordinates and dimensions using the actual 3,072 by 2,048 image size. Automated checks covered image pairing, source hashes, class mapping, finite coordinates, bounds, duplicate rectangles, and agreement with the frozen labels. A visual sample covered ten training or validation images across all five classes. We excluded 32 images from 16 groups with identical pixels but inconsistent rectangles, together with 16 related filename variants. All original JSON and these 48 images remain available for review.

We reused the frozen seed-42 split of 1,371 training, 171 validation, and 171 test images. Pixel duplicates and inferred original/augmented filename families do not cross splits. Verified printing-process identifiers were unavailable, so this grouping does not establish generalization to independent print runs.

Training used 640-pixel inputs for 100 complete epochs, SGD, initial learning rate 0.01, final learning-rate fraction 0.01, momentum 0.937, weight decay 0.0005, and three warm-up epochs. Batch size was 16 with zero loader workers, automatic mixed precision, and RAM caching. Mosaic augmentation closed for the final ten epochs. We reloaded the saved best checkpoint for validation and exported confidence-scored predictions. Test images remained withheld from model selection and evaluation.

## Validation results

| Class | Validation images | Objects | Precision | Recall | AP50 | AP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| Cracking | 42 | 50 | 100.00% | 96.94% | 99.50% | 68.09% |
| Layer_shifting | 30 | 30 | 96.55% | 100.00% | 99.31% | 69.87% |
| Off_platform | 9 | 9 | 79.04% | 84.08% | 85.98% | 44.00% |
| Stringing | 41 | 48 | 95.72% | 97.92% | 97.00% | 77.05% |
| Warping | 49 | 92 | 94.77% | 91.30% | 95.54% | 41.17% |


The table's image counts indicate class presence and can overlap across classes. Object counts are annotation rectangles. Precision and recall use the Ultralytics validation F1-curve operating point. AP50 and AP50–95 integrate the detection confidence curve and use the stated IoU criteria. The independent validation used imgsz 640, confidence 0.001 for AP collection, NMS IoU 0.7, batch 16, device 0, and FP32 validation. Best-checkpoint selection used the same validation split during training, so these are not untouched test results.

At confidence 0.25 and class-aware matching IoU 0.5, the illustrative validation prediction pass found 221 matched detections, 23 unmatched predictions, and 8 unmatched annotations. These counts use a different operating point from the table's precision and recall. predictions/error_analysis.json gives the matching rule and exact image references. The examples include each class and the available false-positive and false-negative cases.

## Interpretation and limits

The current split contains no duplicate decoded pixels or inferred original/augmented filename family across sets. Adjacent photographs from the same real print may still cross sets because verified process IDs were not supplied. High validation accuracy therefore cannot establish independent-print generalization. Off_platform has only nine validation objects, so its per-class estimate is based on a small sample. This dataset does not establish performance on normal print-only inputs or a production false-alarm rate.

Machine integrity checks and ten sampled visual checks cannot establish complete semantic annotation correctness. Member 03 still needs to resolve the 16 groups with inconsistent rectangles and supply verified object, batch, or process identifiers. The isolated samples remain excluded from this experiment. No test results, lightweight-model comparison, verified deployment export, or unified speed benchmark are claimed here. Validator timing is retained only as framework diagnostic output. GPU power was not measured. RAM caching is recorded alongside deterministic=True, but the framework warns that it does not guarantee bitwise-identical reproduction.

## Reproduction and ownership

Run ID: yolov8n_newjson_from_official_20261105_213549. The exact settings, environment, hashes, configuration and split files accompany this report. training.log and results.csv verify 100 consecutive completed epochs. Official initialization SHA256: f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36. Frozen manifest semantic SHA256: ec8385ce1b86748b7a49268f160084609d4ffa1ce5f275d83711be8569afca2c. The CSV file hash is separately recorded in model_handoff.json.

Ultralytics supplies the detector, losses, augmentation engine, validation metrics and plot generation. Project-specific work consists of the JSON conversion and audit, frozen-split materialization, scoped runtime and training wrappers, checkpoint verification, prediction serialization, example matching, and delivery packaging. AI assisted the implementation review and draft prose.

## Figure captions

Training curves: 100 consecutive epochs of the original YOLOv8n baseline on the new JSON-derived annotations. Validation values come from the same fixed split used for checkpoint selection.

Precision–recall and confusion plots: independent reload validation of best.pt on 171 validation images. Consult validation_metrics.json for the complete settings.

Representative detections: fixed-confidence predictions on validation photographs, labelled with class and confidence. Coordinates in predictions.json are pixel xyxy on the original 3072×2048 image. Examples illustrate model behaviour and do not estimate generalization.

## References

[1] Ultralytics, “Ultralytics YOLO,” version 8.2.103, GitHub. [Online]. Available: https://github.com/ultralytics/ultralytics/tree/v8.2.103. Accessed: Nov. 5, 2026.

[2] Ultralytics, “Explore Ultralytics YOLOv8.” [Online]. Available: https://docs.ultralytics.com/models/yolov8/. Accessed: Nov. 5, 2026.

Official initialization artifact: https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt. Its SHA256 is recorded in config.json and model_handoff.json. Results in this report come from the saved local run, not the documentation's COCO benchmarks.


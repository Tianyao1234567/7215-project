# Member 04 presentation material

Two slides accompany this text in member04_baseline_slides.pptx. The speaking allocation below is a team suggestion, not a teacher requirement.

## Slide 1 YOLOv8n baseline and fixed data

Original YOLOv8n with official COCO initialization. Five defect classes. Revised JSON converted to YOLO rectangles. Frozen split 1371 train / 171 validation / 171 test, seed42. Isolate 48 images from conflicting and related groups. Train 100 epochs at 640 with SGD, batch16, AMP and zero workers. Runtime: 31.55 minutes on RTX3080 Laptop GPU.

Speaker text, about 40 seconds: Our reference is the original nano detector. We rebuilt the labels from the revised JSON, kept the previous frozen split, and excluded conflicting copies. The training started from the official pretrained checkpoint and completed all 100 epochs. The log, checkpoints and exact settings are saved so the lightweight-model team can use the same conditions.

## Slide 2 Validation results and limits

Reloaded best.pt on 171 validation images: precision 93.22%, recall 94.05%, mAP50 95.47%, mAP50–95 60.03%.

| Class | Validation images | Objects | Precision | Recall | AP50 | AP50–95 |
|---|---:|---:|---:|---:|---:|---:|
| Cracking | 42 | 50 | 100.00% | 96.94% | 99.50% | 68.09% |
| Layer_shifting | 30 | 30 | 96.55% | 100.00% | 99.31% | 69.87% |
| Off_platform | 9 | 9 | 79.04% | 84.08% | 85.98% | 44.00% |
| Stringing | 41 | 48 | 95.72% | 97.92% | 97.00% | 77.05% |
| Warping | 49 | 92 | 94.77% | 91.30% | 95.54% | 41.17% |


Speaker text, about 45 seconds: These results come from an actual reload and validation of the saved model. The examples show each class and the available errors at confidence 0.25. The validation set also selected the checkpoint, and the test set remains untouched for the unified evaluation. Verified print-process IDs are still missing, and Off_platform has only nine validation objects. We therefore report this as the current baseline rather than evidence of independent-print generalization or production deployment speed.

Sources for both slides: this run's training_verified.json, validation_metrics.json, current_data_audit.json, and references [1]–[2] in baseline_report.md.


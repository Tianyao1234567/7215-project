# Member 4 — PPT content draft (engineering milestone only)
Do not present this as a completed FDM model comparison.

## Slide 1 — Original YOLOv8n Baseline Pipeline
- Standard Ultralytics YOLOv8n architecture; no custom lightweight head.
- Source-traceable official COCO initialization with a SHA256 record.
- Read-only dataset checks: class IDs, normalized boxes, corrupt images, exact duplicates and supplied process groups.
- Train for optimization; validation for model selection; independent test reserved for member 6.
- Each run saves settings, data fingerprints, dependency versions, weights, logs and prediction outputs.

Speaker note:
My assigned module establishes a reproducible baseline interface. The architecture remains the original detector. Fair comparison requires the same agreed training protocol for both models.

## Slide 2 — Verified Work and Remaining Dependencies
- 13 data-tool regression tests passed.
- Two repeated one-epoch CPU smoke runs gave identical recorded loss values.
- An additional smoke run verified official pretrained initialization.
- Weight reload, validation and image prediction interfaces passed.
- These runs used synthetic rectangles; they do not establish FDM detection accuracy.
- Pending: accepted FDM dataset, shared experiment protocol, formal training and downstream independent acceptance.

Replace the last two points with real run IDs, settings, validation results and representative FDM detections after actual training.
Do not put the reference checkpoint metrics or paper results in the baseline-result column.

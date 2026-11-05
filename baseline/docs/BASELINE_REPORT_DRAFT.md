# Baseline and Training Configuration — current-status draft
This text describes completed engineering checks only. Update it using the actual formal run before submission.

An original YOLOv8n detection pipeline was prepared as the baseline for the FFF defect-detection project. The implementation uses the standard Ultralytics architecture rather than a custom lightweight detection head. Official COCO initialization weights were obtained from the Ultralytics release repository, and their download location and SHA256 digest were recorded. The existing project reference checkpoints were inspected separately and were not treated as newly trained baseline results.

The training entry point records the requested configuration, effective framework arguments, random seed, software versions, data fingerprints and run status. It stores the best and final checkpoints, the training history, validation metrics and a prediction example. Training uses the training split for optimization and the validation split for model selection. The independent test split is withheld from the training configuration so that member 6 can perform the final common evaluation after model selection is frozen.

Before training, the data interface checks image readability, label availability, integer class identifiers, finite normalized coordinates, positive box dimensions and box boundaries. Empty label files are preserved as potential negative examples. Exact file and decoded-pixel duplicates are detected, while related-process leakage checks depend on the group identifiers supplied by the data owner. These automated checks do not replace manual annotation review.

Engineering verification was performed in a CPU environment using Python 3.11.15, PyTorch 2.5.1 and Ultralytics 8.2.103. Thirteen data-tool regression tests passed. Two repeated one-epoch runs on a synthetic rectangle fixture produced identical recorded loss values. An additional smoke run verified the official pretrained initialization path. Checkpoint reload, validation and image-prediction interfaces also executed successfully.

These tests establish pipeline functionality, not FFF defect-detection accuracy. The accepted real dataset, shared training protocol and formal training run are still pending. Therefore, this draft reports no independently measured FFF baseline accuracy or final comparative efficiency result.

References:
[1] Ultralytics, “YOLOv8,” https://docs.ultralytics.com/models/yolov8/
[2] W. Hu et al., “Real-time defect detection for FFF 3D printing using lightweight model deployment,”
Int. J. Adv. Manuf. Technol., vol. 134, pp. 4871–4885, 2024. doi:10.1007/s00170-024-14452-4.
Only the publisher's abstract was available in this session; implementation details need the full paper from member 2.

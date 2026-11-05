# Reused code, weights and assistance
- Ultralytics 8.2.103 supplies YOLOv8 architecture, dataloaders, training loop, losses, metrics,
  prediction rendering and export functions. Source: https://github.com/ultralytics/ultralytics
  License shown by the package/reference exports: AGPL-3.0. Preserve required notices in redistribution.
- PyTorch, torchvision, NumPy, Pillow, PyYAML, ONNX and ONNX Runtime are dependencies;
  their package licenses remain applicable.
- weights/yolov8n.pt: official Ultralytics COCO checkpoint, v8.2.0 assets release.
  It is external initialization, not the group's trained defect detector.
- originals/*.py: supplied by member 3; retained unchanged.
- data_tools/*_fixed.py expands the supplied scripts' interfaces and responsibilities;
  the common audit module, training wrappers, tests and documentation were generated and
  verified with ChatGPT assistance in this session. The user must review and explain them.
  Do not label all generated code as solely manually written by the student.
- Reference best/best_pre PT/ONNX: supplied through the project; original creator, code revision,
  data and protocol still need confirmation from member 2/leader. Not included as a new member 4 result.
- The packaged reference runtime pictures use Ultralytics' bus.jpg solely for compatibility testing.
  They do not demonstrate 3D-printing defect accuracy. Reference defect boxes on a street image
  should be interpreted as out-of-domain predictions, not a valid defect demo.
- The synthetic rectangle fixture is explicitly generated for engineering testing.
- Formal experiment numbers, image sources and citations must be updated from real evidence.

The teacher's supplied guide requires students to distinguish open-source parts from their own implementation.
No separate explicit AI-use rule was found in the supplied project guide.
That absence is not evidence of an unrestricted AI policy; use accurate authorship disclosure.

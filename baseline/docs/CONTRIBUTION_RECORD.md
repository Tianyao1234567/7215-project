# Member 4 contribution record — factual working log
Date: 2026-11-01, China/Hong Kong time.

Role: original YOLOv8n baseline engineering and training.
Work below was created or executed with ChatGPT assistance in this session.
The user must review, understand and independently explain it before adopting it as assessed work.

| Work | Actual file/evidence | State |
|---|---|---|
| Audited incoming scripts without executing deletion logic | originals/, docs/CHANGELOG.md | Complete inspection |
| Repaired data checks as temporary upstream support | data_tools/, evidence/data_tools_tests.log | 13 regression tests passed; member 3 real-data acceptance pending |
| Inspected reference checkpoint structure/history | evidence/reference_checkpoint_metadata.json | Read from actual archive; not our model results |
| Loaded supplied PT/ONNX models | evidence/reference_runtime/, reference_pt_onnx_parity.json | Runtime passed; no FDM accuracy evaluation |
| Developed baseline train/val/predict interfaces | train_baseline.py, validate_baseline.py, predict_baseline.py | CPU integration checks passed |
| Recorded official initialization provenance | weights/yolov8n.source.json | Downloaded and hashed |
| Repeated engineering training | runs/smoke_*/ | 3 successful synthetic runs, not formal baseline |
| Formal real-data training | No formal run exists | Blocked |
| Drafted module documentation and handoff | README, PROGRESS, docs/ | Requires user/group review |

Do not claim: manual annotation of the whole dataset, implementing member 5's lightweight head,
performing member 6's final comparison, creating the full demo, or completing the whole group report.
Do not claim that the reference checkpoints or paper metrics are this member's newly measured results.

## Individual contribution report preparation
The teacher requests 300–600 words per member. A final report cannot truthfully be completed now
because the assigned formal training has not been done and the user's own review/explanation has
not been recorded. Use this working record to write the final statement after:
1. Reviewing and being able to explain the scripts and training choices.
2. Running and inspecting the real FDM smoke/formal experiment.
3. Recording actual run IDs, delivered files and downstream acceptance.
4. Describing AI assistance and reused open-source code according to course/institution requirements.

Current technical narrative, for adaptation:
My assigned responsibility is the original YOLOv8n baseline module. The current deliverable includes a reproducible training entry point, validation and inference interfaces, configuration templates and an evidence-based progress record. Development and automated verification were supported by ChatGPT. I remain responsible for checking the implementation, understanding the training settings and confirming that the reported results match the actual runs. Formal defect-detection training and the final handoff are still pending receipt and acceptance of the real dataset.

## 2026-11-02新增工作（AI协助执行）
接收4个ZIP并校验解压；对2380张真实图/标签完整审计；发现483张验证图与训练重复；导出重复及同源线索清单；适配本机路径；在3080执行真实五类20train/10val、2epoch试训并保存权重/验证结果。未完成正式FDM模型训练，未替3号重划正式数据。


## 2026-11-02 — AI-assisted audit and scoped engineering
With the user providing/identifying receipts, the assistant compared all 2380 member 2 label files and all image/label/config files against member 3 sources, recorded no delivered revisions, preserved separate provenance, organized files only in the designated project and removed eight verified redundant input ZIPs as authorized. Re-ran 13 tests and CUDA forward/backward/NumPy/NMS checks successfully. Updated workflow, role boundaries and reproducibility instructions. This does not constitute manual annotation review, member 5 model development or completed formal baseline training.

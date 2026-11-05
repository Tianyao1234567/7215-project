# 文件整理记录 — 2026-11-02

全部操作限定于 D:\Desktop\7215\project。二号、三号交付分开保存；未修改收到的照片、框标签或原data.yaml。原始三号完整数据路径继续保留。

| 原位置 | 现在的位置 | 处理 |
|---|---|---|
| yolo/yolo | sources/member_02/yolo_dataset | 原样移动，不与三号混合 |
| labels(1).zip | sources/member_02/labels_received_20261102 | 完整解压、逐文件校验后删除ZIP |
| reference_models/pre_train_model | sources/member_02/reference_models/pre_train_model | 8个原文件原样移动 |
| 根目录三个Python原脚本 | sources/member_03/scripts | 保留原版；相同的重复上传副本合并保留一份 |
| 四个dataset分包 | datasets/received_20261102/dataset | 解压件保留原路径，两个旧缓存另存sources/member_03 |
| reference_inputs中的PDF | sources/shared/course | 原件字节保留，文件名统一为英文 |
| reference_inputs中的图片 | sources/shared/chat | 原样移动 |
| 数据验收报告、GPU旧报告、样例副本 | reports及其history/examples | 集中保存 |
| 根目录README与进度表 | 保留根目录并更新 | 旧版另存reports/history |
| baseline/README.md | 保留原位置并更新 | 旧版另存reports/history |

删除的8个源ZIP（所有解压内容均已验证保留）：

- dataset-20261101T184211Z-1-001.zip（2147617512字节）
- dataset-20261101T184211Z-1-002.zip（2147677066字节）
- dataset-20261101T184211Z-1-003.zip（2147358603字节）
- dataset-20261101T184211Z-1-004.zip（1349790287字节）
- yolo.zip（7774344252字节）
- labels(1).zip（732572字节）
- pre_train_model(1).zip（33257076字节）
- reference_inputs/pre_train_model(1)(1).zip（33257076字节）

共释放 15634034444 字节，即约15.63GB（14.56GiB），不含合并的小脚本副本。删除前再次检查源包SHA256；遇到旧模型ZIP的Windows只读属性后，仅对该已授权删除文件清除只读并继续，完整操作日志保留。

没有删除解压照片、标注或参考模型。deliverables里的历史交付ZIP保留，它们是输出快照，不是待清理的源数据分包。

整理后验证：13/13数据工具测试通过；RTX3080 CUDA前后向、NumPy桥接、CUDA NMS通过；训练入口仍使用原项目环境，未改变Jupyter或驱动。日志见diagnostics/post_organization_tests_20261102.log和post_organization_check_20261102.log。

历史清单/日志中的旧路径作为当时证据保留。当前路径以sources/SOURCE_CATALOG.json与本表为准。diagnostics内的历史解压/对比程序依赖已按要求删除的源包，不作为日常运行入口；日常使用根目录run_project.py。

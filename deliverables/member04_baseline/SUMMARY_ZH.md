# 四号原始 YOLOv8n 基线总结

本目录集中保存四号已完成的工作、真实实验结果和可供作业使用的材料。编写小组报告时先读本文件，再使用英文方法正文、结果报告和图表。个人贡献仍需本人核实后提交。

## 已完成的工作

1. 复核三号新版train中的1761张照片及逐图JSON，重建YOLO标签；原labels/train仍为旧标签，另一处导出TXT不完整，本轮以JSON转换结果为准。
2. 保留48张争议及关联样本的隔离备份，复用1713张有效图片的冻结划分：1371 train、171 validation、171 test。seed42，旧validation619张不参与。
3. 使用官方COCO yolov8n.pt从epoch1完整训练100轮，resume=False，patience=0。imgsz640、batch16、workers0、SGD、AMP和RAM缓存。训练耗时31.55分钟，终端可见并保存完整日志。
4. 从磁盘重载新best.pt，实际验证171张图片、229个框，生成五类代表预测及误检漏检示例。test保持未使用。
5. 保留代码、配置、版本、初始化来源、权重、清单、曲线、指标和最短命令，并完成项目目录整理。

## 正式验证结果

总体Precision93.22%、Recall94.05%、mAP50 95.47%、mAP50–95 60.03%。这是当前validation上的正式结果，validation也用于选择best checkpoint。mAP50应按指标原名报告，不能改写为整体分类准确率。

| 类别 | Precision | Recall | AP50 | AP50–95 |
|---|---:|---:|---:|---:|
| Cracking | 100.00% | 96.94% | 99.50% | 68.09% |
| Layer_shifting | 96.55% | 100.00% | 99.31% | 69.87% |
| Off_platform | 79.04% | 84.08% | 85.98% | 44.00% |
| Stringing | 95.72% | 97.92% | 97.00% | 77.05% |
| Warping | 94.77% | 91.30% | 95.54% | 41.17% |


判断：这是一份可以交给轻量模型和演示工作的原始基线。较严格的定位指标仍有提升空间。Off_platform仅9个验证框；Warping的AP50–95为41.17%。真实工件/打印过程ID未核实，相邻帧可能相关，因此当前结果不能证明对独立打印过程的泛化能力。没有进行统一FPS测速、功耗测量或部署导出。

## 数据验收的边界

1713张通过全量格式、配对、坐标、哈希和冻结划分核对，并对五类共10张进行了画框抽查。这支持本轮使用，但不能证明每一张语义标注绝对正确。48张不是全部被证明标错：32张来自16组同画面不同框的副本，另16张是相关版本，为避免任取真值和关联泄漏而统一隔离。用户已选择保留隔离备份。

## 输出和证据

- 正式run：[训练目录](../../baseline/runs/yolov8n_newjson_from_official_20261105_213549/)，含training.log、results.csv、weights/best.pt、weights/last.pt。
- [机器可读验证指标](validation_metrics.json)、[本部分英文报告](baseline_report.md)、[约300词方法正文](baseline_method_300words.md)。
- [436词个人贡献草稿](personal_contribution.md)、[两页PPT](member04_baseline_slides.pptx)、[讲稿](presentation_notes.md)。
- [图表](plots/)、[五类及错误预测](../../deliverables/member04_baseline/predictions/)、[三号数据说明](DATA_REVIEW_MEMBER03.md)。
- 完整审计：[reports/new_json_20261105](../../reports/new_json_20261105/)。记录中的旧机器绝对路径属于实验来源，当前运行入口按克隆后的仓库根目录解析。

## 分工交接

四号提供原始基线及这些材料。五号负责论文轻量检测头和自己的训练；六号负责统一精度与速度比较、冻结后的test评价；七号负责演示；八号将本部分材料纳入全组报告。Ultralytics提供原始模型、训练和评估框架，本项目实现JSON转换、审计、冻结数据整理、训练封装及交付工具，并使用了AI辅助。

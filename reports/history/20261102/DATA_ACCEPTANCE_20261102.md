> 当前补充：二号新2380标签与三号逐字节相同，未见人工修订交付；sources按成员分开，8个冗余源ZIP已校验删除。详见SOURCE_COMPARISON_20261102.md及WORKFLOW_AND_RESPONSIBILITIES_20261102.md。

# 数据交付验收与训练进度
日期：2026-11-02（中国/香港时间）
工作根目录：D:\Desktop\7215\project

## 结论
四个压缩包已经接收、检查并解压。2026-11-02按用户要求完成逐项复核后，冗余源ZIP已删除；原始图像、标签、配置及校验清单均保留。
图片与标签的基础格式合格，但正式划分不合格，当前不应启动最终对照实验的长训练。
已实际完成真实五类数据的GPU小样本试训；它是工程验证，不是最终基线成果。

## 已收到与通过的部分
- 4个独立ZIP分包；解压4,761个文件，写出7,789,684,906字节，CRC验证通过并记录每文件SHA256。
- 2份旧框架.cache已单独保留到sources/member_03/original_cache_files，不导入训练，以免引用他人环境路径或载入旧缓存。
- 训练1761张、验证619张；2380张图全部能读取。
- 每张图片都有标签；没有孤立标签、空标签或非法数值/类别/框边界。
- 5类ID与参考映射一致：Cracking、Layer_shifting、Off_platform、Stringing、Warping。
- 实际共有3197条数值格式有效的框记录，train2366条、val831条；语义正确性仍需人工核验。
- 原始data.yaml写了他人E盘路径。本机另建baseline/configs/data.received_20261102.yaml，
  未修改收到的配置或正式划分。

## 正式验收未通过的部分
1. 完整图像SHA与解码像素SHA均确认：480个跨集合重复图像组。
   验证集619张中有483张与训练集字节完全相同，占78.03%。
   不同文件名也纳入检查，不是单纯因为名称相似。
2. 文件名的同源图像时间戳ID中有471个跨train/val；原图和增强版本也需要放在同一集合。
   文件名推断的source ID不等于经过核实的打印过程/工件ID，不能据此直接宣布无关联泄漏。
3. 对495对同源且字节相同的跨集合图像进行标签比较，492对框坐标等内容不同，
   已排除单纯换行/空格差异。差异不自动意味着某一版标错，但需要3号确认最终保留的标注版本。
4. 没有独立test，也没有正式工件/打印过程分组文件。
5. 1/4/5号尚未记录统一正式训练设置；provisional配置不能冒充已经商定。

## 每类标签计数
| 类别 | train图片含该类 | train框 | val图片含该类 | val框 |
|---|---:|---:|---:|---:|
| Cracking | 406 | 483 | 147 | 170 |
| Layer_shifting | 345 | 388 | 110 | 125 |
| Off_platform | 124 | 126 | 42 | 42 |
| Stringing | 417 | 505 | 135 | 161 |
| Warping | 503 | 864 | 196 | 333 |
一张图可能包含多个类别，因此“含该类图片数”不能简单相加作为总图片数。

## 本轮实际训练
run：baseline/runs/real_smoke_20261102/smoke_20261101T185410_489568Z/
- 官方YOLOv8n COCO初始化，使用真实FDM图和原BBox。
- 临时小样本：train20张、val10张，覆盖全部5类。
- 2 epoch，640像素，batch4，seed42，SGD，AMP关闭，增强关闭。
- 在RTX3080 Laptop GPU上完成训练、best/last保存、重新加载、验证及预测。
- 真实训练日志、曲线、配置和环境已保存。
- 选取的单张预测在conf0.25下为0个框；这不是有效缺陷检测的最终验收。
- 小样本验证mAP50约0.000840、mAP50-95约0.000408，只是短试训输出，
  不作为全数据性能、最终Baseline结果或论文复现成绩。

没有对收到的完整train/val重划，也没有删除/覆盖原图与标签。
没有用有78%重复的验证集跑100轮后冒充正式指标。

## 责任与最小后续交付
3号：无需重新提供8GB照片或重做已合格的基础格式检查。
请确认最终标签版本，去重，并按同源图像及真实工件/打印过程生成固定train/val/test划分。
可以先补新的划分清单、分组对应表和必要的最终标签文件；已有图片由4号本机复用。
candidate_source_image_groups.csv可辅助核对原图/增强图来源，但不是已验收的正式groups.csv。

1/4/5号：确定共同框架版本、数据摘要、输入尺寸、训练预算、batch、优化器/LR、增强、
seed、AMP和停止规则。正式模板仍为baseline/configs/baseline.provisional.yaml。

4号：负责新交付核验、正式训练、权重/日志/配置/预测交接和模块文稿更新。
本轮发现与修正临时路径、做30张真实图试训，不代表替3号承担整套正式数据维护。

## 证据文件
- diagnostics/dataset_archive_inventory.json
- diagnostics/dataset_extraction_status.json、dataset_extraction_manifest.json
- diagnostics/received_dataset_audit.json
- diagnostics/final_dataset_acceptance_summary.json
- diagnostics/duplicate_train_val_pairs.csv
- diagnostics/duplicate_annotation_conflicts.json
- diagnostics/candidate_source_image_groups.csv
- diagnostics/received_ground_truth_contact_sheet.jpg
- diagnostics/real_fdm_smoke_20261102_status.json、real_fdm_smoke_20261102.log
- 上述run中的status.json、handoff.json、fit/results.csv、fit/weights/best.pt,last.pt

需要提醒：run ID使用UTC，2026-11-01T18:54对应中国/香港时间2026-11-02凌晨，
不是把前一天的旧合成训练当成本轮真实训练。


## 2026-11-02：补充yolo.zip核查
3号说明最初使用2号文件，自己写3个Python脚本生成2份TXT清单。新yolo.zip含4763个文件，逐文件SHA256与此前四个dataset包全部一致（仅顶层目录名yolo/dataset不同），不是修订数据。示例train标签仍为两个class0框，val标签仍为一个class1框；现有重复和标签冲突未消除。下一步改为请2号确认框标签来源（人工/自动、是否有最终统一版本）及需要采用的权威标注；不再要求3号反复解释manifest。暂不冻结最终标签、划分或启动正式长训练。证据：diagnostics/yolo_source_comparison.json。

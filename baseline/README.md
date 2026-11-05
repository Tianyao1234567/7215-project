# IDAT7215 Topic 3 当前工程

工程根目录：D:\Desktop\7215\project。以下相对路径均从工程根目录起算。

已完成四号原始YOLOv8n基线。本次从官方COCO权重开始，完整训练100轮，耗时31.55分钟，已重载best.pt进行validation验证和预测。

验证集171张：Precision 93.22%，Recall 94.05%，mAP50 95.47%，mAP50–95 60.03%。完整逐类结果见deliverables/member04_baseline/validation_metrics.json。test保持未使用。

## 交付入口

交付目录：deliverables/member04_baseline。总说明和六／七号可直接执行的命令：该目录README.md。完整小包：deliverables/IDAT7215_Member04_Baseline_20261105.zip。内含代码、配置、best/last权重、日志、训练曲线、验证图、五类预测与错误示例、方法和个人贡献草稿，以及两页可编辑PPT。多GB图片不重复装包。

当前run：baseline/runs/yolov8n_newjson_from_official_20261105_213549。实时终端和training.log均保留，terminal_exit.json记录退出码，status.json和baseline/current_training_status.json记录完成状态。

## 唯一正式数据

数据入口datasets/current/data.yaml；1371 train / 171 val / 171 test，seed42。全部1761份原始JSON在datasets/annotation_source/json；48张争议和关联图片及对应JSON在datasets/quarantine。旧validation不用。当前YOLO标签由新版JSON生成，五类映射和冻结清单均已复核。

## 目录整理

原项目逻辑文件长度约31.71GB。清理10项旧副本／冗余ZIP后，可用磁盘空间实增25.49GB。详细删除和保留记录在reports/new_json_20261105/cleanup_record.json，最终目录占用在disk_after.json。参考模型、可用GPU环境、正式run、必要历史证据保留。C盘历史来源未修改。

## 运行

使用environment/.venv_gpu/Scripts/python.exe -B run_project.py status或verify-labels查看状态和复核JSON标签。train启动新的完整100轮实验；validate和predict默认加载当前正式best.pt。具体参数见交付README。baseline/start_training.ps1提供可见PowerShell入口。

## 解释边界与待补项

当前划分无完全相同解码图片或推断的原图／增强家族跨集合，但真实工件／打印过程ID未核实，相邻帧仍可能相关。只完成全量机器检查和10张画框抽查，不承诺所有语义标注绝对正确。Off_platform验证仅9个框。三号需确认16组标注分歧并提供过程分组ID，清单见交付member03_pending.md。

五号负责轻量检测头；六号负责统一评价／测速及冻结test评价；七号负责演示；八号负责统稿。已提供所需接口和材料，未替用户向成员发送消息。没有宣称同机测速、功耗测量或未经测试的部署导出。

reports/history与baseline/runs/history_35epochs_20261105为历史记录。本次没有恢复旧35轮，也没有把历史或smoke指标冒充正式结论。

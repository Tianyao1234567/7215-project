# IDAT7215 Topic 3 原始 YOLOv8n 基线

本仓库保存四号已完成的原始YOLOv8n基线及其报告材料。官方COCO初始化、完整100轮、640输入、batch16、workers0、SGD、seed42。训练耗时31.55分钟。它为五号轻量模型及六号统一评价提供对照。

验证171张、229个框：Precision **93.22%**，Recall **94.05%**，mAP50 **95.47%**，mAP50–95 **60.03%**。test保持未使用。

## 先看这里

- [每个目录做什么、结果在哪里](PROJECT_GUIDE.md)
- [四号作业与报告材料](reports/member04/README.md)
- [中文工作总结与结果解释](reports/member04/SUMMARY_ZH.md)
- [48张为什么隔离及三号对接](reports/member04/DATA_REVIEW_MEMBER03.md)
- [可直接转发的队友消息](TEAM_UPDATE.md)
- [完整数据和交付包 Release](https://github.com/Tianyao1234567/7215-project/releases/tag/member04-baseline-20261105)

## 数据版本

三号新版train共1761张及逐图JSON。32张来自16组同画面标注不一致的副本，另16张关联版本，合计48张保留隔离。本轮使用1713张，冻结1371 train / 171 validation / 171 test，旧validation619张不用。其余数据通过全量机器核对和10张画框抽查，不代表逐张语义验收。真实打印过程ID仍未核实。

JSON及冻结标签直接保存在仓库。约5.8GB的原始图片作为同仓库Release配套分包提供。普通git clone不包含图片，下载工具会核对分包SHA256、解压路径和图片身份。

## 在Windows上复现

使用Python3.10及兼容NVIDIA GPU环境。版本见[requirements.txt](requirements.txt)与[环境说明](environment/SETUP.md)。本机虚拟环境及全局Python不上传，其他电脑需自行重建环境。

```powershell
git clone https://github.com/Tianyao1234567/7215-project.git
cd 7215-project
py -3.10 -m venv environment/.venv_gpu
.\environment\.venv_gpu\Scripts\python.exe -m pip install --extra-index-url https://download.pytorch.org/whl/cu117 -r requirements.txt
.\environment\.venv_gpu\Scripts\python.exe tools/fetch_dataset.py
.\environment\.venv_gpu\Scripts\python.exe -B run_project.py verify-labels
.\environment\.venv_gpu\Scripts\python.exe -B run_project.py validate --output baseline/runs/validation_check
```

提供的验证/预测默认使用device0。使用新的输出目录以保留既有结果；完整训练入口为baseline/start_training.ps1，默认创建新run并使用官方初始化。当前best/last由baseline/current_model.json指向，路径相对仓库根目录。

## 分工和材料边界

五号负责论文轻量检测头与自身训练；六号负责统一精度/测速与最终test；七号负责演示；八号负责全组统稿。本仓库不宣称完成这些独立任务。四号295词方法、英文结果报告、436词贡献草稿和两页可编辑PPT集中于reports/member04。个人贡献提交前需本人核实。

Ultralytics提供模型、训练/评估引擎和内置绘图，许可文件见baseline/licenses。本项目实现JSON转换、审计、冻结数据整理、运行封装和交付工具，并使用AI辅助。RAM缓存与deterministic=True不保证逐位相同结果。当前validation也参与了选模，独立打印过程泛化尚未验证。

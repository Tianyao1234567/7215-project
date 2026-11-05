# 四号 YOLOv8n Baseline

更新：2026-11-02。项目根目录为本目录上一层。完整当前状态见../README.md、../PROGRESS_CURRENT.md。旧CPU阶段说明已保存至../reports/history，不代表当前GPU状态。

## 当前状态

本机RTX3080 GPU环境通过，13项回归测试通过；真实五类20train/10val、2epoch小样本训练保存best/last、日志、曲线并通过加载、验证、预测。真实run在runs/real_smoke_20261102/smoke_20261101T185410_489568Z/；预测样例conf0.25下0框，不能称作正式有效缺陷检测成果。

正式训练未完成：原始划分严重重复且无test、存在480组标签版本冲突，1/4/5尚未记录共同条件。所有smoke权重是工程测试；weights/yolov8n.pt是官方COCO初始化。二号参考best.pt不是四号独立训练结果。

## 本机运行（从项目根目录）

~~~powershell
.\environment\.venv_gpu\Scripts\python.exe -B .\run_project.py check
.\environment\.venv_gpu\Scripts\python.exe -B .\run_project.py tests
.\environment\.venv_gpu\Scripts\python.exe -B .\run_project.py smoke
~~~

smoke默认合成1类；如需重复真实小样本流程，使用已存在的真实测试配置/数据：

~~~powershell
.\environment\.venv_gpu\Scripts\python.exe -B .\run_project.py smoke --config baseline/configs/smoke.real_20261102.yaml --data datasets/real_smoke_20261102/data.yaml
~~~

每次运行建立独立时间戳目录。缓存和临时文件由项目入口限制到本项目内；不要直接调用含删除逻辑的原prepare_data。环境重建和依赖见../environment/SETUP.md及各run的requirements-lock.txt。evidence/requirements-tested.txt是首次CPU环境的历史锁定。

## 正式训练前的数据接口

3号交完整images/train,val,test与对应labels，data.yaml、类别映射、固定清单、版本和真实工件/过程分组。groups.csv两列image,group_id，image可为相对data根目录的图片路径；group_id须有事实依据，不为过检查编造。

机器审查与清单生成：

~~~powershell
.\environment\.venv_gpu\Scripts\python.exe -B .\diagnostics\run_scoped.py .\environment\.venv_gpu\Scripts\python.exe -B baseline/data_tools/check_label_fixed.py --data ACCEPTED_DATA --groups VERIFIED_GROUPS --require-test --report NEW_AUDIT_PATH
~~~

ACCEPTED_DATA等为待替换参数；当前无已验收的正式数据。check返回0表示机器检查通过，2表示发现错误；机器检查不能取代人工语义复核。prepare_data_fixed.py是只读审查，空标签合法保留；split_manifest_fixed.py只列出既有划分，不负责重新划分。正式标注维护由3号负责。

## 正式训练配置与命令

configs/baseline.provisional.yaml是待统一的100epoch、640、batch16、SGD、seed42提案，不能当已采用参数。1/4/5确认同一数据/划分、框架、预算、输入、初始化、优化器和增强后，生成agreed配置并真实记录protocol.status、agreement_record、dataset_version、dataset_sha256。

~~~powershell
.\environment\.venv_gpu\Scripts\python.exe -B .\run_project.py train --config AGREED_CONFIG --data ACCEPTED_DATA --groups VERIFIED_GROUPS
~~~

这些是待替换路径；未记录协议、无test/分组、数据审计失败或摘要不一致会停止。官方原始yolov8n.yaml构建并加载同源COCO初始化，不用二号best.pt初始化本次基线。训练只使用train与val，test交6号冻结后评价。

每个run保存requested_config、实际args、初始化来源、数据摘要/清单、环境/依赖、console.log、status、fit/results.csv和曲线、best/last、验证指标、预测与handoff.json。只有mode=formal且实际完成的run才作为最终基线结果。

## 验证与预测

从项目根目录运行，替换YOUR_RUN等占位参数，output使用新目录：

~~~powershell
.\environment\.venv_gpu\Scripts\python.exe -B .\run_project.py validate --weights baseline/runs/YOUR_RUN/fit/weights/best.pt --data ACCEPTED_DATA --output validation_new --imgsz 640 --batch 1
.\environment\.venv_gpu\Scripts\python.exe -B .\run_project.py predict --weights baseline/runs/YOUR_RUN/fit/weights/best.pt --source INPUT_IMAGE_OR_VIDEO --output predictions_new --imgsz 640 --conf 0.25
~~~

validate默认val；6号可显式--split test。预测保存画框图、YOLO TXT和JSON（像素xyxy、class_id、confidence）。完整演示归7号，统一mAP/延迟/FPS/参数/GFLOPs与对照实验归6号。

## 交付

4号正式best/last、配置、版本、数据来源/摘要、日志、曲线、基本验证预测、README与模块报告/PPT文字交1/6/7/8。5号负责轻量结构与独立训练，3号负责正式数据。开源、参考与AI协助如实记录于docs/THIRD_PARTY_AND_ASSISTANCE.md；个人贡献于docs/CONTRIBUTION_RECORD.md。

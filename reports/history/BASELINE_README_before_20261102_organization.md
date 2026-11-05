> 2026-11-01更新：工程已迁移至D:\Desktop\7215\project，3080 GPU完整smoke已通过。请优先使用上一层README.md和run_project.py。下文CPU环境描述为首次测试记录。

# IDAT7215 Topic 3 — Member 4 Baseline
Updated: 2026-11-01 (Asia/Shanghai).

**状态：训练工程已经通过 CPU 工程测试；真实 FDM Baseline 尚未训练完成。**
本包所有 runs/smoke_* 权重均为合成方框数据上的工程测试模型，只有1类，不得提交为5类缺陷检测正式成果。
weights/yolov8n.pt 是官方80类COCO初始化权重，也不是训练后的缺陷检测模型。

先看 docs/FIRST_ROUND_AUDIT.md 和 PROGRESS.md。代码注释为英文，说明为中文。
原始3个脚本在 originals/，只供对照，不要运行其中的删除逻辑。
sources/ 和用户原始附件未被修改。

## 1. 环境
优先复用已有匹配环境。实际测试：Python 3.11.15 / torch 2.5.1+cpu /
torchvision 0.20.1 / Ultralytics 8.2.103 / NumPy 1.26.4。
这是新建的隔离测试环境版本，并非已与5号确认的正式框架版本。
完整锁定记录：evidence/requirements-tested.txt；硬件与版本：evidence/environment-tested.json。
本包不包含虚拟环境。

若需单独建立 CPU 测试环境，在解压目录中执行（Windows PowerShell）：
~~~powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-cpu.txt
.\.venv\Scripts\python.exe check_environment.py
~~~
后续示例中的 python 替换为上述虚拟环境解释器，或先激活该环境。
GPU正式训练必须先确认 torch.cuda.is_available() 为 true。保留兼容的现有 CUDA/PyTorch；
缺少GPU版PyTorch时按官方适配安装，不要直接用 requirements-cpu.txt 覆盖已有GPU环境。
官方安装说明：https://pytorch.org/get-started/locally/

## 2. 复现工程测试
~~~powershell
python -m unittest discover -s tests -v
python tools/make_synthetic_fixture.py --output tests/new_smoke_fixture
python train_baseline.py --config configs/smoke.yaml --data tests/new_smoke_fixture/data.yaml
~~~
fixture目录必须是新目录，避免覆盖数据。也可直接使用包内 tests/synthetic_fixture/data.yaml；
已将该文件路径改为相对路径。每次训练自动使用独立时间戳目录，不覆盖已有run。
合成数据4张train、2张val、2张test，只有 synthetic_rectangle 一类。
smoke不使用test选模型。1个epoch、64像素、batch=2，仅验证工程，指标无FDM研究意义。

官方预训练初始化也已单独测通：
~~~powershell
python train_baseline.py --config configs/smoke.official.yaml --data tests/synthetic_fixture/data.yaml
~~~
包内 weights/yolov8n.pt 从官方 Ultralytics release 获取，来源及SHA256见
weights/yolov8n.source.json。若文件未随转交保留，执行以下命令重新获取（目标必须不存在）：
~~~powershell
python tools/fetch_official_weights.py --output weights/yolov8n.pt
~~~
source记录里的历史本地路径可不同；校验依据是来源URL、字节数与SHA256。

## 3. 验收3号真实数据（必须先拿到文件）
标准结构：
~~~text
dataset/
  data.yaml
  images/train/... images/val/... images/test/...
  labels/train/... labels/val/... labels/test/...
  groups.csv
~~~
配置格式参考 configs/data.example.yaml，但类别顺序须3号确认。
脚本统一将 data.yaml 的 path 相对于该YAML所在目录解释；
manifest中的相对图片路径相对于manifest所在目录解释。
支持子目录、jpg/jpeg/png/bmp/tif/tiff/webp及大小写扩展名。
图像与标签通过最后一层 images -> labels 映射并保留子目录，标签后缀为.txt。
不支持自动下载配置中的 download 指令，不执行数据提供方的代码。

groups.csv 两列：
~~~csv
image,group_id
images/train/part01_frame001.jpg,print_process_01
images/val/part02_frame001.jpg,print_process_02
images/test/part03_frame001.jpg,print_process_03
~~~
group_id必须对应真实工件/打印过程/原图及其增强图关系，不得为了通过检查人为编造独立ID。
关联信息无法取得时由3号/组长说明并决定可报告的实验范围，不能静默宣称无泄漏。

~~~powershell
python data_tools/check_label_fixed.py --data dataset/data.yaml --groups dataset/groups.csv --require-test --report evidence/data_v1_audit.json
python data_tools/prepare_data_fixed.py --root dataset --nc 5 --report evidence/data_v1_review.json
python data_tools/split_manifest_fixed.py --root dataset --output manifests_v1
~~~
check脚本返回0表示基础机器检查通过，2表示发现错误。
空标签合法保留；缺失标签单独报错，须3号确认是漏标还是负样本。
prepare脚本改为只读审查，输出review而不自动纠错/删除，避免破坏原始标注。
manifest脚本只是记录已有划分，不会重新分割。已有清单拒绝覆盖。
检测精确文件/解码像素重复；相似帧及工件关系依赖group_id和3号人工核实。
按组重新划分和正式标注修复仍由3号完成，本包没有擅自重划正式数据。

## 4. 正式Baseline（当前被阻塞）
先让1/4/5号确认同一实验协议，包括框架版本、同一数据SHA、
640等输入尺寸、训练epoch/batch、初始化、优化器、LR/增强、seed、AMP和停止规则。
configs/baseline.provisional.yaml 只是可编辑提案，100 epoch / batch16 / SGD等不是已批准配置。
确认后复制为 configs/baseline.agreed.yaml，并填写：
- protocol.status: agreed
- agreement_record: 实际组内决定的日期/负责人/沟通记录
- dataset_version 和 dataset_sha256：3号版本与本包audit产生的digest
- 相同Ultralytics版本；初始化的官方来源与SHA256
- train参数及device：实际商定值；显存不足须协调两个模型一起更改batch

~~~powershell
python train_baseline.py --mode formal --config configs/baseline.agreed.yaml --data dataset/data.yaml --groups dataset/groups.csv
~~~
未记录统一协议、数据审计失败、缺test/分组或数据摘要不一致时会停止，不会自动改为smoke或重新划分。
原始YOLOv8n从官方 yolov8n.yaml 构建并加载官方COCO参数；
不接受现有 best.pt/best_pre.pt 充当本次训练初始化。
正式训练只用train优化、val选模；给Ultralytics的实际训练配置里不包含test。
正式test比较交给6号，避免反复用test调参。

每个run保留：console.log / status.json / environment.json / requirements-lock.txt /
requested_config.json / dataset_audit.json / data.input.yaml / data.resolved.yaml /
train_images.txt / val_images.txt / initialization.json /
fit/args.yaml / fit/results.csv / fit/results.png / fit/weights/best.pt,last.pt /
validation_metrics.json / prediction.json / prediction图 / handoff.json。
fit/args.yaml记录框架最终接收的设置；正式报告以真实run为准。
时间戳为UTC，用户面对的截止日按香港/中国时间。
固定seed和确定性设置有助于复现，不保证跨硬件/框架位级一致。

## 5. 验证与预测接口
~~~powershell
python validate_baseline.py --weights runs/YOUR_RUN/fit/weights/best.pt --data dataset/data.yaml --output validation_new --device 0 --imgsz 640 --batch 1
python predict_baseline.py --weights runs/YOUR_RUN/fit/weights/best.pt --source dataset/images/val --output predictions_new --device 0 --imgsz 640 --conf 0.25
~~~
CPU测试将device写cpu。不要用smoke的1类权重去验证真实5类数据。
输出JSON使用像素 xyxy、class_id、confidence；保存画框图片和YOLO预测TXT。
validate默认val；6号冻结模型后可显式 --split test 进行单模型测试，
其完整公平对比、GFLOPs和同步测速仍使用6号自己的统一程序。
所有 output 参数用新目录。视频预测逐帧输出；长视频正式Demo由7号负责。

## 6. 交接与未完成项
- 1号：整个工程、README、配置与PROGRESS.md。
- 3号：data_tools修正版及修复说明；请在真实数据上正式验收并维护。
- 5号：统一协议模板；其轻量head实现不在此包。
- 6号：未来真实run的best.pt/handoff.json/data摘要/环境；本包smoke权重不可作比较结果。
- 7号：predict_baseline.py；正式FDM调用仍待真实权重。
- 8号：docs/BASELINE_REPORT_DRAFT.md、PPT_CONTENT.md及真实结果到位后的更新责任。
- 个人贡献：docs/CONTRIBUTION_RECORD.md，包含AI协助事实，不虚构个人手工完成内容。

13项数据测试已通过；随机初始化smoke重复2次，官方初始化smoke1次成功；
真实通用图片COCO推理、基础验证CLI均通过。
真实FDM数据验收、FDM smoke、正式GPU训练、正式best.pt及下游独立验收均未完成。

额外复现验证：将完整工程解压至另一个目录后，使用相同隔离解释器再次完成官方初始化smoke。日志见 evidence/relocation_reproduction.log。这是4号自测，不替代下游组员独立验收。

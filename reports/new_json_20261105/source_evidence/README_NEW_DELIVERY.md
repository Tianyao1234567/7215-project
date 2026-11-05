# IDAT7215：11月5日在线链接新版数据与 YOLOv8n 基线

本文件记录本轮实际处理。旧的 `IDAT7215_TrainOnly_811_20261105.zip` 来自此前的 yolo 目录，其清单不是本轮新版训练数据，请勿混用。

## 这次是否真的更新

下载位置：`D:\Desktop\7215\project\new`。

四包名称：`dataset-20261105T105219Z-1-001.zip` 至 `-004.zip`。

四个独立 ZIP 已安全解压合并，共 8,285 个文件、7,792,061,321 字节。读取各 ZIP 成员时完成 CRC 校验，逐文件 SHA256 记录见 extraction_manifest.json。

本次仅以交付 train 为候选数据，交付的旧 validation 没有用于训练数据重划分。

| 内容 | 与前两版 train 比较 |
|---|---|
| 1,761 张 JPG | 图片内容全部相同 |
| images/train 内 1,761 个 JSON | 新增的标注来源；转成框后，1,761 份均与旧标注不同 |
| labels/train 内 1,761 个 TXT | 仍与前两版逐字节相同 |
| images/labels 内 1,761 个 TXT | 429 个与 JSON 一致；1,332 个为空，不能直接用作训练标签 |

因此，新版确实包含新的人工交付标注，但旧 data.yaml 指向的 labels/train 没有同步更新，新导出的另一套 TXT 也有缺失。本轮以 JSON 为来源重新转换，没有覆盖或修改交付原件。

类别统一映射：

| ID | 训练类别 | JSON 中的名称 |
|---:|---|---|
| 0 | Cracking | Cracking |
| 1 | Layer_shifting | Layer shifting |
| 2 | Off_platform | off platform |
| 3 | Stringing | stringing |
| 4 | Warping | warping |

只统一大小写、空格和下划线所表示的同一类别；没有代替三号重新判断缺陷类别或重画框。

## 数据验收和划分

- 全部 1,761 张 train JPG 均能解码，实际尺寸与 JSON 一致（3072×2048）。
- JSON 与图片一一对应，均含有效 rectangle 标注，类别均能映射，坐标有限、宽高有效、无越界。
- 新 JSON 共 2,338 个框：Cracking 542、Layer_shifting 322、Off_platform 88、Stringing 474、Warping 912。
- 16 组完全相同的图片存在不同 JSON 框，共 32 份文件；没有擅自挑选某一版为真值。这些文件连同 16 张同前缀关联版本暂不进入训练，原件仍保留。
- 最终入选 1,713 张唯一图片；train 1,371、validation 171、test 171，seed=42，各集合均覆盖五类。
- 原图/增强图的同文件名前缀始终在同一集合；入选集不存在相同像素内容跨集合。
- group_id 是按文件名推断的图像家族，尚未取得已核实的真实工件/打印过程 ID。不能把它当成独立打印过程级评价。
- 已查看 ground_truth_review.jpg 中的 10 张样本（每类两张），框与可见缺陷区域对齐，未见类别映射或坐标缩放偏移。这不是人工逐张复审全部数据。
- 原 JSON 的 checked=false、review_status=pending 元数据保持不变；这些默认字段本身不能证明实际人工审核是否完成。

完整证据：NEW_DELIVERY_AUDIT.json、per_image_comparison.json、frozen_split_manifest.csv、VISUAL_REVIEW.json。

## 执行位置

当前 D 盘项目不在本会话可写范围内。本轮在本机可写工作区中执行，D 盘原 ZIP、旧数据、代码和环境均未改动。

本轮目录：

`C:\Users\Z1234\.codex\.chatgpt-projects\g-p-6aacb7113054819184d6120451354a0c\work\new_delivery_20261105_105219`

- received/dataset：四包合并的原始交付。
- dataset_train_only_811：只从 train 构建的正式训练输入与重新生成的 YOLO TXT。
- dataset_train_only_811/data.yaml：本轮训练配置引用的数据入口。
- .runtime：本轮进程专用缓存，不改全局 Python/Jupyter。
- runs：真实训练、验证、预测输出。

训练图片以同卷硬链接引用解压原图，不需要再占一整套图片的空间。压缩交付包只包含代码、标签、清单与审计材料，不重复包含数 GB 图片；原图来自用户已有四包。

## 训练任务

沿用已安装的 Python 3.10.11、torch 2.0.1+cu117、torchvision 0.15.2+cu117、ultralytics 8.2.103。RTX 3080 Laptop GPU 的 CUDA 矩阵运算和 NMS 已实测通过。

流程：20 train / 10 validation 的五类真实小样本训练 2 epoch → 检查有限 loss、best/last 保存、模型重载、验证、预测 → 重新从官方 COCO 权重初始化原始 YOLOv8n，启动 100 epoch 基线。

正式参数保存在 BASELINE_RUN_CONFIGURATION.json：imgsz=640、batch=8（本机显存 8GB）、SGD、seed=42、deterministic=true，其余增强和学习率参数随文件记录。采用进程内 RAM 图片缓存以提高读取速度；训练框架提示 RAM 缓存不能保证严格逐位确定性，因此不能把同 seed 解释为逐位复现承诺。

官方初始化权重 SHA256：

`f59b3d833e2ff32e194b5bb8e08d211dc7c5bdf144b90d2c8412c47ccfc83b36`

这是用户授权启动的本轮基线配置，不能冒充已由 1/4/5 号共同签字确认的实验协议。5号后续比较应使用同一冻结数据和对应参数。

test 不参与训练、选 epoch、阈值调节或本轮验证；留给冻结模型后的统一评估。

## 查询实际进度

先看 train_job_status.json 和 training.log，不要仅凭此 README 判断训练已完成。

- SMOKE_RESULT.json：小样本真实数据流程测试证据，不是正式精度。
- runs/yolov8n_new_json_baseline/results.csv：已完成 epoch 的真实指标。
- runs/yolov8n_new_json_baseline/weights/best.pt、last.pt：训练期间实际检查点。
- BASELINE_MODEL_HANDOFF.json：仅在 100 epoch 和最终重载验证全部完成后生成。

若训练进程仍在运行，不要重复启动。代码带 PID 检查以阻止同时启动同一任务。正式权重未产生之前，不得把 smoke 模型作为最终基线模型。

## 核心脚本

- extract_delivery.py：四包安全解压和逐文件记录。
- prepare_delivery.py：JSON 转换、逐图核查、前两版比较、分组排除、冻结 80/10/10、生成画框图。
- gpu_preflight.py：读取现有环境并做真实 GPU/NMS 测试。
- train_delivery.py：小样本验收与 100 epoch 原始 YOLOv8n 基线。

脚本输出相对于其所在目录，现有输入 ZIP 和 GPU Python 路径则指向本机 D 盘。本轮未执行 D 盘旧数据删除；后续应在本轮成果验证完成、且 D 盘可写时处理。

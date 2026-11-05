# 二号资料（按用户本次说明记录交付来源）

- yolo_dataset/：新放入的root yolo/yolo整体移至此处。2380张图、2380标签、data.yaml、2个旧缓存。它是数据集，不含新PT；原件内容未改。
- labels_received_20261102/labels/：新labels(1).zip的完整解压件，含2380标签和2缓存；源ZIP已校验后删除。
- reference_models/pre_train_model/：原pre_train_model ZIP的8个解压文件，包括best.pt、best_pre.pt、两个ONNX和原脚本/配置。保留原件，不用原硬编码脚本修改数据。

2380标签与三号交付逐字节相同；yolo_dataset中的4761个非缓存文件与三号相同，缓存亦一致。此处仍独立保存二号来源，不能把这些参考权重称为四号本次训练成果。

用户转述了少量人工标签→迭代训练→自动标注的流程；人工种子图片、各轮已有PT和当前标签的对应、伪标签参数仍待二号说明，不把口述数量写成已核实数量。

目录归属是接收/交付来源，权重具体作者和每轮实验仍需其确认。对比证据：../../diagnostics/NEW_MEMBER2_COMPARISON_20261102.json。

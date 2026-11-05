from ultralytics import YOLO

# 加载你刚刚训练出来的最优模型（注意检查路径，通常是 best.pt）
model = YOLO(r"e:\hku\IDAT7215\topic3\archive\FDM-3D-Printing-Defect-Dataset\data\best.pt")

# 导出为 ONNX 格式
model.export(format="onnx", imgsz=640, opset=12)
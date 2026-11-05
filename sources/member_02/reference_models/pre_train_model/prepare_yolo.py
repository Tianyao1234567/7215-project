import os
import random
import shutil
from pathlib import Path

# ================= 配置区域 =================
# 你的原始数据根目录（里面包含五个类别文件夹和导出的 labels 文件夹）
source_dir = Path(".")  # 注意把这里改成你的实际路径
# 输出的 YOLOv8 标准数据集目录
output_dir = Path("../yolo")
train_ratio = 0.8
random.seed(42)
classes = ["Cracking", "Layer_shifting", "Off_platform", "Stringing", "Warping"]
valid_data = []

# 1. 建立 labels 字典
label_dir = source_dir / "labels"
txt_dict = {}
if label_dir.exists():
    for f in os.listdir(label_dir):
        if f.endswith('.txt'):
            txt_dict[f] = label_dir / f

# 2. 遍历图片并配对
for cls in classes:
    img_dir = source_dir / cls
    if not img_dir.exists():
        continue
        
    count = 0
    for img_file in os.listdir(img_dir):
        if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
            img_path = img_dir / img_file
            target_txt = img_path.stem + ".txt"
            
            if target_txt in txt_dict:
                lbl_path = txt_dict[target_txt]
                if os.path.getsize(lbl_path) > 0:
                    valid_data.append((img_path, lbl_path, cls))
                    count += 1
    print(f"✅ {cls}: 找到 {count} 张图")

print(f"\n总计有效图片: {len(valid_data)} 张")

# 3. 划分并直接复制到你建好的文件夹中
random.shuffle(valid_data)
train_size = int(len(valid_data) * train_ratio)

def copy_files(data_list, split):
    for img_path, lbl_path, cls in data_list:
        # 加前缀防重名
        new_img_name = f"{cls}_{img_path.name}"
        new_lbl_name = f"{cls}_{lbl_path.name}"
        
        # 直接存入你建好的文件夹（如果文件夹不存在，脚本依然会抛出错误，请确保路径正确）
        shutil.copy2(img_path, output_dir / "images" / split / new_img_name)
        shutil.copy2(lbl_path, output_dir / "labels" / split / new_lbl_name)

print(f"正在复制文件到 {output_dir.absolute()} ...")
copy_files(valid_data[:train_size], "train")
copy_files(valid_data[train_size:], "val")
print("🎉 分发完成！请打开你的文件夹检查。")
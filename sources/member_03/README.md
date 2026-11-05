# 三号交付（独立于二号保留）

- scripts/：三号原prepare_data(1).py、check_label(1).py、split_manifest(1).py，未修改。重复且字节相同的再次上传副本已合并保留一份。
- original_cache_files/dataset/labels/：四个原ZIP内的两个旧缓存，仅用于原件留存，不作为训练输入。
- 完整图片、标签和data.yaml仍在项目根目录的datasets/received_20261102/dataset。保留先前给用户的查找路径；这是三号原始交付，不是二号与三号混合后的数据。

原prepare_data包含删除图片逻辑，不应直接运行。四号已提供临时修正版于baseline/data_tools，正式数据处理质量和维护仍由三号验收负责。

四个源分包和三号转发的yolo.zip在逐项校验后删除；图片、标注、配置、缓存原件及SHA清单保留。三号交付的标签与二号新交付2380份标签完全相同，未见正式纠错版本；不据此认定其从未做过检查。

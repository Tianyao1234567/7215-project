# GPU与迁移状态（2026-11-01）
根目录：D:\Desktop\7215\project

| 项目 | 状态 | 实际证据 |
|---|---|---|
| 既有项目复制 | 已验收 | diagnostics/migration_manifest.json：214个文件全部SHA一致 |
| 原始用户放入的四个文件 | 未修改 | 根目录保留；未执行其中的删除程序 |
| 原有系统/Jupyter环境 | 未修改 | original_environment_preserved.log中的原版本仍为torch2.0.1+cu117、NumPy2.2.6、Ultralytics8.4.10、OpenCV4.13.0.90 |
| 项目环境 | 已验收 | environment/.venv_gpu，仅本目录安装覆盖依赖 |
| CUDA前向/反向 | 已验收 | project_gpu_environment_verified.log |
| NumPy桥接和CUDA NMS | 已验收 | 同一GPU检查记录 |
| YOLO完整GPU smoke | 已验收 | run status=completed、handoff.json、best/last、验证和预测输出 |
| 新环境数据回归测试 | 已验收 | project_gpu_regression_tests.log：13/13 |
| 真实FDM数据 | 被阻塞 | 尚未收到完整图/框标签/data.yaml/分组 |
| 正式训练协议 | 进行中 | provisional配置仍未与1/5号商定 |
| 正式FDM best.pt | 被阻塞 | 没有正式FDM run |

成功的GPU run：baseline/runs/smoke_20261101T082115_071946Z。
使用合成方框4张train、2张val、官方COCO初始化、320像素、batch2、1epoch。
该权重不是正式5类缺陷模型；合成测试指标不能写进FDM比较表。

第一次GPU调用的50秒外层命令限制在最终验证期间断开了输出；
当时已保存权重，但run的status为failed。未将“进程返回看似0”作为成功证据。
改为文件日志和独立完成状态跟踪后，完整run实际完成，保留两次记录便于追溯。

已消除“GPU不可用”这一旧阻塞；剩余优先级：
3号真实数据交付 → 核验与真实smoke → 1/4/5号冻结协议 → 正式GPU训练 → 下游验收。

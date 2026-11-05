# 项目目录与输出位置

当前正式实验是原始YOLOv8n的100轮基线，run_id为`yolov8n_newjson_from_official_20261105_213549`。本文件说明每个文件夹的职责，避免将早期试验或来源材料当作当前结果。

| 目录或文件 | 内容与用途 | 使用建议 |
|---|---|---|
| baseline/ | 四号训练、验证、预测、JSON转换和公共运行环境封装 | 当前模型代码入口 |
| baseline/configs/ | 正式100轮协议及历史配置 | 当前使用new_json_100epochs.json |
| baseline/weights/ | 官方COCO初始化权重及来源 | 用于新训练初始化 |
| baseline/runs/yolov8n_newjson_from_official_20261105_213549/ | 本次正式权重、100轮CSV、日志、曲线、独立验证与预测 | 正式实验的原始证据 |
| baseline/runs/其他目录 | 小样本或旧35轮训练 | 历史流程证据，不作正式成绩 |
| baseline/data_tools、tests、tools | 数据接口工具、13项回归检查及辅助工具 | 工程检查 |
| datasets/current/ | 唯一正式数据，固定1371/171/171划分及data.yaml | 所有模型复用同一清单 |
| datasets/annotation_source/json/ | 三号新版train全部1761份原始JSON | 标注来源保留 |
| datasets/quarantine/ | 48张隔离图片、JSON、转换标签与排除理由 | 保留备份，不参加本轮训练 |
| datasets/IMAGE_PACKAGES.json | Release图片分包URL、大小与SHA256 | 配合下载工具使用 |
| deliverables/member04_baseline/ | 面向6/7/8号的完整小包，含best/last、代码、配置、指标、预测、报告及PPT | 下游交付入口 |
| deliverables/history/ | 早期ZIP和历史交付 | 不覆盖当前版本 |
| reports/member04/ | 四号中文总结、英文报告/方法、436词贡献草稿、两页PPT、图表和48张说明 | 写作业优先读取 |
| reports/new_json_20261105/ | 转换审计、冻结身份、预检、清理记录及正式结果JSON | 核对事实与来源 |
| reports/history/ | 早期结论和整理前版本 | 历史存档 |
| diagnostics/ | 数据与环境诊断、整理/验证脚本和日志 | 排查问题时使用 |
| sources/ | 已收到的参考模型、原始脚本和来源索引 | 参考权重不作为本次训练成果 |
| new/ | 原始交付中的少量脚本和旧清单 | 历史输入，非正式入口 |
| tools/ | 仓库数据下载、发布和复核工具 | 先看各工具帮助 |
| environment/ | 环境说明；本机.venv_gpu留本地 | 换机器需重建兼容环境 |
| .runtime/、.chart-data-* | 缓存、临时文件与发布中间件 | 不上传源码仓库 |
| run_project.py | status、check、tests、verify-labels、train、validate、predict | 统一命令入口 |

## 当前结果在哪里

- [正式权重](baseline/runs/yolov8n_newjson_from_official_20261105_213549/weights/)及[完整日志](baseline/runs/yolov8n_newjson_from_official_20261105_213549/training.log)。
- [独立验证指标](deliverables/member04_baseline/validation_metrics.json)，[训练CSV](baseline/runs/yolov8n_newjson_from_official_20261105_213549/results.csv)。
- [训练/验证曲线](deliverables/member04_baseline/plots/)，[五类预测与错误示例](deliverables/member04_baseline/predictions/)。
- [我的报告材料](reports/member04/README.md)，[给三号的数据说明](reports/member04/DATA_REVIEW_MEMBER03.md)。
- 完整交付ZIP和1761张图片分包在[Release](https://github.com/Tianyao1234567/7215-project/releases/tag/member04-baseline-20261105)。虚拟环境、私有聊天原件、教师文件原件和缓存保留本地。

## 写作业如何使用

先读reports/member04/SUMMARY_ZH.md了解本部分做了什么；将baseline_method_300words.md与baseline_report.md作为四号英文材料交八号；贡献草稿由本人确认；图表和PPT数字均来自validation_metrics.json。论文参考值、旧35轮结果和smoke结果不作为本次正式成绩。test未使用，真实打印过程分组仍未核实。

历史JSON中保留原始机器路径以记录来源。当前代码与下载入口按克隆后的项目根目录解析，冻结CSV和标签的字节身份不改变。

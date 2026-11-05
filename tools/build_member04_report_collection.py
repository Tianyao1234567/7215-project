"""Create member04 writing material, a complete directory guide and team handoff notes."""
import sys,json,csv,shutil
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'baseline'))
import new_json_common as c
OUT=ROOT/'reports/member04';OUT.mkdir(parents=True,exist_ok=True)
PACKAGE=ROOT/'deliverables/member04_baseline';run=c.resolve_project_path(c.load(c.BASE/'current_model.json')['run_directory'])
metrics=c.load(PACKAGE/'validation_metrics.json');audit=c.load(c.REPORT/'current_data_audit.json');ex=c.load(ROOT/'datasets/quarantine/exclusion_details.json')
repo='https://github.com/Tianyao1234567/7215-project';tag='member04-baseline-20261105'
def write(path,text):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.strip()+'\n',encoding='utf-8')
for name in ['baseline_report.md','baseline_method_300words.md','personal_contribution.md','presentation_notes.md','references.md','validation_metrics.json','classes.json','config.json','environment.json','text_word_counts.json','member04_baseline_slides.pptx']:
    shutil.copy2(PACKAGE/name,OUT/name)
figures=OUT/'figures';figures.mkdir(exist_ok=True)
for i in (1,2):
    source=ROOT/f'diagnostics/presentation_build/final-v5/verified-slide-{i}.png'
    if source.is_file():shutil.copy2(source,figures/f'slide_{i}.png')
for name in ['results.png','PR_curve.png','confusion_matrix.png','confusion_matrix_normalized.png']:
    candidates=[run/'independent_validation'/name,run/name]
    src=next((p for p in candidates if p.is_file()),None)
    if src:shutil.copy2(src,figures/name)
rows=[];comparisons=[]
for group_id,g in enumerate(ex['excluded_conflicts'],1):
    members=[]
    for r in g['variants']:
        rows.append({'filename':r['stem']+'.jpg','reason':'same_pixel_conflicting_annotations','conflict_group':group_id,'family':r['family'],'class_ids':','.join(map(str,r['classes'])),'image_sha256':r['image_sha256'],'included_in_training':False,'note':'Same decoded image has different JSON rectangles; neither variant declared authoritative.'})
        members.append({'filename':r['stem']+'.jpg','normalized_boxes':r['boxes'],'xyxy_pixel_boxes':[[int(b[0]),round((b[1]-b[3]/2)*3072,3),round((b[2]-b[4]/2)*2048,3),round((b[1]+b[3]/2)*3072,3),round((b[2]+b[4]/2)*2048,3)] for b in r['boxes']]})
    comparisons.append({'group_id':group_id,'pixel_sha256':g['pixel_sha256'],'variants':members})
for r in ex['excluded_related']:
    rows.append({'filename':r['stem']+'.jpg','reason':'related_filename_family_precaution','conflict_group':'','family':r['family'],'class_ids':','.join(map(str,r['classes'])),'image_sha256':r['image_sha256'],'included_in_training':False,'note':'Related filename variant conservatively excluded; not independently proven mislabeled.'})
assert len(rows)==48 and len(comparisons)==16
with (OUT/'quarantine_48.csv').open('w',encoding='utf-8-sig',newline='') as f:
    writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
c.save(OUT/'conflict_group_comparison.json',comparisons)
pct=lambda v:f'{100*v:.2f}%'
table='| 类别 | Precision | Recall | AP50 | AP50–95 |\n|---|---:|---:|---:|---:|\n'
for m in metrics['per_class']:table+=f"| {m['name']} | {pct(m['precision'])} | {pct(m['recall'])} | {pct(m['mAP50'])} | {pct(m['mAP50_95'])} |\n"
summary=f'''# 四号原始 YOLOv8n 基线总结

本目录集中保存四号已完成的工作、真实实验结果和可供作业使用的材料。编写小组报告时先读本文件，再使用英文方法正文、结果报告和图表。个人贡献仍需本人核实后提交。

## 已完成的工作

1. 复核三号新版train中的1761张照片及逐图JSON，重建YOLO标签；原labels/train仍为旧标签，另一处导出TXT不完整，本轮以JSON转换结果为准。
2. 保留48张争议及关联样本的隔离备份，复用1713张有效图片的冻结划分：1371 train、171 validation、171 test。seed42，旧validation619张不参与。
3. 使用官方COCO yolov8n.pt从epoch1完整训练100轮，resume=False，patience=0。imgsz640、batch16、workers0、SGD、AMP和RAM缓存。训练耗时31.55分钟，终端可见并保存完整日志。
4. 从磁盘重载新best.pt，实际验证171张图片、229个框，生成五类代表预测及误检漏检示例。test保持未使用。
5. 保留代码、配置、版本、初始化来源、权重、清单、曲线、指标和最短命令，并完成项目目录整理。

## 正式验证结果

总体Precision93.22%、Recall94.05%、mAP50 95.47%、mAP50–95 60.03%。这是当前validation上的正式结果，validation也用于选择best checkpoint。mAP50应按指标原名报告，不能改写为整体分类准确率。

{table}

判断：这是一份可以交给轻量模型和演示工作的原始基线。较严格的定位指标仍有提升空间。Off_platform仅9个验证框；Warping的AP50–95为41.17%。真实工件/打印过程ID未核实，相邻帧可能相关，因此当前结果不能证明对独立打印过程的泛化能力。没有进行统一FPS测速、功耗测量或部署导出。

## 数据验收的边界

1713张通过全量格式、配对、坐标、哈希和冻结划分核对，并对五类共10张进行了画框抽查。这支持本轮使用，但不能证明每一张语义标注绝对正确。48张不是全部被证明标错：32张来自16组同画面不同框的副本，另16张是相关版本，为避免任取真值和关联泄漏而统一隔离。用户已选择保留隔离备份。

## 输出和证据

- 正式run：[训练目录](../../baseline/runs/{run.name}/)，含training.log、results.csv、weights/best.pt、weights/last.pt。
- [机器可读验证指标](validation_metrics.json)、[本部分英文报告](baseline_report.md)、[约300词方法正文](baseline_method_300words.md)。
- [436词个人贡献草稿](personal_contribution.md)、[两页PPT](member04_baseline_slides.pptx)、[讲稿](presentation_notes.md)。
- [图表](figures/)、[五类及错误预测](../../deliverables/member04_baseline/predictions/)、[三号数据说明](DATA_REVIEW_MEMBER03.md)。
- 完整审计：[reports/new_json_20261105](../new_json_20261105/)。记录中的旧机器绝对路径属于实验来源，当前运行入口按克隆后的仓库根目录解析。

## 分工交接

四号提供原始基线及这些材料。五号负责论文轻量检测头和自己的训练；六号负责统一精度与速度比较、冻结后的test评价；七号负责演示；八号将本部分材料纳入全组报告。Ultralytics提供原始模型、训练和评估框架，本项目实现JSON转换、审计、冻结数据整理、训练封装及交付工具，并使用了AI辅助。
'''
write(OUT/'SUMMARY_ZH.md',summary)
example=comparisons[0]
data_note=f'''# 给三号的数据复核说明

本轮范围是新版train的1761张照片及JSON，不包括旧validation619张。1713张已通过现有机器检查和10张抽样画框复核，可用于当前基线；这不代表其余图片都经过逐张人工语义验收。

## 48张为什么隔离

- 16组完全相同画面，每组2份文件，共32张。相同解码像素对应的JSON矩形位置、大小或框数不一致，不能自动选其中一份为真值，也不能把两套框平均或拼接。
- 另有16张同文件名前缀的关联版本。它们不一定标错；为统一排除争议家族而暂时不参与当前划分。
- 合计48张，占1761张的2.73%。用户已决定保持排除、保留隔离备份。当前训练、validation和test均不包含这48张，因此无须为此重训。

## 一个真实例子

{example['variants'][0]['filename']} 与 {example['variants'][1]['filename']} 的解码像素相同，但各自JSON转换得到的像素xyxy矩形为：

```json
{json.dumps(example['variants'],ensure_ascii=False,indent=2)}
```

完整16组对照见[conflict_group_comparison.json](conflict_group_comparison.json)，全部48张逐文件名单见[quarantine_48.csv](quarantine_48.csv)。原始图片和JSON位于datasets/quarantine，原始1761份JSON另存于datasets/annotation_source/json。图片随仓库的配套Release数据包提供。

## 本轮如何对接

请全组继续沿用冻结的1713张和1371/171/171划分，不要重新随机分组或把隔离图直接放回本轮。无需重传整套照片。后续如确认这些争议的最终标注，另开数据版本维护；如有真实工件、批次或打印过程ID，请补充，供后续核查划分独立性使用。
'''
write(OUT/'DATA_REVIEW_MEMBER03.md',data_note)
write(OUT/'README.md','''# 四号作业和报告材料入口

这里是四号的部分，不是全组最终报告。写作业和准备展示时优先阅读以下文件。

| 文件 | 用途 |
|---|---|
| SUMMARY_ZH.md | 中文工作总结、数据版本、实验结果和限制 |
| baseline_report.md | 本部分英文报告、结果讨论、图注和引用 |
| baseline_method_300words.md | 295词方法与训练设置，可交八号统稿 |
| personal_contribution.md | 436词个人贡献草稿，提交前由本人核实 |
| member04_baseline_slides.pptx | 两页可编辑PPT素材 |
| presentation_notes.md | 对应展示讲稿和数字 |
| validation_metrics.json | 原始精度、逐类指标和实际验证设置 |
| config.json、environment.json | 训练协议与版本信息 |
| figures/ | 训练曲线、验证图和两页PPT预览 |
| DATA_REVIEW_MEMBER03.md | 48张隔离的原因与三号对接说明 |
| quarantine_48.csv | 全部48张逐文件清单 |
| conflict_group_comparison.json | 16组同画面标注差异的精确矩形记录 |
| references.md | 本部分引用来源 |

实际权重和完整预测位于../../deliverables/member04_baseline，原始正式run位于../../baseline/runs。全组展示安排与最终提交由原分工负责，本目录只陈述四号已完成且有证据的部分。
''')
write(ROOT/'reports/README.md','''# Reports 目录入口

- [member04](member04/README.md)：四号当前总结、英文方法/报告、个人贡献、PPT、指标和三号数据说明。写作业先读这里。
- [new_json_20261105](new_json_20261105/)：原始数据审计、转换、环境预检、正式结果与清理记录。
- [history](history/)：先前版本和旧结论，仅作历史证据，不能作为当前训练入口。

四号当前正式结果：100轮，validation mAP50 95.47%、mAP50–95 60.03%，test未使用。完整项目目录说明见根目录PROJECT_GUIDE.md。
''')
team=f'''# 可转发给队友的项目更新

项目已整理到 {repo} 。四号原始YOLOv8n基线已从官方COCO权重完整训练100轮，验证Precision93.22%、Recall94.05%、mAP50 95.47%、mAP50–95 60.03%。代码、权重、配置、日志、曲线、预测和四号报告/PPT材料均有明确入口。写作业先看 reports/member04/README.md。

三号新版train共1761张。1713张通过目前的机器验收及10张画框抽查，用于冻结的1371/171/171划分；这不是逐张人工语义复审。48张已经隔离保留：16组同画面不同框共32张，另16张关联版本，后者不一定标错。本轮先排除，不用重传整套图片，也不用为此重训。具体文件和差异在reports/member04/DATA_REVIEW_MEMBER03.md及quarantine_48.csv。test尚未用于评价或调参，真实打印过程ID仍需补充。

五号请按论文全文实现轻量检测头，并对齐同一划分及训练条件；六号接统一评价和测速；七号接推理演示；八号接四号方法、报告、贡献草稿和两页PPT。各自成果按原分工继续推进。

图片数据和完整交付ZIP在同仓库Release：{repo}/releases/tag/{tag} 。普通git clone下载源码及结果，图片用 tools/fetch_dataset.py 拉取配套数据包。目录和输出位置见PROJECT_GUIDE.md。
'''
write(ROOT/'TEAM_UPDATE.md',team)
guide=f'''# 项目目录与输出位置

当前正式实验是原始YOLOv8n的100轮基线，run_id为`{run.name}`。本文件说明每个文件夹的职责，避免将早期试验或来源材料当作当前结果。

| 目录或文件 | 内容与用途 | 使用建议 |
|---|---|---|
| baseline/ | 四号训练、验证、预测、JSON转换和公共运行环境封装 | 当前模型代码入口 |
| baseline/configs/ | 正式100轮协议及历史配置 | 当前使用new_json_100epochs.json |
| baseline/weights/ | 官方COCO初始化权重及来源 | 用于新训练初始化 |
| baseline/runs/{run.name}/ | 本次正式权重、100轮CSV、日志、曲线、独立验证与预测 | 正式实验的原始证据 |
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

- [正式权重](baseline/runs/{run.name}/weights/)及[完整日志](baseline/runs/{run.name}/training.log)。
- [独立验证指标](deliverables/member04_baseline/validation_metrics.json)，[训练CSV](baseline/runs/{run.name}/results.csv)。
- [训练/验证曲线](deliverables/member04_baseline/plots/)，[五类预测与错误示例](deliverables/member04_baseline/predictions/)。
- [我的报告材料](reports/member04/README.md)，[给三号的数据说明](reports/member04/DATA_REVIEW_MEMBER03.md)。
- 完整交付ZIP和1761张图片分包在[Release]({repo}/releases/tag/{tag})。虚拟环境、私有聊天原件、教师文件原件和缓存保留本地。

## 写作业如何使用

先读reports/member04/SUMMARY_ZH.md了解本部分做了什么；将baseline_method_300words.md与baseline_report.md作为四号英文材料交八号；贡献草稿由本人确认；图表和PPT数字均来自validation_metrics.json。论文参考值、旧35轮结果和smoke结果不作为本次正式成绩。test未使用，真实打印过程分组仍未核实。

历史JSON中保留原始机器路径以记录来源。当前代码与下载入口按克隆后的项目根目录解析，冻结CSV和标签的字节身份不改变。
'''
write(ROOT/'PROJECT_GUIDE.md',guide)
readme=f'''# IDAT7215 Topic 3 原始 YOLOv8n 基线

本仓库保存四号已完成的原始YOLOv8n基线及其报告材料。官方COCO初始化、完整100轮、640输入、batch16、workers0、SGD、seed42。训练耗时31.55分钟。它为五号轻量模型及六号统一评价提供对照。

验证171张、229个框：Precision **93.22%**，Recall **94.05%**，mAP50 **95.47%**，mAP50–95 **60.03%**。test保持未使用。

## 先看这里

- [每个目录做什么、结果在哪里](PROJECT_GUIDE.md)
- [四号作业与报告材料](reports/member04/README.md)
- [中文工作总结与结果解释](reports/member04/SUMMARY_ZH.md)
- [48张为什么隔离及三号对接](reports/member04/DATA_REVIEW_MEMBER03.md)
- [可直接转发的队友消息](TEAM_UPDATE.md)
- [完整数据和交付包 Release]({repo}/releases/tag/{tag})

## 数据版本

三号新版train共1761张及逐图JSON。32张来自16组同画面标注不一致的副本，另16张关联版本，合计48张保留隔离。本轮使用1713张，冻结1371 train / 171 validation / 171 test，旧validation619张不用。其余数据通过全量机器核对和10张画框抽查，不代表逐张语义验收。真实打印过程ID仍未核实。

JSON及冻结标签直接保存在仓库。约5.8GB的原始图片作为同仓库Release配套分包提供。普通git clone不包含图片，下载工具会核对分包SHA256、解压路径和图片身份。

## 在Windows上复现

使用Python3.10及兼容NVIDIA GPU环境。版本见[requirements.txt](requirements.txt)与[环境说明](environment/SETUP.md)。本机虚拟环境及全局Python不上传，其他电脑需自行重建环境。

```powershell
git clone {repo}.git
cd 7215-project
py -3.10 -m venv environment/.venv_gpu
.\\environment\\.venv_gpu\\Scripts\\python.exe -m pip install --extra-index-url https://download.pytorch.org/whl/cu117 -r requirements.txt
.\\environment\\.venv_gpu\\Scripts\\python.exe tools/fetch_dataset.py
.\\environment\\.venv_gpu\\Scripts\\python.exe -B run_project.py verify-labels
.\\environment\\.venv_gpu\\Scripts\\python.exe -B run_project.py validate --output baseline/runs/validation_check
```

提供的验证/预测默认使用device0。使用新的输出目录以保留既有结果；完整训练入口为baseline/start_training.ps1，默认创建新run并使用官方初始化。当前best/last由baseline/current_model.json指向，路径相对仓库根目录。

## 分工和材料边界

五号负责论文轻量检测头与自身训练；六号负责统一精度/测速与最终test；七号负责演示；八号负责全组统稿。本仓库不宣称完成这些独立任务。四号295词方法、英文结果报告、436词贡献草稿和两页可编辑PPT集中于reports/member04。个人贡献提交前需本人核实。

Ultralytics提供模型、训练/评估引擎和内置绘图，许可文件见baseline/licenses。本项目实现JSON转换、审计、冻结数据整理、运行封装和交付工具，并使用AI辅助。RAM缓存与deterministic=True不保证逐位相同结果。当前validation也参与了选模，独立打印过程泛化尚未验证。
'''
write(ROOT/'README.md',readme)
shutil.copy2(PACKAGE/'requirements.txt',ROOT/'requirements.txt')
c.save(OUT/'REPORT_MATERIALS_INDEX.json',{'scope':'member04_only','run_id':run.name,'method_words':295,'contribution_words':436,'test_used':False,'source_metrics':str((PACKAGE/'validation_metrics.json').relative_to(ROOT)),'repo':repo,'release_tag':tag})
print('Member04 report collection, folder guide, quarantine explanations and team message prepared.')


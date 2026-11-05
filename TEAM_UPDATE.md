# 可转发给队友的项目更新

项目已整理到 https://github.com/Tianyao1234567/7215-project 。四号原始YOLOv8n基线已从官方COCO权重完整训练100轮，验证Precision93.22%、Recall94.05%、mAP50 95.47%、mAP50–95 60.03%。代码、权重、配置、日志、曲线、预测和四号报告/PPT材料均有明确入口。写作业先看 reports/member04/README.md。

三号新版train共1761张。1713张通过目前的机器验收及10张画框抽查，用于冻结的1371/171/171划分；这不是逐张人工语义复审。48张已经隔离保留：16组同画面不同框共32张，另16张关联版本，后者不一定标错。本轮先排除，不用重传整套图片，也不用为此重训。具体文件和差异在reports/member04/DATA_REVIEW_MEMBER03.md及quarantine_48.csv。test尚未用于评价或调参，真实打印过程ID仍需补充。

五号请按论文全文实现轻量检测头，并对齐同一划分及训练条件；六号接统一评价和测速；七号接推理演示；八号接四号方法、报告、贡献草稿和两页PPT。各自成果按原分工继续推进。

图片数据和完整交付ZIP在同仓库Release：https://github.com/Tianyao1234567/7215-project/releases/tag/member04-baseline-20261105 。普通git clone下载源码及结果，图片用 tools/fetch_dataset.py 拉取配套数据包。目录和输出位置见PROJECT_GUIDE.md。

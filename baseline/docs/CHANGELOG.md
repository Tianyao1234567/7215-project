# 2026-11-01 修复与测试记录
原版3份脚本完整保留在 originals/。本轮未对真实dataset执行任何清理。
修正版是基于原函数职责与调用接口扩展，并非取代3号正式数据交付。
新增公共 dataset_audit.py 是为避免三个工具和训练入口各自使用不一致的标签/路径规则。

| 原版问题 | 影响 | 修复与兼容性 | 实测 |
|---|---|---|---|
| prepare_data对无标签或0字节标签调用os.remove | 丢失唯一原图，删除有效负样本 | 保留prepare_data(img_folder,label_folder)，现在返回只读review；不删除、不夹断、不猜测标注 | 空标签/缺标分别识别，原文件SHA未变 |
| check_label只检查5列且只执行train | 非数值、非法类别、无效框、val/test错误漏过 | 保留check_dataset接口，新增全split CLI；ID整数/范围/有限值/正宽高/框边界/重复框/坏图检查 | 数值边界等13项测试全通过 |
| 所有脚本只支持jpg/JPG | PNG/JPEG等遗漏 | 统一大小写扩展名与递归子目录 | PNG/JPG夹杂及同stem标签碰撞被识别 |
| split_manifest只是枚举现有目录 | 有清单不能证明分割正确 | 明确inventory_only；排序、SHA、train/val/test、绝对路径、拒绝覆盖 | 同输入两份manifest逐字一致，重复输出报错 |
| 没有重复/关联泄漏检查 | train/val/test结果虚高 | 文件SHA/解码像素SHA、同标签路径碰撞、groups.csv跨split检查 | 精确重复与跨组泄漏被拒绝 |
| 原脚本无机器可追溯报告 | 只凭终端数量难验收 | JSON包含逐图问题、每类框数/图片数、负样本数、数据指纹 | CLI实际运行并保存evidence |
| Ultralytics默认用户目录在本环境缺失 | import失败 | runtime_setup.py把YOLO/Matplotlib缓存放到项目本地 | 初次失败保留日志，修复后3次训练成功 |
| 正式配置尚未统一 | 无法公平比较 | provisional模板与协议/数据摘要校验；不悄悄开正式实验 | formal_protocol_guard.log确认拒绝未商定协议 |

未自动修复：漏标/错框的语义、近似重复、关联工件信息、真实数据重新划分。
这些需要3号验收和正式维护；本轮代码级修复不表示3号工作已经完成。
临时兼容补丁/环境脚本属于4号工程支持；组内后续仍按原分工。

额外发现的zip脚本问题：
- prepare_yolo.py只80/20随机分图、丢弃空标、无test、不创建目录；
  同名标签在统一labels目录可能配错；与正式分组划分不能混用。
- pt2onnx.py写死他人E盘路径。
这些参考脚本未被用于正式数据处理/训练，也没有替2/3号擅自转换完整数据。


## 2026-11-02 — source comparison and organization
Member 2 newly received labels (2380) match member 3 delivery byte-for-byte; received YOLO directory is data, not new weights. Receipts separated under sources/member_02 and sources/member_03; member 3 raw dataset path retained. Eight verified extracted source archives removed at user request; SHA256 and operation journals retained. Root/baseline READMEs and current progress rewritten. Post-organization 13 tests and CUDA checks passed. Formal baseline remains blocked by label revisions, leakage and agreed protocol.

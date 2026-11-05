> 2026-11-02最新状态：4个数据ZIP已解压，真实五类GPU小样本训练已完成。正式划分未通过（483/619验证图与训练重复，且缺test）。请先看 DATA_ACCEPTANCE_20261102.md 与 PROGRESS_CURRENT.md。下文“尚未收到数据”为2026-11-01历史记录。

# IDAT7215 Topic 3 — 本机工作入口
更新时间：2026-11-01（中国/香港时间）。

工作根目录：D:\Desktop\7215\project
后续项目文件、环境覆盖包、缓存、临时文件和运行结果均写入此目录。
原有Python/Jupyter和驱动保持不变，仅读取并复用GPU版PyTorch。
当前没有收到完整真实FDM数据集，正式Baseline仍未训练完成。

## 本轮已完成
- 214个既有工程/参考/交付文件复制迁移，逐文件SHA256一致，旧源目录保留。
- 找到原有Python 3.10.11，torch 2.0.1+cu117、torchvision 0.15.2+cu117。
- CUDA实际前向、反向、NumPy转换、GPU NMS通过。
- 原始YOLOv8n一轮GPU工程训练、保存best/last、重新加载、验证和预测全部通过。
- GPU环境13项数据工具回归测试通过。
- 成功run：baseline/runs/smoke_20261101T082115_071946Z/
- 此run只有合成方框1类，不能作为正式5类FDM模型或研究指标。

## 固定启动方式
在此目录打开PowerShell，执行：
~~~powershell
python -B run_project.py check
python -B run_project.py tests
python -B run_project.py smoke
~~~
run_project.py会调用 environment/.venv_gpu/Scripts/python.exe，不依赖当前python默认指向哪个环境。
不必使用Jupyter，也不必改系统默认Python。
check验证GPU计算；smoke通常需要一分钟左右完成本机首次预热和所有验证/绘图，不要在训练刚保存权重时提前关闭。
以run中的status.json为completed、handoff.json和预测输出存在为完成依据。

收到真实数据并与1/5号确定同一正式协议后：
~~~powershell
python -B run_project.py train --config baseline/configs/baseline.agreed.yaml --data dataset/data.yaml --groups dataset/groups.csv
~~~
上例的agreed配置和真实dataset目前尚未提供，不要只修改状态来绕过正式实验核查。
predict和validate也支持同一入口，例如：
~~~powershell
python -B run_project.py predict --weights baseline/runs/YOUR_RUN/fit/weights/best.pt --source dataset/images/val --output predictions_new
python -B run_project.py validate --weights baseline/runs/YOUR_RUN/fit/weights/best.pt --data dataset/data.yaml --output validation_new
~~~
输出目录选新名称；不要把工程测试的1类权重用作正式5类模型。

## 为什么之前Notebook能用、普通进程不行
本轮查到三个具体差异：
1. 最初的任务测试用Python 3.11 CPU版torch，不能代表用户原有Python 3.10 GPU环境。
2. 当前任务子进程没有USERPROFILE，原有torch 2.0.1在导入时因无法解析用户目录而失败。
   现在只在项目子进程恢复实际用户目录信息，并将项目可配置缓存/临时目录指向根目录内.runtime。
3. 原有GPU环境装有NumPy 2.2.6，torch 2.0.1出现NumPy二进制兼容警告。
   在本目录的新虚拟环境内覆盖为NumPy 1.26.4，同时固定Ultralytics 8.2.103和OpenCV 4.10.0.84。
   原有全局NumPy、Ultralytics和OpenCV均未降级或删除；见diagnostics/original_environment_preserved.log。

NVML/nvidia-smi曾初始化失败，但CUDA Driver API和PyTorch实际GPU计算均通过；
因此没有据此要求重装驱动。后续以真实GPU训练结果判断可用性。

## 目录
| 位置 | 内容 |
|---|---|
| baseline/ | 训练工程、修正版、保留的原版、配置、日志、测试权重 |
| baseline/dataset/ | 已建空目录；也可直接把完整dataset放根目录 |
| reference_inputs/ | 之前实际取得的原始项目附件、教师PDF和群聊图片 |
| reference_models/ | 原pre_train_model解压件，属于参考权重 |
| diagnostics/ | 迁移清单、GPU定位记录、检查程序、完整GPU测试日志 |
| environment/.venv_gpu/ | 项目局部环境；只读复用原有GPU torch |
| deliverables/ | 历史交付ZIP；文件名带First_Round的是迁移前历史版本 |
| 根目录的三个原脚本和zip | 用户自行放入的原件，本轮未修改 |

用户把3号完整dataset目录或压缩包放在根目录即可，不需要手动逐张搬图或重新划分。
根目录原prepare_data脚本包含删除逻辑，保留用于对照；执行检查请用baseline/data_tools中的fixed版本。

原版README和第一次核查报告保留了当时CPU环境的历史信息；
当前设备状态、启动命令以本文件及GPU_MIGRATION_STATUS.md为准。

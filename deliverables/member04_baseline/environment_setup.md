# Project GPU environment
Verified on 2026-11-01:
- Base Python: C:\Users\Z1234\AppData\Local\Programs\Python\Python310\python.exe
- Project Python: D:\Desktop\7215\project\environment\.venv_gpu\Scripts\python.exe
- torch 2.0.1+cu117 and torchvision 0.15.2+cu117 are READ from the existing base installation.
- Project-local overlays: numpy 1.26.4, ultralytics 8.2.103, opencv-python 4.10.0.84.
- Pillow 12.0.0 and PyYAML 6.0.3 were available from the base environment.
- GPU: NVIDIA GeForce RTX 3080 Laptop GPU, 8192 MiB.
- CUDA forward/backward, NumPy bridge, NMS and full YOLO smoke passed.

This environment was created with --system-site-packages to reuse the working GPU stack.
It depends on the existing Python310 installation and is not a self-contained portable environment.
No base packages were removed or upgraded. Do not delete the base Python installation while using it.

For this machine, if only the project environment needs reconstruction:
1. Run the existing Python310 with -B -m venv --system-site-packages environment/.venv_gpu
   through diagnostics/run_scoped.py so temporary directories remain under this project.
2. Using the new project Python, install with --no-deps:
   numpy==1.26.4 ultralytics==8.2.103 opencv-python==4.10.0.84
3. Run python -B run_project.py check, then tests and smoke.
All installation commands must run inside the project and use the scoped runner.
Do not run pip against the existing global Python.

A different computer must install compatible GPU torch/torchvision separately; follow:
https://pytorch.org/get-started/previous-versions/
No driver update was performed for this task.

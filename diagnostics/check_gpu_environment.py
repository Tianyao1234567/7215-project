"""Read-only Python/CUDA diagnosis plus a real CUDA forward/backward if available."""
import importlib.util,json,os,sys,traceback
report={"python":sys.executable,"version":sys.version,"prefix":sys.prefix,
        "environment":{k:os.environ.get(k) for k in ("CUDA_PATH","CUDA_VISIBLE_DEVICES","NVIDIA_VISIBLE_DEVICES","CONDA_PREFIX")},
        "modules":{k:bool(importlib.util.find_spec(k)) for k in ("torch","ultralytics","ipykernel","jupyter")}}
try:
    import torch
    report.update(torch=torch.__version__,torch_file=torch.__file__,torch_cuda=torch.version.cuda,
                  cuda_available=torch.cuda.is_available(),device_count=torch.cuda.device_count())
    if torch.cuda.is_available():
        report["gpu_name"]=torch.cuda.get_device_name(0)
        x=torch.randn(256,256,device="cuda",requires_grad=True)
        loss=(x@x.T).square().mean()
        loss.backward()
        torch.cuda.synchronize()
        report["cuda_forward_backward_passed"]=bool(torch.isfinite(loss).item() and torch.isfinite(x.grad).all().item())
        report["device"]=str(x.device)
        import numpy as np
        report["numpy_version"]=np.__version__
        report["torch_numpy_bridge_passed"]=bool(torch.from_numpy(np.ones((2,2),dtype=np.float32)).numpy().sum()==4)
        import torchvision
        boxes=torch.tensor([[0,0,10,10],[1,1,9,9],[20,20,30,30]],dtype=torch.float32,device="cuda")
        scores=torch.tensor([0.9,0.8,0.7],device="cuda")
        report["cuda_nms_indices"]=torchvision.ops.nms(boxes,scores,0.5).tolist()
        report["cuda_nms_passed"]=report["cuda_nms_indices"]==[0,2]
    elif torch.version.cuda:
        try:
            torch.cuda.init()
        except Exception as error:
            report["cuda_init_error"]=str(error)
except Exception as error:
    report["torch_error"]=str(error)
    report["torch_traceback"]=traceback.format_exc()
try:
    import ctypes
    cuda=ctypes.WinDLL("nvcuda.dll")
    version=ctypes.c_int()
    report["driver_api_get_version_result"]=cuda.cuDriverGetVersion(ctypes.byref(version))
    report["driver_api_version"]=version.value
    report["driver_api_cuInit_result"]=cuda.cuInit(0)
except Exception as error:
    report["driver_api_error"]=str(error)
print(json.dumps(report,ensure_ascii=False,indent=2))

raise SystemExit(0 if report.get("cuda_forward_backward_passed") and report.get("torch_numpy_bridge_passed") and report.get("cuda_nms_passed") else 2)

"""Runtime-check user-supplied reference models; never labels them as our training."""
import sys, json, traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import runtime_setup
import numpy as np
import torch
import ultralytics
from ultralytics import YOLO
import onnx
import onnxruntime as ort
from data_tools.dataset_audit import write_json
torch.set_num_threads(2)
root=Path(sys.argv[1])
out=Path(sys.argv[2]);out.mkdir(parents=True,exist_ok=True)
sample=Path(ultralytics.__file__).parent/"assets"/"bus.jpg"
rows=[]
for name in ("best.pt","best_pre.pt"):
    row={"file":name,"version_under_test":ultralytics.__version__,"image":str(sample),"is_fdm_accuracy_test":False}
    try:
        model=YOLO(str(root/name))
        result=model.predict(str(sample),imgsz=640,device="cpu",verbose=False,save=True,project=str(out),name=Path(name).stem)[0]
        row.update(loaded=True,predict_passed=True,names=model.names,
                   parameters=sum(p.numel() for p in model.model.parameters()),
                   detections=len(result.boxes),finite_boxes=bool(torch.isfinite(result.boxes.data).all()))
    except Exception as e:
        row.update(loaded=False,error=str(e),traceback=traceback.format_exc())
    rows.append(row)
for name in ("best.onnx","best_pre.onnx"):
    row={"file":name}
    try:
        m=onnx.load(str(root/name));onnx.checker.check_model(m)
        opts=ort.SessionOptions();opts.intra_op_num_threads=2;opts.inter_op_num_threads=1
        session=ort.InferenceSession(str(root/name),sess_options=opts,providers=["CPUExecutionProvider"])
        inp=session.get_inputs()[0]
        dims=[d if isinstance(d,int) else v for d,v in zip(inp.shape,[1,3,640,640])]
        values=session.run(None,{inp.name:np.zeros(dims,dtype=np.float32)})
        row.update(onnx_checker=True,forward_passed=True,input_shape=inp.shape,
                   output_shapes=[list(v.shape) for v in values],finite=all(bool(np.isfinite(v).all()) for v in values),
                   metadata={p.key:p.value for p in m.metadata_props},
                   group_convs=[{"name":n.name,"group":a.i} for n in m.graph.node if n.op_type=="Conv"
                                for a in n.attribute if a.name=="group" and a.i>1])
    except Exception as e:
        row.update(forward_passed=False,error=str(e),traceback=traceback.format_exc())
    rows.append(row)
write_json(out/"runtime_checks.json",rows)
print(json.dumps(rows,ensure_ascii=False,indent=2))

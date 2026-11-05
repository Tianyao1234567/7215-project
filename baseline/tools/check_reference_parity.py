import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import runtime_setup
import torch,numpy as np,onnxruntime as ort
from ultralytics import YOLO
torch.set_num_threads(2)
root=Path(sys.argv[1]); rows=[]
x=np.random.default_rng(42).random((1,3,640,640),dtype=np.float32)
for base in ("best","best_pre"):
    model=YOLO(str(root/(base+".pt"))).model.float().eval()
    with torch.inference_mode(): y=model(torch.from_numpy(x))
    if isinstance(y,tuple): y=y[0]
    y=y.numpy()
    opts=ort.SessionOptions();opts.intra_op_num_threads=2
    session=ort.InferenceSession(str(root/(base+".onnx")),sess_options=opts,providers=["CPUExecutionProvider"])
    z=session.run(None,{session.get_inputs()[0].name:x})[0]
    delta=np.abs(y-z)
    rows.append({"pair":base,"input":"seed42 random tensor, not FDM accuracy evaluation","shape":list(y.shape),
                 "maximum_absolute_difference":float(delta.max()),"mean_absolute_difference":float(delta.mean()),
                 "allclose_rtol_1e-3_atol_1e-3":bool(np.allclose(y,z,rtol=1e-3,atol=1e-3))})
Path(sys.argv[2]).write_text(json.dumps(rows,indent=2),encoding="utf8")
print(json.dumps(rows))

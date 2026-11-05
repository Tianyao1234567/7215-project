"""Basic validation interface; member 6 owns the final comparative evaluation."""
import runtime_setup
import argparse
from pathlib import Path
import yaml
from ultralytics import YOLO
from data_tools.dataset_audit import audit_yaml, load_data_yaml, write_json

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weights",required=True)
    p.add_argument("--data",required=True)
    p.add_argument("--output",required=True)
    p.add_argument("--device",default="cpu")
    p.add_argument("--imgsz",type=int,default=640)
    p.add_argument("--batch",type=int,default=1)
    p.add_argument("--split",choices=["val","test"],default="val")
    a=p.parse_args()
    out=Path(a.output).resolve()
    out.mkdir(parents=True,exist_ok=False)
    audit=audit_yaml(a.data,require_test=a.split=="test")
    write_json(out/"dataset_audit.json",audit)
    if not audit["passed"]: raise ValueError("Dataset failed audit")
    root,names,splits=load_data_yaml(a.data)
    manifest=out/"images.txt"
    manifest.write_text("".join(i.as_posix()+"\n" for i in splits[a.split]),encoding="utf8")
    # Ultralytics expects train and val fields even for explicit test evaluation.
    data={"path":str(root),"names":names,"train":str(manifest),"val":str(manifest),a.split:str(manifest)}
    dp=out/"data.resolved.yaml"; dp.write_text(yaml.safe_dump(data),encoding="utf8")
    model=YOLO(a.weights)
    if list(model.names.values())!=names: raise ValueError("Weight classes do not match data.yaml")
    metrics=model.val(data=str(dp),split=a.split,imgsz=a.imgsz,batch=a.batch,device=a.device,
                      workers=0,project=str(out),name="metrics",plots=True)
    write_json(out/"metrics.json",metrics.results_dict)
if __name__=="__main__":
    main()

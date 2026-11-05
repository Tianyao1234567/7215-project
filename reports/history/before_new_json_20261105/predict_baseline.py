"""Minimal model interface for member 7; images or videos, no GUI."""
import runtime_setup
import argparse
from pathlib import Path
from ultralytics import YOLO
from data_tools.dataset_audit import write_json

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--weights",required=True)
    p.add_argument("--source",required=True)
    p.add_argument("--output",default="predictions")
    p.add_argument("--device",default="cpu")
    p.add_argument("--imgsz",type=int,default=640)
    p.add_argument("--conf",type=float,default=0.25)
    a=p.parse_args()
    if Path(a.output).exists(): raise FileExistsError("Choose a new output directory")
    model=YOLO(a.weights)
    results=model.predict(a.source,device=a.device,imgsz=a.imgsz,conf=a.conf,
                          save=True,save_txt=True,save_conf=True,project=a.output,name="rendered",stream=True)
    rows=[]
    for frame,result in enumerate(results):
        rows.append({"image":result.path,"frame_index":frame,"coordinate_format":"xyxy_pixels",
                     "detections":[{"box":b.xyxy[0].tolist(),"class_id":int(b.cls[0]),
                                    "confidence":float(b.conf[0])} for b in result.boxes]})
    write_json(Path(a.output)/"detections.json",{"names":model.names,"results":rows})
if __name__=="__main__":
    main()

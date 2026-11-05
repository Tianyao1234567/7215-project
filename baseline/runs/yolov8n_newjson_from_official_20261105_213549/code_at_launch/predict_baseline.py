"""Predict images and save class IDs, confidences and pixel xyxy boxes as JSON."""
import new_json_common as c
import argparse
from pathlib import Path

def serialize(result):
    items=[]
    for box in result.boxes:
        cls=int(box.cls.item());items.append({'class_id':cls,'class_name':c.NAMES[cls],'confidence':float(box.conf.item()),'xyxy_pixels':[float(x) for x in box.xyxy[0].tolist()]})
    return {'image_id':Path(result.path).stem,'source':str(result.path),'image_width':int(result.orig_shape[1]),'image_height':int(result.orig_shape[0]),'box_format':'xyxy pixels in original image; x1,y1,x2,y2','detections':items}
def predict(weights,source,output,conf=.25):
    from ultralytics import YOLO
    c.quiet_integrations();output=Path(output)
    if output.exists():raise FileExistsError(f'Use a new output directory: {output}')
    model=YOLO(str(weights));rows=[]
    for result in model.predict(source=str(source),stream=True,imgsz=640,device=0,conf=conf,iou=.7,save=True,project=str(output.parent),name=output.name,exist_ok=False,verbose=False):rows.append(serialize(result))
    value={'weights':str(weights),'weights_sha256':c.sha(weights),'confidence_threshold':conf,'NMS_iou':.7,'classes':c.NAMES,'images':rows}
    c.save(output/'predictions.json',value);return value

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--weights',required=True);ap.add_argument('--source',required=True);ap.add_argument('--output',required=True);ap.add_argument('--conf',type=float,default=.25);a=ap.parse_args();predict(a.weights,a.source,a.output,a.conf)
if __name__=='__main__':main()

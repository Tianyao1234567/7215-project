"""Reload a saved baseline checkpoint and evaluate an explicitly chosen frozen split."""
import new_json_common as c
import argparse
from pathlib import Path

def evaluate(weights,split='val',output=None,final_test=False):
    if split=='test' and not final_test:raise ValueError('Final test requires explicit --final-test after model selection is frozen.')
    from ultralytics import YOLO
    c.quiet_integrations()
    output=Path(output or c.BASE/'runs/independent_validation')
    model=YOLO(str(weights))
    observed={}
    def collect(validator):
        observed.update(images=int(validator.seen),objects_per_class=[int(v) for v in validator.nt_per_class],images_per_class=[int(v) for v in validator.nt_per_image])
    model.add_callback('on_val_end',collect)
    metrics=model.val(data=str(c.DATA),split=split,imgsz=640,batch=16,device=0,workers=0,conf=.001,iou=.7,max_det=300,half=False,plots=True,save_json=False,project=str(output.parent),name=output.name,exist_ok=False,verbose=True)
    expected=c.load(c.REPORT/'current_data_audit.json')
    assert observed['images']==sum(r['split']==split for r in c.manifest())
    assert observed['objects_per_class']==[expected['box_counts_by_split'][split][n] for n in c.NAMES]
    assert observed['images_per_class']==[expected['class_image_counts'][split][n] for n in c.NAMES]
    class_metrics=[]
    positions={int(cls):i for i,cls in enumerate(metrics.box.ap_class_index)}
    for cls,name in enumerate(c.NAMES):
        if cls in positions:
            p,r,a50,a=map(float,metrics.box.class_result(positions[cls]))
        else:p=r=a50=a=0.
        class_metrics.append({'class_id':cls,'name':name,'precision':p,'recall':r,'mAP50':a50,'mAP50_95':a})
    value={'run_id':model.ckpt.get('train_args',{}).get('name',Path(weights).parent.parent.name),'evaluated_China':c.now(),'weights':str(Path(weights).resolve()),'weights_sha256':c.sha(weights),'data':str(c.DATA),'split':split,'images':observed['images'],'observed_dataset_counts':observed,'settings':{'imgsz':640,'batch':16,'device':0,'workers':0,'confidence_for_AP':.001,'NMS_iou':.7,'max_det':300,'half':False},'overall':{k:float(v) for k,v in metrics.results_dict.items()},'per_class':class_metrics,'speed_ms_from_validator':{k:float(v) for k,v in metrics.speed.items()},'speed_limitation':'Validator timing only; not member 06 unified batch-one synchronized deployment benchmarking.','precision_recall_definition':'Ultralytics detection metrics select the maximum mean F1 operating point from validation curves; AP integrates the confidence curve.','manifest_semantic_sha256':c.SEMANTIC_SHA,'plots_directory':str(metrics.save_dir),'test_used':split=='test'}
    c.save(Path(metrics.save_dir)/('validation_metrics.json' if split=='val' else 'test_metrics.json'),value)
    return value

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--weights',required=True);ap.add_argument('--split',choices=['val','test'],default='val');ap.add_argument('--output');ap.add_argument('--final-test',action='store_true');args=ap.parse_args()
    evaluate(args.weights,args.split,args.output,args.final_test)
if __name__=='__main__':main()



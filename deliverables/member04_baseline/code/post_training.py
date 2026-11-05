"""Run independent checkpoint validation and export deterministic validation examples."""
import new_json_common as c
import csv,json,subprocess,sys,time
from pathlib import Path

def iou(a,b):
    x=max(0,min(a[2],b[2])-max(a[0],b[0]));y=max(0,min(a[3],b[3])-max(a[1],b[1]))
    inter=x*y;area=lambda q:max(0,q[2]-q[0])*max(0,q[3]-q[1])
    return inter/max(area(a)+area(b)-inter,1e-12)
def ground_truth(path,w,h):
    rows=[]
    for line in path.read_text(encoding='utf-8-sig').splitlines():
        if not line.strip():continue
        cls,x,y,bw,bh=map(float,line.split());rows.append({'class_id':int(cls),'xyxy_pixels':[(x-bw/2)*w,(y-bh/2)*h,(x+bw/2)*w,(y+bh/2)*h]})
    return rows

def export_predictions(run):
    import torch
    from ultralytics import YOLO
    from predict_baseline import serialize
    out=run/'validation_predictions';out.mkdir(parents=True,exist_ok=True)
    best=run/'weights/best.pt';target=out/'error_analysis.json'
    if target.is_file() and c.load(target).get('weights_sha256')==c.sha(best):return c.load(target)
    model=YOLO(str(best));assert [model.names[i] for i in range(5)]==c.NAMES
    model_info={'unfused_parameters':sum(p.numel() for p in model.model.parameters()),'class_names':model.names}
    rows=[];representatives={};error_candidates={'false_positive':[],'false_negative':[]}
    for result in model.predict(source=str(c.DATA.parent/'images/val'),stream=True,imgsz=640,device=0,conf=.25,iou=.7,verbose=False,save=False):
        row=serialize(result);gt=ground_truth(c.DATA.parent/'labels/val'/(row['image_id']+'.txt'),row['image_width'],row['image_height'])
        unmatched=set(range(len(gt)));tp=[];fp=[]
        for idx,pred in enumerate(row['detections']):
            matches=[(iou(pred['xyxy_pixels'],gt[j]['xyxy_pixels']),j) for j in unmatched if pred['class_id']==gt[j]['class_id']]
            overlap,j=max(matches,default=(0,None))
            if j is not None and overlap>=.5:unmatched.remove(j);tp.append({'prediction':idx,'ground_truth':j,'iou':overlap,'class_id':pred['class_id']})
            else:fp.append(idx)
        row.update({'ground_truth':gt,'true_positive_matches':tp,'false_positive_prediction_indices':fp,'false_negative_ground_truth_indices':sorted(unmatched)})
        rows.append(row)
        for cls in sorted({g['class_id'] for g in gt}):
            key=(not any(t['class_id']==cls for t in tp),row['image_id'])
            if cls not in representatives or key<representatives[cls]['key']:representatives[cls]={'key':key,'result':result,'row':row}
        for category,count in [('false_positive',len(fp)),('false_negative',len(unmatched))]:
            if count:
                error_candidates[category].append({'count':count,'result':result,'row':row})
                error_candidates[category].sort(key=lambda x:(-x['count'],x['row']['image_id']))
                error_candidates[category]=error_candidates[category][:3]
    assert len(rows)==171 and len(representatives)==5
    index=[]
    for cls,item in sorted(representatives.items()):
        filename=f'class_{cls}_{c.NAMES[cls]}.jpg';item['result'].save(filename=str(out/filename))
        index.append({'kind':'class_representative','class_id':cls,'class_name':c.NAMES[cls],'image_id':item['row']['image_id'],'file':filename,'has_matched_prediction_for_requested_class':not item['key'][0]})
    for category,items in error_candidates.items():
        for i,item in enumerate(items,1):
            filename=f'{category}_{i}_{item["row"]["image_id"]}.jpg';item['result'].save(filename=str(out/filename))
            index.append({'kind':category,'image_id':item['row']['image_id'],'file':filename,'unmatched_count':item['count']})
    total_fp=sum(len(r['false_positive_prediction_indices']) for r in rows);total_fn=sum(len(r['false_negative_ground_truth_indices']) for r in rows);total_tp=sum(len(r['true_positive_matches']) for r in rows)
    report={'run_id':run.name,'weights_sha256':c.sha(best),'split':'val','images':171,'confidence_threshold':.25,'NMS_iou':.7,'class_aware_matching_iou':.5,'matching':'Greedy descending-confidence same-class IoU match, one prediction per ground truth','true_positive_boxes':total_tp,'false_positive_boxes':total_fp,'false_negative_boxes':total_fn,'examples':index,'model_info':model_info,'test_used':False,'limitation':'Example error counts use fixed conf0.25 and IoU0.5; precision and recall in validation_metrics.json follow the Ultralytics F1 curve operating point. Class examples illustrate outputs and are not an independent performance estimate.'}
    c.save(out/'predictions.json',{'box_format':'xyxy_pixels on original image','classes':c.NAMES,'weights_sha256':c.sha(best),'images':rows})
    c.save(target,report);return report

def main():
    model=c.current_model();run=Path(model['run_directory']);verified=c.load(run/'training_verified.json')
    assert verified['status']=='100_epochs_verified' and verified['csv_rows']==100
    status=c.load(run/'status.json');status.update({'status':'independent_validation','updated_China':c.now()});c.save(run/'status.json',status);c.save(c.BASE/'current_training_status.json',status)
    val_dir=run/'independent_validation';metrics_file=val_dir/'validation_metrics.json'
    if not metrics_file.is_file():
        subprocess.run([sys.executable,'-B','-u',str(c.BASE/'evaluate_baseline.py'),'--weights',str(run/'weights/best.pt'),'--split','val','--output',str(val_dir)],cwd=c.ROOT,check=True)
    metrics=c.load(metrics_file);assert metrics['weights_sha256']==verified['best_sha256'] and metrics['images']==171 and not metrics['test_used']
    predictions=export_predictions(run)
    c.save(run/'post_training_verified.json',{'status':'passed','China':c.now(),'validation_metrics':str(metrics_file),'prediction_analysis':str(run/'validation_predictions/error_analysis.json'),'best_reloaded_from_disk':True,'test_used':False})
    print(json.dumps({'validation':metrics['overall'],'per_class':metrics['per_class'],'errors_at_conf025':{k:predictions[k] for k in ['true_positive_boxes','false_positive_boxes','false_negative_boxes']}},indent=2),flush=True)
if __name__=='__main__':main()

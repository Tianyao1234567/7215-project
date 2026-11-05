"""Small real-data smoke training and conservative batch-memory acceptance."""
import new_json_common as c
from pathlib import Path
import os,shutil,time,gc,json

def main():
    rows=c.assert_dataset();target=c.ROOT/'datasets/resource_smoke_20261105';picked=[]
    for split,each in [('train',4),('val',2)]:
        candidates=sorted((r for r in rows if r['split']==split),key=lambda r:r['image']);seen=set()
        for cls in range(5):
            for row in [r for r in candidates if str(cls) in r['class_ids'].split(',') and r['image'] not in seen][:each]:
                seen.add(row['image']);picked.append(row)
                for kind in ['image','label']:
                    src=c.DATA.parent/row[kind];dst=target/row[kind];dst.parent.mkdir(parents=True,exist_ok=True)
                    if not dst.exists():os.link(src,dst)
    (target/'data.yaml').write_text('path: '+json.dumps(target.as_posix())+'\ntrain: images/train\nval: images/val\nnc: 5\nnames: '+json.dumps(c.NAMES)+'\n',encoding='utf-8')
    import torch
    from ultralytics import YOLO
    torch.set_num_threads(4);c.quiet_integrations();os.chdir(c.INITIAL.parent)
    history=c.load(c.REPORT/'source_evidence/BASELINE_RUN_CONFIGURATION.json')
    settings=history['settings'].copy();settings.update({'epochs':1,'batch':16,'workers':0,'cache':'ram','close_mosaic':0,'resume':False,'plots':False})
    run_id='resource_smoke_'+time.strftime('%Y%m%d_%H%M%S')
    started=time.time();torch.cuda.reset_peak_memory_stats()
    model=YOLO(str(c.INITIAL))
    model.train(data=str(target/'data.yaml'),project=str(c.BASE/'runs'),name=run_id,exist_ok=False,**settings)
    run=Path(model.trainer.save_dir);best=run/'weights/best.pt';assert best.is_file()
    peak=torch.cuda.max_memory_allocated();total=torch.cuda.get_device_properties(0).total_memory
    assert peak<total*.8,f'Batch 16 leaves insufficient headroom: {peak}/{total}'
    reloaded=YOLO(str(best));metrics=reloaded.val(data=str(target/'data.yaml'),split='val',imgsz=640,batch=16,workers=0,device=0,plots=False,project=str(run),name='reload_validation',verbose=False)
    prediction=reloaded.predict(source=str(target/picked[0]['image']),imgsz=640,device=0,conf=.25,verbose=False)
    final=history.copy();final.update({'status':'user_authorized_baseline_configuration_not_team_agreement','data_yaml':str(c.DATA),'initialization_path':str(c.INITIAL),'frozen_manifest_file_sha256':c.sha(c.MANIFEST),'resource_choice':'Batch16 passed real-data training/save/reload/validation/prediction and CUDA peak allocation headroom; workers0 retained for stable Windows loading. Share this fixed protocol with member05.'})
    final['settings']=history['settings'].copy();final['settings'].update({'epochs':100,'batch':16,'workers':0,'resume':False,'patience':0})
    c.save(c.BASE/'configs/new_json_100epochs.json',final)
    result={'status':'passed','smoke_run':str(run),'train_images':sum(r['split']=='train' for r in picked),'val_images':sum(r['split']=='val' for r in picked),'epochs':1,'batch':16,'workers':0,'peak_cuda_allocated_bytes':peak,'vram_bytes':total,'seconds':time.time()-started,'reloaded_best_validation':{k:float(v) for k,v in metrics.results_dict.items()},'sample_prediction_boxes':len(prediction[0].boxes),'is_formal_result':False,'environment':c.environment()}
    c.save(c.REPORT/'resource_preflight.json',result);print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()

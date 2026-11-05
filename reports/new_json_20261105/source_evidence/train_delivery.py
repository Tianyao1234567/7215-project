"""Run a real-data GPU smoke test, then start the original YOLOv8n baseline."""
import prepare_delivery as scope
import csv
from datetime import datetime,timezone,timedelta
import gc
import json
import math
import os
from pathlib import Path
import shutil
import sys
import time
import traceback

ROOT=scope.ROOT
STATUS=ROOT/'train_job_status.json'
START=time.time()
os.environ['CUBLAS_WORKSPACE_CONFIG']=':4096:8'
os.environ['OMP_NUM_THREADS']='4'
os.environ['MKL_NUM_THREADS']='4'


def state(status,**details):
    value={'status':status,'pid':os.getpid(),'updated_China':datetime.now(timezone(timedelta(hours=8))).isoformat(timespec='seconds'),
           'elapsed_seconds':round(time.time()-START,1),**details}
    scope.save(STATUS,value)
    print('JOB_STATUS '+json.dumps(value,ensure_ascii=False),flush=True)


def make_smoke_dataset(manifest,classes):
    target=ROOT/'smoke_dataset'
    for split,wanted,each in [('train',20,4),('val',10,2)]:
        available=sorted((r for r in manifest if r['split']==split),key=lambda r:r['image'])
        picked=[];seen=set()
        for cls in range(classes):
            candidates=[r for r in available if cls in [int(v) for v in r['class_ids'].split(',')] and r['image'] not in seen]
            for row in candidates[:each]:
                picked.append(row);seen.add(row['image'])
        for row in available:
            if len(picked)>=wanted:break
            if row['image'] not in seen:picked.append(row);seen.add(row['image'])
        picked=picked[:wanted]
        for row in picked:
            image=scope.DATASET/row['image'];label=scope.DATASET/row['label']
            image_out=target/'images'/split/image.name;label_out=target/'labels'/split/label.name
            image_out.parent.mkdir(parents=True,exist_ok=True);label_out.parent.mkdir(parents=True,exist_ok=True)
            if not image_out.exists():os.link(image,image_out)
            shutil.copyfile(label,label_out)
    data='path: '+json.dumps(target.as_posix())+'\ntrain: images/train\nval: images/val\nnc: 5\nnames: '+json.dumps(scope.NAMES)+'\n'
    (target/'data.yaml').write_text(data,encoding='utf-8')
    return target/'data.yaml'


def run():
    import psutil
    lock=ROOT/'train_job.lock.json'
    if lock.exists():
        previous=json.loads(lock.read_text(encoding='utf-8'))
        if psutil.pid_exists(previous['pid']):
            proc=psutil.Process(previous['pid'])
            if any(str(Path(__file__).resolve()).casefold()==str(arg).casefold() for arg in proc.cmdline()):
                raise RuntimeError(f'Training job is already running with PID {previous["pid"]}')
    scope.save(lock,{'pid':os.getpid(),'script':str(Path(__file__).resolve())})
    prepared=json.loads((ROOT/'preparation_status.json').read_text(encoding='utf-8'))
    if prepared['status']!='completed':raise RuntimeError('Data preparation is incomplete')
    review=json.loads((ROOT/'VISUAL_REVIEW.json').read_text(encoding='utf-8'))
    if review['status']!='sampled_review_passed':raise RuntimeError('Sampled visual review has not passed')
    preflight=json.loads((ROOT/'gpu_preflight.json').read_text(encoding='utf-8'))
    audit=json.loads((ROOT/'NEW_DELIVERY_AUDIT.json').read_text(encoding='utf-8'))
    with (ROOT/'frozen_split_manifest.csv').open(encoding='utf-8-sig',newline='') as stream:manifest=list(csv.DictReader(stream))
    # Recheck the frozen annotations without decoding all images a second time.
    for row in manifest:
        if scope.sha(scope.DATASET/row['label'])!=row['label_sha256']:raise RuntimeError('Frozen annotation changed')
    state('preflight_passed',data_yaml=str(scope.DATASET/'data.yaml'),counts=audit['split_counts'])
    import torch
    import ultralytics
    from ultralytics import YOLO
    if ultralytics.__version__!='8.2.103':raise RuntimeError('Unexpected Ultralytics version')
    torch.set_num_threads(4)
    torch.backends.cudnn.benchmark=False
    initialization=ROOT/'yolov8n.pt'
    if scope.sha(initialization)!=preflight['initialization_sha256']:raise RuntimeError('Initialization digest changed')
    smoke_data=make_smoke_dataset(manifest,5)
    common={'imgsz':640,'device':'0','workers':0,'seed':42,'deterministic':True,
            'optimizer':'SGD','lr0':.01,'lrf':.01,'momentum':.937,'weight_decay':.0005,
            'warmup_epochs':3.,'warmup_momentum':.8,'warmup_bias_lr':.1,'nbs':64,
            'box':7.5,'cls':.5,'dfl':1.5,'amp':True,'patience':0,'mosaic':1.,'mixup':0.,'copy_paste':0.,
            'hsv_h':.015,'hsv_s':.7,'hsv_v':.4,'degrees':0.,'translate':.1,'scale':.5,
            'shear':0.,'perspective':0.,'flipud':0.,'fliplr':.5,'save':True,'plots':True,
            'val':True,'verbose':False}
    state('smoke_training',epochs=2,train_images=20,val_images=10)
    smoke=YOLO(str(initialization))
    smoke.train(data=str(smoke_data),epochs=2,batch=4,cache=False,close_mosaic=0,
                project=str(ROOT/'runs'),name='new_json_smoke',exist_ok=False,**common)
    smoke_dir=Path(smoke.trainer.save_dir)
    best=smoke_dir/'weights/best.pt';last=smoke_dir/'weights/last.pt'
    if not best.is_file() or not last.is_file():raise RuntimeError('Smoke training did not save both checkpoints')
    with (smoke_dir/'results.csv').open(newline='') as stream:smoke_rows=list(csv.DictReader(stream))
    if len(smoke_rows)!=2:raise RuntimeError('Smoke training did not finish two epochs')
    for row in smoke_rows:
        for key,value in row.items():
            if value.strip() and not math.isfinite(float(value)):raise RuntimeError(f'Nonfinite smoke result: {key}')
    reloaded=YOLO(str(best))
    validation=reloaded.val(data=str(smoke_data),split='val',imgsz=640,batch=4,device='0',workers=0,
                            project=str(ROOT/'runs'),name='smoke_reload_validation',plots=True,verbose=False)
    image=next((ROOT/'smoke_dataset/images/val').glob('*.jpg'))
    predictions=reloaded.predict(source=str(image),imgsz=640,device='0',conf=.25,save=True,
                                  project=str(ROOT/'runs'),name='smoke_reload_prediction',verbose=False)
    scope.save(ROOT/'SMOKE_RESULT.json',{'status':'completed','epochs':2,'train':20,'val':10,
               'best':str(best),'last':str(last),'best_sha256':scope.sha(best),
               'validation_metrics':{k:float(v) for k,v in validation.results_dict.items()},
               'prediction_count':len(predictions[0].boxes),'test_used':False,'is_formal_result':False})
    del smoke,reloaded,validation,predictions;gc.collect();torch.cuda.empty_cache()
    batch=16 if preflight['vram_GB']>=10 else 8
    cache='ram' if preflight.get('available_RAM_GB',0)>=8 else False
    settings={**common,'epochs':100,'batch':batch,'cache':cache,'close_mosaic':10}
    protocol={'status':'user_authorized_baseline_configuration_not_team_agreement',
              'dataset_manifest_sha256':audit['manifest_sha256'],'data_yaml':str(scope.DATASET/'data.yaml'),
              'initialization':'official YOLOv8n COCO','initialization_sha256':preflight['initialization_sha256'],
              'group_status':audit['group_status'],'test_withheld':True,'settings':settings}
    scope.save(ROOT/'BASELINE_RUN_CONFIGURATION.json',protocol)
    formal=YOLO(str(initialization))
    def epoch_done(trainer):
        state('formal_training',completed_epochs=int(trainer.epoch)+1,total_epochs=int(trainer.epochs),
              best_fitness=float(trainer.best_fitness),metrics={k:float(v) for k,v in trainer.metrics.items()},
              run_directory=str(trainer.save_dir),data_yaml=str(scope.DATASET/'data.yaml'))
    formal.add_callback('on_fit_epoch_end',epoch_done)
    state('formal_training_starting',total_epochs=100,batch=batch,cache=cache,data_yaml=str(scope.DATASET/'data.yaml'))
    formal.train(data=str(scope.DATASET/'data.yaml'),project=str(ROOT/'runs'),name='yolov8n_new_json_baseline',
                 exist_ok=False,**settings)
    result_dir=Path(formal.trainer.save_dir);best=result_dir/'weights/best.pt';last=result_dir/'weights/last.pt'
    if not best.is_file() or not last.is_file():raise RuntimeError('Full baseline is missing checkpoints')
    loaded=YOLO(str(best))
    metrics=loaded.val(data=str(scope.DATASET/'data.yaml'),split='val',imgsz=640,batch=batch,device='0',workers=0,
                       project=str(ROOT/'runs'),name='baseline_reload_validation',plots=True,verbose=False)
    handoff={'status':'completed','best':str(best),'last':str(last),'best_sha256':scope.sha(best),'last_sha256':scope.sha(last),
             'validation_metrics':{k:float(v) for k,v in metrics.results_dict.items()},'configuration':'BASELINE_RUN_CONFIGURATION.json',
             'manifest_sha256':audit['manifest_sha256'],'test_used':False,'classes':scope.NAMES,
             'limitations':audit['limitations']}
    scope.save(ROOT/'BASELINE_MODEL_HANDOFF.json',handoff)
    state('completed',completed_epochs=100,total_epochs=100,best=str(best),last=str(last),validation_metrics=handoff['validation_metrics'])
    lock.unlink(missing_ok=True)


if __name__=='__main__':
    try:run()
    except Exception as exc:
        state('failed',error=str(exc));traceback.print_exc();raise

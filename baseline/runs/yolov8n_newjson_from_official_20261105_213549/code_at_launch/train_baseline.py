"""Train a unique original YOLOv8n run for exactly 100 epochs from official COCO weights."""
import new_json_common as c
import argparse,csv,json,math,os,sys,time,traceback,threading
from pathlib import Path
class Tee:
    def __init__(self,console,log,lock):self.console,self.log,self.lock=console,log,lock
    def write(self,s):
        with self.lock:self.console.write(s);self.console.flush();self.log.write(s);self.log.flush()
        return len(s)
    def flush(self):
        with self.lock:self.console.flush();self.log.flush()
    def isatty(self):return self.console.isatty()
    @property
    def encoding(self):return 'utf-8'
    def fileno(self):return self.console.fileno()
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--run-id',required=True);a=ap.parse_args()
    if Path(a.run_id).name!=a.run_id:raise ValueError('run-id must be a single directory name')
    run=c.BASE/'runs'/a.run_id;run.mkdir(parents=True,exist_ok=False)
    log=(run/'training.log').open('a',encoding='utf-8',buffering=1);lock=threading.RLock();sys.stdout=Tee(sys.stdout,log,lock);sys.stderr=Tee(sys.stderr,log,lock)
    start=time.time();completed=0;started=c.now();epochs=[]
    def state(status,**kw):
        value={'status':status,'pid':os.getpid(),'run_id':a.run_id,'run_directory':str(run),'started_China':started,'updated_China':c.now(),'elapsed_seconds':round(time.time()-start,2),'completed_epochs':completed,'total_epochs':100,'log':str(run/'training.log'),**kw}
        c.save(run/'status.json',value);c.save(c.BASE/'current_training_status.json',value)
        print('JOB_STATUS '+json.dumps(value,ensure_ascii=False),flush=True)
    try:
        import psutil
        c.save(run/'process.json',{'pid':os.getpid(),'create_time':psutil.Process().create_time(),'script':str(Path(__file__).resolve()),'command':sys.argv})
        state('preflight')
        rows=c.assert_dataset()
        config=c.load(c.BASE/'configs/new_json_100epochs.json')
        settings=config['settings'];assert settings['epochs']==100 and settings['resume'] is False and settings['patience']==0
        import torch,ultralytics
        from ultralytics import YOLO
        assert ultralytics.__version__=='8.2.103' and torch.cuda.is_available()
        torch.set_num_threads(4);torch.backends.cudnn.benchmark=False
        c.quiet_integrations();os.chdir(c.INITIAL.parent)
        c.save(run/'environment.json',c.environment());c.save(run/'protocol.json',config)
        model=YOLO(str(c.INITIAL));gpu_memory=[]
        def epoch_done(trainer):
            nonlocal completed
            n=int(trainer.epoch)+1
            if n<=completed:return
            completed=n;metrics={k:float(v) for k,v in trainer.metrics.items()}
            if any(not math.isfinite(v) for v in metrics.values()):raise RuntimeError('Nonfinite validation metrics')
            record={'epoch':n,'epoch_seconds':float(trainer.epoch_time),'elapsed_seconds':round(time.time()-start,2),'cuda_allocated_bytes':torch.cuda.memory_allocated(),'cuda_reserved_bytes':torch.cuda.memory_reserved(),'cuda_peak_allocated_bytes':torch.cuda.max_memory_allocated(),'metrics':metrics}
            epochs.append(record);c.save(run/'epoch_observations.json',epochs)
            with (run/'epoch_events.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
            mean=sum(r['epoch_seconds'] for r in epochs[-5:])/min(5,len(epochs));eta=(100-n)*mean
            state('training',last_epoch_seconds=record['epoch_seconds'],estimated_remaining_training_seconds=round(eta,1),metrics=metrics,cuda_peak_allocated_bytes=record['cuda_peak_allocated_bytes'])
        model.add_callback('on_fit_epoch_end',epoch_done)
        state('training_starting',initialization=str(c.INITIAL),initialization_sha256=c.INITIAL_SHA,data=str(c.DATA),batch=settings['batch'],workers=settings['workers'])
        training_start=time.time()
        model.train(data=str(c.DATA),project=str(run.parent),name=run.name,exist_ok=True,**settings)
        train_seconds=time.time()-training_start
        with (run/'results.csv').open(newline='') as f:results=[{k.strip():v.strip() for k,v in r.items()} for r in csv.DictReader(f)]
        assert len(results)==100 and [int(float(r['epoch'])) for r in results]==list(range(1,101))
        for row in results:
            for k,v in row.items():
                if v and not math.isfinite(float(v)):raise RuntimeError(f'Nonfinite CSV value: {k}')
        for name in ['best.pt','last.pt']:assert (run/'weights'/name).is_file()
        c.save(run/'training_verified.json',{'status':'100_epochs_verified','csv_rows':len(results),'first_epoch':1,'last_epoch':100,'training_seconds':train_seconds,'elapsed_seconds':time.time()-start,'initialization_sha256':c.INITIAL_SHA,'resume':False,'best_sha256':c.sha(run/'weights/best.pt'),'last_sha256':c.sha(run/'weights/last.pt'),'test_used':False})
        c.save(c.BASE/'current_model.json',{'run_id':a.run_id,'run_directory':str(run),'best':str(run/'weights/best.pt'),'last':str(run/'weights/last.pt')})
        state('training_complete_pending_independent_validation',training_seconds=train_seconds)
    except BaseException as e:
        state('failed',error=repr(e));traceback.print_exc();raise
    finally:sys.stdout.flush();sys.stderr.flush()
if __name__=='__main__':main()

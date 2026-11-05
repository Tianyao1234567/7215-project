"""Member 4: reproducible original YOLOv8n training; smoke and formal kept distinct."""
import runtime_setup
import argparse
import contextlib
import datetime
import importlib.metadata
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import traceback
import yaml
from data_tools.dataset_audit import audit_yaml, load_data_yaml, sha256, write_json

class Tee:
    def __init__(self,*streams): self.streams=streams
    def write(self,s):
        for stream in self.streams: stream.write(s); stream.flush()
        return len(s)
    def flush(self):
        for stream in self.streams: stream.flush()
    def isatty(self): return False
    @property
    def encoding(self): return "utf-8"

def environment():
    info={"python":sys.version,"executable":sys.executable,"platform":sys.platform}
    info["versions"]={}
    for pkg in ("torch","torchvision","ultralytics","numpy","Pillow","PyYAML"):
        try: info["versions"][pkg]=importlib.metadata.version(pkg)
        except importlib.metadata.PackageNotFoundError: info["versions"][pkg]=None
    import torch
    info.update(cuda_available=torch.cuda.is_available(),torch_cuda=torch.version.cuda,
                gpu=torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
                torch_threads=torch.get_num_threads())
    return info

def resolve_from(base,value):
    p=Path(value)
    return p.resolve() if p.is_absolute() else (base/p).resolve()

def run(config_path,data_path,mode="smoke",groups=None,device=None):
    config_path=Path(config_path).resolve()
    config=yaml.safe_load(config_path.read_text(encoding="utf-8-sig"))
    if not isinstance(config,dict) or not isinstance(config.get("train"),dict):
        raise ValueError("Config requires a train mapping")
    protocol=config.get("protocol",{})
    if mode=="formal" and (protocol.get("status")!="agreed" or
            not protocol.get("agreement_record") or not protocol.get("dataset_version")):
        raise ValueError("Formal protocol is provisional. Members 1/4/5 must record the agreed settings and dataset version.")
    out=resolve_from(config_path.parent,config.get("output","../runs"))
    run_id=mode+"_"+datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
    run_dir=out/run_id
    run_dir.mkdir(parents=True,exist_ok=False)
    state={"run_id":run_id,"mode":mode,"status":"preflight","config":str(config_path),
           "is_formal_result":mode=="formal"}
    write_json(run_dir/"status.json",state)
    with (run_dir/"console.log").open("w",encoding="utf8") as log:
        with contextlib.redirect_stdout(Tee(sys.stdout,log)),contextlib.redirect_stderr(Tee(sys.stderr,log)):
            try:
                import numpy as np
                import torch
                from ultralytics import YOLO
                seed=int(config["train"]["seed"])
                random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
                if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)
                os.environ["CUBLAS_WORKSPACE_CONFIG"]=":4096:8"
                torch.set_num_threads(int(config.get("cpu_threads",2)))
                info=environment()
                write_json(run_dir/"environment.json",info)
                freeze=subprocess.run([sys.executable,"-m","pip","freeze"],capture_output=True,text=True,check=True)
                (run_dir/"requirements-lock.txt").write_text(freeze.stdout,encoding="utf8")
                cfg_version=protocol.get("ultralytics")
                if cfg_version and info["versions"]["ultralytics"]!=cfg_version:
                    raise ValueError(f"Ultralytics version must match protocol: {cfg_version}")
                audit=audit_yaml(data_path,groups,require_test=mode=="formal")
                write_json(run_dir/"dataset_audit.json",audit)
                if not audit["passed"]:
                    raise ValueError(f"Dataset failed audit with {len(audit['errors'])} errors")
                if mode=="formal" and audit["group_status"]!="verified_for_supplied_group_ids":
                    raise ValueError("Formal training requires member 3's complete process/part group mapping")
                root,names,splits=load_data_yaml(data_path)
                if mode=="formal" and audit["dataset_sha256"]!=protocol.get("dataset_sha256"):
                    raise ValueError("Dataset digest differs from agreed protocol")
                # Absolute manifests avoid working-directory ambiguity. Test is withheld from training.
                snapshot={"path":str(root),"names":dict(enumerate(names))}
                for split in ("train","val"):
                    manifest=run_dir/(split+"_images.txt")
                    manifest.write_text("".join(p.as_posix()+"\n" for p in splits[split]),encoding="utf8")
                    snapshot[split]=manifest.as_posix()
                snapshot_path=run_dir/"data.resolved.yaml"
                snapshot_path.write_text(yaml.safe_dump(snapshot,sort_keys=False),encoding="utf8")
                original_data=Path(data_path).read_bytes()
                (run_dir/"data.input.yaml").write_bytes(original_data)
                write_json(run_dir/"requested_config.json",config)
                model=YOLO("yolov8n.yaml",task="detect")
                init=config.get("initialization",{})
                if init.get("kind")=="official_coco":
                    weight=resolve_from(config_path.parent,init["weights"])
                    if not weight.is_file(): raise FileNotFoundError(f"Official initialization weights missing: {weight}")
                    digest=sha256(weight)
                    if not init.get("sha256") or digest!=init["sha256"]:
                        raise ValueError("Initialization weights need the recorded matching SHA256")
                    if not init.get("source_url","").startswith("https://github.com/ultralytics/assets/releases/"):
                        raise ValueError("Record the official Ultralytics release source URL")
                    model.load(str(weight))
                    initialization={"kind":"official_coco","sha256":digest,"source_url":init["source_url"]}
                elif init.get("kind")=="random_architecture_only" and mode=="smoke":
                    initialization={"kind":"random_architecture_only","note":"Engineering smoke only; no transfer learning or defect performance claim."}
                else:
                    raise ValueError("Formal baseline requires official COCO initialization; reference best.pt is not allowed")
                write_json(run_dir/"initialization.json",initialization)
                args=dict(config["train"])
                for forbidden in ("data","model","resume","project","name","exist_ok","pretrained","split","fraction"):
                    if forbidden in args: raise ValueError(f"Config cannot override reserved setting: {forbidden}")
                if device is not None: args["device"]=device
                if mode=="formal" and device is not None and str(device)!=str(config["train"].get("device")):
                    raise ValueError("Record a device change in the agreed formal protocol first")
                args.update(data=str(snapshot_path),project=str(run_dir),name="fit",exist_ok=False,
                            pretrained=initialization["kind"]=="official_coco",resume=False,val=True,save=True,plots=True)
                state.update(status="training",dataset_sha256=audit["dataset_sha256"])
                write_json(run_dir/"status.json",state)
                model.train(**args)
                fit=Path(model.trainer.save_dir)
                best,last=fit/"weights/best.pt",fit/"weights/last.pt"
                if not best.is_file() or not last.is_file():
                    raise RuntimeError("Training returned without required weights")
                trained=YOLO(str(best))
                metrics=trained.val(data=str(snapshot_path),split="val",imgsz=args["imgsz"],
                                    batch=args["batch"],device=args.get("device","cpu"),workers=0,
                                    project=str(run_dir),name="validation",plots=True,verbose=False)
                write_json(run_dir/"validation_metrics.json",metrics.results_dict)
                sample=splits["val"][0]
                pred=trained.predict(source=str(sample),imgsz=args["imgsz"],device=args.get("device","cpu"),
                                     conf=0.25,save=True,save_txt=True,save_conf=True,
                                     project=str(run_dir),name="prediction",verbose=False)
                boxes=pred[0].boxes
                write_json(run_dir/"prediction.json",{"image":str(sample),"coordinate_format":"xyxy_pixels",
                    "detections":[{"box":b.xyxy[0].tolist(),"class_id":int(b.cls[0]),"confidence":float(b.conf[0])} for b in boxes]})
                write_json(run_dir/"handoff.json",{"run_id":run_id,"mode":mode,"best":str(best),"last":str(last),
                    "best_sha256":sha256(best),"last_sha256":sha256(last),"names":names,
                    "dataset_sha256":audit["dataset_sha256"],"test_used_for_training_or_selection":False,
                    "predict_sample":str(sample),"validation_metrics":"validation_metrics.json",
                    "upstream_data_yaml":str(Path(data_path).resolve())})
                state.update(status="completed",fit_directory=str(fit),prediction_count=len(boxes))
                write_json(run_dir/"status.json",state)
                print(f"Completed {mode}: {run_dir}")
                return run_dir
            except Exception as e:
                state.update(status="failed",error=str(e))
                write_json(run_dir/"status.json",state)
                traceback.print_exc()
                raise

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--config",default="configs/smoke.yaml")
    p.add_argument("--data",required=True)
    p.add_argument("--mode",choices=["smoke","formal"],default="smoke")
    p.add_argument("--groups")
    p.add_argument("--device")
    a=p.parse_args()
    run(a.config,a.data,a.mode,a.groups,a.device)

if __name__=="__main__":
    main()

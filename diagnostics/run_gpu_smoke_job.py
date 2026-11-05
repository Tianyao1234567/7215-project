"""Managed project GPU smoke job; no pipe-dependent progress or timeout guessing."""
import datetime,json,os,subprocess,sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
state_file=root/"diagnostics"/"gpu_smoke_job_status.json"
state={"status":"running","started":datetime.datetime.now(datetime.timezone.utc).isoformat(),"pid":os.getpid()}
state_file.write_text(json.dumps(state,indent=2),encoding="utf8")
gpu_python=root/"environment/.venv_gpu/Scripts/python.exe"
command=[sys.executable,"-B",str(root/"diagnostics/run_scoped.py"),str(gpu_python),"-B",
         str(root/"baseline/train_baseline.py"),"--config",str(root/"baseline/configs/smoke.gpu.yaml"),
         "--data",str(root/"baseline/tests/synthetic_fixture/data.yaml")]
try:
    with (root/"diagnostics"/"gpu_yolo_smoke_complete.log").open("w",encoding="utf8") as log:
        result=subprocess.run(command,cwd=root,stdout=log,stderr=subprocess.STDOUT)
    state.update(status="finished" if result.returncode==0 else "failed",exit_code=result.returncode,
                 ended=datetime.datetime.now(datetime.timezone.utc).isoformat())
except Exception as error:
    state.update(status="failed",error=str(error))
state_file.write_text(json.dumps(state,indent=2),encoding="utf8")

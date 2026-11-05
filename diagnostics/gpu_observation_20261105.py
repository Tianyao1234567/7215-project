import sys
from pathlib import Path
root=Path(r'D:\Desktop\7215\project');sys.path.insert(0,str(root/'baseline'))
import new_json_common as c
import shutil,subprocess
exe=shutil.which('nvidia-smi')
report={'observed_China':c.now(),'power_measured':False,'training_state':c.load(c.BASE/'current_training_status.json'),'nvidia_smi_executable':exe}
if exe:
    try:
        proc=subprocess.run([exe,'--query-gpu=name,utilization.gpu,memory.used,temperature.gpu','--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=12)
        report.update(nvidia_smi_exit=proc.returncode,nvidia_smi_stdout=proc.stdout,nvidia_smi_stderr=proc.stderr)
    except Exception as e:report['nvidia_smi_error']=repr(e)
c.save(c.REPORT/'gpu_observation.json',report)
print({k:v for k,v in report.items() if k!='training_state'})

"""Run a task with durable logs and an explicit exit status."""
import argparse,datetime,json,os,subprocess,sys,traceback
from pathlib import Path
from run_scoped import configured_environment,ROOT
p=argparse.ArgumentParser()
p.add_argument("--name",required=True);p.add_argument("--python",required=True);p.add_argument("--script",required=True)
p.add_argument("args",nargs=argparse.REMAINDER)
a=p.parse_args();a.args=a.args[1:] if a.args and a.args[0]=="--" else a.args;state_path=ROOT/"diagnostics"/(a.name+"_status.json")
log_path=ROOT/"diagnostics"/(a.name+".log")
state={"status":"running","pid":os.getpid(),"started":datetime.datetime.now(datetime.timezone.utc).isoformat(),
       "log":str(log_path),"command":[a.python,"-B",a.script,*a.args]}
state_path.write_text(json.dumps(state,indent=2),encoding="utf8")
try:
    with log_path.open("w",encoding="utf8") as log:
        result=subprocess.run([a.python,"-B",a.script,*a.args],cwd=ROOT,env=configured_environment(),stdout=log,stderr=subprocess.STDOUT)
    state.update(status="completed" if result.returncode==0 else "failed",exit_code=result.returncode)
except Exception as error:
    state.update(status="failed",error=str(error),traceback=traceback.format_exc())
state["ended"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
state_path.write_text(json.dumps(state,indent=2),encoding="utf8")

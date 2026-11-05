"""Provide scoped process settings without changing the system/Jupyter installation."""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def configured_environment():
    env=os.environ.copy()
    env.setdefault("USERPROFILE",r"C:\Users\Z1234")
    locations={"TEMP":"tmp","TMP":"tmp","PIP_CACHE_DIR":"pip","XDG_CACHE_HOME":"cache",
               "YOLO_CONFIG_DIR":"yolo","MPLCONFIGDIR":"matplotlib","TORCH_HOME":"torch",
               "JUPYTER_RUNTIME_DIR":"jupyter","IPYTHONDIR":"ipython","NUMBA_CACHE_DIR":"numba",
               "CUDA_CACHE_PATH":"cuda","APPDATA":"appdata"}
    for key,rel in locations.items():
        folder=ROOT/".runtime"/rel
        folder.mkdir(parents=True,exist_ok=True)
        env[key]=str(folder)
    env["PYTHONDONTWRITEBYTECODE"]="1"
    env["PYTHONIOENCODING"]="utf-8"
    return env

def main():
    if len(sys.argv)<2:
        raise SystemExit("Usage: python -B diagnostics/run_scoped.py EXECUTABLE [ARGS...]")
    result=subprocess.run(sys.argv[1:],cwd=ROOT,env=configured_environment())
    raise SystemExit(result.returncode)
if __name__=="__main__":
    main()

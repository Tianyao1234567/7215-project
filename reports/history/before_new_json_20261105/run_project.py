"""Project entry point: always use the verified GPU Python and project-local caches."""
import sys
sys.dont_write_bytecode=True
from pathlib import Path
import subprocess
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/"diagnostics"))
from run_scoped import configured_environment

def main():
    commands=("check","tests","smoke","train","validate","predict")
    if len(sys.argv)<2 or sys.argv[1] not in commands:
        print("Usage: python run_project.py {check|tests|smoke|train|validate|predict} [arguments]")
        print("check/tests/smoke need no additional arguments. Formal training still needs accepted FDM data.")
        return 0 if len(sys.argv)<2 else 2
    python=ROOT/"environment/.venv_gpu/Scripts/python.exe"
    if not python.is_file():
        raise FileNotFoundError("The project GPU environment is missing; see README.md")
    action=sys.argv[1]; extra=sys.argv[2:]
    if action=="check":
        args=[str(ROOT/"diagnostics/check_gpu_environment.py")]
    elif action=="tests":
        args=[str(ROOT/"diagnostics/run_tests.py")]
    elif action=="smoke":
        args=[str(ROOT/"baseline/train_baseline.py"),
              "--config",str(ROOT/"baseline/configs/smoke.gpu.yaml"),
              "--data",str(ROOT/"baseline/tests/synthetic_fixture/data.yaml")]
    elif action=="train":
        args=[str(ROOT/"baseline/train_baseline.py"),"--mode","formal"]
    elif action=="validate":
        args=[str(ROOT/"baseline/validate_baseline.py"),"--device","0"]
    else:
        args=[str(ROOT/"baseline/predict_baseline.py"),"--device","0"]
    result=subprocess.run([str(python),"-B",*args,*extra],cwd=ROOT,env=configured_environment())
    return result.returncode
if __name__=="__main__":
    raise SystemExit(main())

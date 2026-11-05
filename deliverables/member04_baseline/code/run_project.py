"""Unified entry for the current original YOLOv8n baseline and frozen JSON dataset."""
import sys
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path(__file__).resolve().parent/'baseline'))
import new_json_common as c
import json,subprocess
from datetime import datetime,timezone,timedelta
ROOT=c.ROOT

def main():
    commands=('status','check','tests','smoke','train','validate','predict','verify-labels')
    if len(sys.argv)<2 or sys.argv[1] not in commands:
        print('Usage: python run_project.py {'+'|'.join(commands)+'} [arguments]')
        return 0 if len(sys.argv)<2 else 2
    action=sys.argv[1];extra=sys.argv[2:];python=ROOT/'environment/.venv_gpu/Scripts/python.exe'
    if action=='status':print(json.dumps(c.load(c.BASE/'current_training_status.json'),ensure_ascii=False,indent=2));return 0
    if action=='check':
        c.assert_dataset();print(json.dumps({'dataset':'passed','environment':c.environment()},ensure_ascii=False,indent=2));return 0
    script={'tests':ROOT/'diagnostics/run_tests.py','smoke':c.BASE/'resource_preflight.py','train':c.BASE/'train_baseline.py','validate':c.BASE/'evaluate_baseline.py','predict':c.BASE/'predict_baseline.py','verify-labels':c.BASE/'convert_annotations.py'}[action]
    if action=='train' and '--run-id' not in extra and '--help' not in extra:extra=['--run-id','yolov8n_newjson_from_official_'+datetime.now(timezone(timedelta(hours=8))).strftime('%Y%m%d_%H%M%S'),*extra]
    if action in ('validate','predict') and '--weights' not in extra and '--help' not in extra:extra=['--weights',c.current_model()['best'],*extra]
    if action=='verify-labels' and not extra:extra=['--verify']
    return subprocess.run([str(python),'-B','-u',str(script),*extra],cwd=ROOT,env=dict(c.os.environ)).returncode
if __name__=='__main__':raise SystemExit(main())

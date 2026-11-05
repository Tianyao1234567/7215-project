"""Record actual environment; does not install or upgrade any dependency."""
import json
from pathlib import Path
from train_baseline import environment
if __name__=="__main__":
    try:
        result=environment()
    except ImportError as e:
        result={"ready":False,"error":str(e)}
    Path("environment.json").write_text(json.dumps(result,indent=2),encoding="utf8")
    print(json.dumps(result,indent=2))

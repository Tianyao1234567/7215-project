"""Keep framework configuration and plotting caches inside this project."""
import os
from pathlib import Path
def configure():
    root=Path(__file__).resolve().parent
    for var,folder in (("YOLO_CONFIG_DIR",root/".runtime"/"yolo"),("MPLCONFIGDIR",root/".runtime"/"matplotlib")):
        target=Path(os.environ.get(var,str(folder)))
        target.mkdir(parents=True,exist_ok=True)
        os.environ.setdefault(var,str(target))
configure()

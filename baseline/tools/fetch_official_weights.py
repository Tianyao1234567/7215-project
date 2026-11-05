"""Download the official COCO YOLOv8n initialization and record its exact bytes."""
import argparse, hashlib, json, urllib.request
from pathlib import Path
URL="https://github.com/ultralytics/assets/releases/download/v8.2.0/yolov8n.pt"
def fetch(dest):
    p=Path(dest)
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists(): raise FileExistsError(p)
    tmp=p.with_suffix(".download")
    try:
        with urllib.request.urlopen(URL,timeout=30) as response, tmp.open("xb") as f:
            while True:
                block=response.read(1024*1024)
                if not block: break
                f.write(block)
        digest=hashlib.sha256(tmp.read_bytes()).hexdigest()
        tmp.rename(p)
        result={"source_url":URL,"sha256":digest,"path":str(p.resolve()),"bytes":p.stat().st_size,
                "purpose":"Official COCO initialization; not a trained FDM baseline."}
        p.with_suffix(".source.json").write_text(json.dumps(result,indent=2),encoding="utf8")
        return result
    except Exception:
        if tmp.exists(): tmp.unlink()
        raise
if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",default="weights/yolov8n.pt")
    print(json.dumps(fetch(parser.parse_args().output),indent=2))

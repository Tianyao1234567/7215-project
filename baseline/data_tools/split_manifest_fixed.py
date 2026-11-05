"""Repair of split_manifest.py. Records existing splits; does NOT split data."""
import argparse
import hashlib
from pathlib import Path
try:
    from .dataset_audit import images_in, write_json
except ImportError:
    from dataset_audit import images_in, write_json

def create_manifest(img_folder, output_filename):
    images = images_in(img_folder)
    p=Path(output_filename)
    p.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive create prevents accidental replacement of an accepted split.
    with p.open("x",encoding="utf8",newline="\n") as f:
        f.writelines(im.as_posix()+"\n" for im in images)
    return {"images":len(images),"manifest_sha256":hashlib.sha256(p.read_bytes()).hexdigest()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",default="dataset")
    p.add_argument("--output",default="manifests")
    a=p.parse_args()
    result={"purpose":"inventory_only_not_data_splitting","splits":{}}
    for s in ("train","val","test"):
        folder=Path(a.root)/"images"/s
        result["splits"][s]=create_manifest(folder,Path(a.output)/(s+"_manifest.txt")) if folder.is_dir() else {"status":"missing"}
    write_json(Path(a.output)/"manifest_metadata.json",result)
    print(result)
if __name__ == "__main__":
    main()

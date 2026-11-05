"""Repair of prepare_data.py: report questionable pairs; preserve all originals."""
import argparse
from pathlib import Path
try:
    from .dataset_audit import images_in, check_label_file, write_json
except ImportError:
    from dataset_audit import images_in, check_label_file, write_json

def prepare_data(img_folder, label_folder, nc=5):
    image_root, label_root = Path(img_folder).resolve(), Path(label_folder).resolve()
    rows = []
    for image in images_in(image_root):
        label = label_root/image.relative_to(image_root).with_suffix(".txt")
        boxes, errors = check_label_file(label,nc)
        rows.append({"image":str(image),"label":str(label),"errors":errors,
                     "status":"needs_review" if errors else ("valid_negative" if not boxes else "valid_annotation")})
    return {"mode":"read_only","deleted":0,"modified":0,"items":rows}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",default="dataset")
    p.add_argument("--nc",type=int,default=5)
    p.add_argument("--report",default="preparation_review.json")
    a=p.parse_args()
    reports={}
    for s in ("train","val","test"):
        image_dir=Path(a.root)/"images"/s
        reports[s]=prepare_data(image_dir,Path(a.root)/"labels"/s,a.nc) if image_dir.is_dir() else {"status":"missing"}
    write_json(a.report,reports)
    print(f"Read-only review written to {a.report}; no files removed.")
if __name__ == "__main__":
    main()

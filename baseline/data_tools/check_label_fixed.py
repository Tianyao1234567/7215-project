"""Repair of check_label.py. Never modifies source images or annotations."""
import argparse
from pathlib import Path
try:
    from .dataset_audit import audit_yaml, audit_splits, images_in, write_json
except ImportError:
    from dataset_audit import audit_yaml, audit_splits, images_in, write_json

def check_dataset(img_folder, label_folder, nc=5):
    images = images_in(img_folder)
    image_root = Path(img_folder).resolve()
    label_root = Path(label_folder).resolve()
    return audit_splits(image_root,[str(i) for i in range(nc)],{"train":images},
                        label_resolver=lambda im:label_root/im.relative_to(image_root).with_suffix(".txt"), required_splits=("train",))

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--data",required=True)
    p.add_argument("--groups")
    p.add_argument("--require-test",action="store_true")
    p.add_argument("--report",default="audit.json")
    a = p.parse_args()
    result = audit_yaml(a.data,a.groups,a.require_test)
    write_json(a.report,result)
    print(f"passed={result['passed']} errors={len(result['errors'])} report={a.report}")
    return 0 if result["passed"] else 2

if __name__ == "__main__":
    raise SystemExit(main())

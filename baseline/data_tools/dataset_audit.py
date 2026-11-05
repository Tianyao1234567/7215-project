"""Read-only YOLO detection dataset audit, shared by the repaired scripts."""
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path
import yaml
from PIL import Image

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff", ".webp"}

def sha256(p):
    h = hashlib.sha256()
    with Path(p).open("rb") as f:
        for block in iter(lambda:f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def images_in(folder):
    folder = Path(folder)
    if not folder.is_dir():
        raise FileNotFoundError(f"Image directory missing: {folder}")
    return sorted((p.resolve() for p in folder.rglob("*") if p.suffix.lower() in IMAGE_EXTS),
                  key=lambda p:p.as_posix().casefold())

def label_for(image):
    parts = list(Path(image).parts)
    indices = [i for i,part in enumerate(parts) if part == "images"]
    if not indices:
        raise ValueError(f"Expected an images/ directory in {image}")
    parts[indices[-1]] = "labels"
    return Path(*parts).with_suffix(".txt")

def load_data_yaml(p):
    p = Path(p).resolve()
    data = yaml.safe_load(p.read_text(encoding="utf-8-sig"))
    if not isinstance(data, dict):
        raise ValueError("data.yaml must contain a mapping")
    raw_names = data.get("names")
    if isinstance(raw_names, dict):
        by_id = {int(k):v for k,v in raw_names.items()}
        if set(by_id) != set(range(len(by_id))):
            raise ValueError("Class IDs must be contiguous starting at 0")
        names = [by_id[i] for i in range(len(by_id))]
    elif isinstance(raw_names, list):
        names = raw_names
    else:
        raise ValueError("names must be a list or an ID-to-name mapping")
    if not names or any(not isinstance(x,str) or not x.strip() for x in names) or len(set(names)) != len(names):
        raise ValueError("Invalid or duplicate class names")
    if "nc" in data and data["nc"] != len(names):
        raise ValueError("nc disagrees with names")
    root = Path(data.get("path") or ".")
    root = (p.parent / root).resolve() if not root.is_absolute() else root.resolve()
    splits = {}
    for split in ("train", "val", "test"):
        value = data.get(split)
        if not value:
            splits[split] = []
            continue
        entries = value if isinstance(value,list) else [value]
        found = []
        for entry in entries:
            q = Path(entry)
            q = (root / q).resolve() if not q.is_absolute() else q.resolve()
            if q.is_dir():
                found.extend(images_in(q))
            elif q.is_file() and q.suffix.lower() == ".txt":
                for line in q.read_text(encoding="utf-8-sig").splitlines():
                    if line.strip():
                        im = Path(line.strip())
                        found.append((q.parent / im).resolve() if not im.is_absolute() else im.resolve())
            else:
                raise FileNotFoundError(f"{split} source missing: {q}")
        splits[split] = sorted(found, key=lambda x:x.as_posix().casefold())
    return root, names, splits

def check_label_file(p, nc):
    p = Path(p)
    if not p.is_file():
        return [], ["missing_label"]
    try:
        lines = p.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, UnicodeError) as e:
        return [], [f"unreadable_label:{type(e).__name__}"]
    boxes, errors = [], []
    for num, line in enumerate(lines,1):
        if not line.strip():
            continue
        parts = line.split()
        try:
            if len(parts) != 5:
                raise ValueError("expected_5_fields")
            if not parts[0].isdigit():
                raise ValueError("class_not_nonnegative_integer")
            cls = int(parts[0])
            if not 0 <= cls < nc:
                raise ValueError("class_out_of_range")
            x,y,w,h = map(float,parts[1:])
            if not all(math.isfinite(v) for v in (x,y,w,h)):
                raise ValueError("nonfinite_coordinate")
            if not (0 <= x <= 1 and 0 <= y <= 1 and 0 < w <= 1 and 0 < h <= 1):
                raise ValueError("coordinate_out_of_range")
            if min(x-w/2,y-h/2) < -1e-6 or max(x+w/2,y+h/2) > 1+1e-6:
                raise ValueError("bbox_outside_image")
            box = (cls,x,y,w,h)
            if box in boxes:
                raise ValueError("duplicate_bbox")
            boxes.append(box)
        except (ValueError,OverflowError) as e:
            errors.append(f"line_{num}:{e}")
    return boxes, errors

def audit_splits(root, names, splits, groups_csv=None, require_test=False, label_resolver=label_for, required_splits=("train","val")):
    root = Path(root).resolve()
    rows, errors, warnings = [], [], []
    for s in tuple(required_splits) + (("test",) if require_test else ()):
        if not splits.get(s):
            errors.append({"split":s,"error":"missing_or_empty_split"})
    label_keys, file_hashes, pixel_hashes = defaultdict(list), defaultdict(list), defaultdict(list)
    counts = {}
    for split, images in splits.items():
        box_counts, image_counts = Counter(), Counter()
        empty = 0
        for im in images:
            im = Path(im).resolve()
            try:
                rel = im.relative_to(root).as_posix()
            except ValueError:
                errors.append({"image":str(im),"error":"image_outside_dataset_root"})
                continue
            label = label_resolver(im)
            row = {"split":split,"image":rel,"label":str(label),"errors":[]}
            try:
                with Image.open(im) as pic:
                    pic.verify()
                with Image.open(im) as pic:
                    pic.load()
                    rgb = pic.convert("RGB")
                    row["size"] = list(rgb.size)
                    row["pixel_sha256"] = hashlib.sha256(str(rgb.size).encode()+rgb.tobytes()).hexdigest()
                row["image_sha256"] = sha256(im)
                pixel_hashes[row["pixel_sha256"]].append((split,rel))
                file_hashes[row["image_sha256"]].append((split,rel))
            except (OSError,ValueError,Image.DecompressionBombError) as e:
                row["errors"].append(f"bad_image:{type(e).__name__}")
            boxes, problems = check_label_file(label,len(names))
            row["errors"].extend(problems)
            row["boxes"] = len(boxes)
            row["label_sha256"] = sha256(label) if label.is_file() else None
            if not boxes and not problems:
                empty += 1
            box_counts.update(b[0] for b in boxes)
            image_counts.update(set(b[0] for b in boxes))
            label_keys[str(label.resolve()).casefold()].append((split,rel))
            errors.extend({"split":split,"image":rel,"error":e} for e in row["errors"])
            rows.append(row)
        counts[split] = {"images":len(images),"negative_images":empty,
                         "boxes_per_class":{n:box_counts[i] for i,n in enumerate(names)},
                         "images_per_class":{n:image_counts[i] for i,n in enumerate(names)}}
        if images and not sum(box_counts.values()):
            errors.append({"split":split,"error":"no_valid_bounding_boxes"})
        if images and any(not image_counts[i] for i in range(len(names))):
            warnings.append({"split":split,"warning":"one_or_more_classes_absent"})
    duplicates = []
    for kind, mapping in (("file",file_hashes),("decoded_pixels",pixel_hashes),("label_collision",label_keys)):
        for digest, items in mapping.items():
            if len(items) > 1:
                cross = len({s for s,_ in items}) > 1
                duplicates.append({"kind":kind,"items":items,"cross_split":cross})
                if cross or kind == "label_collision":
                    errors.append({"error":f"{kind}_duplicate_or_collision","items":items})
                else:
                    warnings.append({"warning":f"{kind}_duplicate_within_split","items":items})
    orphan_labels = []
    paired = {str(label_resolver((root / r["image"]).resolve()).resolve()).casefold() for r in rows}
    if (root/"labels").is_dir():
        orphan_labels = sorted(str(p.relative_to(root)) for p in (root/"labels").rglob("*.txt")
                               if str(p.resolve()).casefold() not in paired)
        if orphan_labels:
            warnings.append({"warning":"orphan_labels","count":len(orphan_labels)})
    group_status = "not_verified"
    if groups_csv:
        group_status = "verified_for_supplied_group_ids"
        groups = {}
        with Path(groups_csv).open(encoding="utf-8-sig",newline="") as f:
            for r in csv.DictReader(f):
                key = r["image"].replace("\\","/")
                if key in groups or not r.get("group_id","").strip():
                    errors.append({"error":"duplicate_or_empty_group_mapping","image":key})
                groups[key] = r.get("group_id","").strip()
        membership = defaultdict(set)
        for row in rows:
            group = groups.get(row["image"])
            if not group:
                errors.append({"error":"missing_group_id","image":row["image"]})
                group_status = "incomplete"
            else:
                membership[group].add(row["split"])
        for group, ss in membership.items():
            if len(ss)>1:
                errors.append({"error":"related_group_crosses_splits","group_id":group,"splits":sorted(ss)})
                group_status = "leakage_found"
    else:
        warnings.append({"warning":"group_ids_missing_near_duplicates_and_related_frames_NOT_verified"})
    signature = hashlib.sha256(json.dumps(
        [{"split":r["split"],"image":r["image"],"image_sha256":r.get("image_sha256"),
          "label_sha256":r.get("label_sha256")} for r in rows],sort_keys=True).encode()).hexdigest()
    return {"schema":1,"root":str(root),"names":names,"counts":counts,"errors":errors,"warnings":warnings,
            "duplicates":duplicates,"orphan_labels":orphan_labels,"group_status":group_status,
            "dataset_sha256":signature,"records":rows,"passed":not errors,
            "limitations":"Exact file/pixel duplicates only. Group correctness needs member 3 provenance and human review."}

def audit_yaml(data, groups_csv=None, require_test=False):
    root,names,splits = load_data_yaml(data)
    return audit_splits(root,names,splits,groups_csv,require_test)

def write_json(p, data):
    p = Path(p)
    p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf8")

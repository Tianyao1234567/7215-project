"""Prepare a lossless repartition index; do not choose labels or alter received files."""
import csv,json,re
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
report=json.loads((ROOT/"diagnostics/received_dataset_audit.json").read_text(encoding="utf8"))
out=ROOT/"datasets/repartition_draft_20261102"
out.mkdir(parents=True,exist_ok=True)
groups=defaultdict(list)
for row in report["records"]:
    groups[row["image_sha256"]].append(row)
def canonical(text):
    boxes=[tuple(map(float,line.split())) for line in text.splitlines() if line.strip()]
    return tuple(sorted(boxes))
rows=[];conflicts=[]
for image_hash,items in sorted(groups.items()):
    variants=[]
    for item in items:
        boxes=canonical(Path(item["label"]).read_text(encoding="utf-8-sig"))
        variants.append({"image":item["image"],"label":item["label"],"original_split":item["split"],
                         "boxes":boxes})
    unique_labels=set(v["boxes"] for v in variants)
    class_sets=set(tuple(sorted(set(b[0] for b in v["boxes"]))) for v in variants)
    box_counts=set(len(v["boxes"]) for v in variants)
    first=sorted(items,key=lambda r:r["image"])[0]
    stem=Path(first["image"]).stem
    match=re.match(r"^(.*?_Image_(\d{8})\d{9})",stem)
    row={"image_sha256":image_hash,"copies":len(items),
         "reference_image":first["image"],"reference_is_authoritative_label":False,
         "source_id_candidate":match.group(1) if match else stem,
         "capture_day_candidate":match.group(2) if match else "",
         "label_versions":len(unique_labels),"class_sets_differ":len(class_sets)>1,
         "box_counts_differ":len(box_counts)>1,"new_split":"UNASSIGNED"}
    rows.append(row)
    if len(unique_labels)>1:
        conflicts.append({**row,"variants":variants})
fields=list(rows[0])
with (out/"unique_image_index.csv").open("w",encoding="utf-8-sig",newline="") as f:
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
(out/"label_versions_to_confirm.json").write_text(json.dumps(conflicts,ensure_ascii=False,indent=2),encoding="utf8")
n=len(rows);train=round(n*.7);val=round(n*.15)
plan={"status":"DRAFT_NOT_FROZEN","received_images":len(report["records"]),"unique_images":n,
      "redundant_copies":len(report["records"])-n,
      "label_conflict_groups":len(conflicts),
      "groups_with_different_class_sets":sum(r["class_sets_differ"] for r in rows),
      "groups_with_different_box_counts":sum(r["box_counts_differ"] for r in rows),
      "proposed_ratio":[0.7,0.15,0.15],
      "illustrative_counts_only":{"train":train,"val":val,"test":n-train-val},
      "rules":["Retain received ZIP/images/labels unchanged",
               "Use all received images, not only original val",
               "Keep identical images, original/augmented variants, and known same-process frames in one split",
               "Stratify class coverage as far as actual groups permit; grouped counts may differ from target ratio",
               "Confirm authoritative label version; do not average boxes or silently prefer train",
               "Fix seed and freeze manifests before training; test is withheld from tuning"],
      "needed_facts":["Which annotation version is final?","Are print-process/part IDs available?"],
      "not_needed":"No reupload of existing photos; reconstructing why duplicates appeared is optional."}
(out/"repartition_plan.json").write_text(json.dumps(plan,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps(plan,ensure_ascii=False,indent=2))

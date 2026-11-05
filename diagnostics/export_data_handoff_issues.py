"""Export concrete upstream fixes without modifying or repartitioning the dataset."""
import csv,json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
inventory=json.loads((ROOT/"diagnostics/dataset_archive_inventory.json").read_text(encoding="utf8"))
overlap=json.loads((ROOT/"diagnostics/confirmed_exact_train_val_overlap.json").read_text(encoding="utf8"))
conflicts=json.loads((ROOT/"diagnostics/duplicate_annotation_conflicts.json").read_text(encoding="utf8"))
conflict_keys={(r["train"],r["val"]) for r in conflicts["allPairs"]}
with (ROOT/"diagnostics/duplicate_train_val_pairs.csv").open("w",encoding="utf-8-sig",newline="") as f:
    fields=["source_image_id","train_image","val_image","image_sha256","annotations_differ"]
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for r in overlap["allPairs"]:
        writer.writerow({"source_image_id":r["id"],"train_image":r["train"],"val_image":r["val"],
                         "image_sha256":r["sha256"],"annotations_differ":(r["train"],r["val"]) in conflict_keys})
with (ROOT/"diagnostics/candidate_source_image_groups.csv").open("w",encoding="utf-8-sig",newline="") as f:
    fields=["image","current_split","candidate_source_id","status"]
    writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
    for r in inventory["entries"]:
        if r["name"].endswith(".jpg"):
            image=r["name"].removeprefix("dataset/")
            stem=Path(image).stem
            match=re.match(r"^(.*?_Image_\d{17})",stem)
            writer.writerow({"image":image,"current_split":image.split("/")[1],
                             "candidate_source_id":match.group(1) if match else stem,
                             "status":"filename_source_identity_only_not_verified_print_process"})
print("Exported duplicate-pair and candidate-source-ID lists; no split or annotation changed.")

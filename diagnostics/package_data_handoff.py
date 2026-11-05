from pathlib import Path
import hashlib,json,zipfile
root=Path(__file__).resolve().parents[1]
files=["DATA_ACCEPTANCE_20261102.md","PROGRESS_CURRENT.md",
       "diagnostics/MESSAGE_TO_MEMBER3_20261102.md",
       "diagnostics/duplicate_train_val_pairs.csv","diagnostics/candidate_source_image_groups.csv",
       "diagnostics/duplicate_annotation_conflicts.json","diagnostics/final_dataset_acceptance_summary.json",
       "diagnostics/received_dataset_audit.json","diagnostics/source_image_group_leakage.json",
       "diagnostics/timestamp_group_screen.json","diagnostics/received_ground_truth_contact_sheet.jpg",
       "baseline/configs/data.received_20261102.yaml"]
out=root/"deliverables/Data_Handoff_Issues_20261102.zip"
with zipfile.ZipFile(out,"w",zipfile.ZIP_DEFLATED) as z:
    for rel in files:z.write(root/rel,rel)
with zipfile.ZipFile(out) as z:
    assert z.testzip() is None
summary={"path":str(out),"bytes":out.stat().st_size,"files":len(files),
         "sha256":hashlib.sha256(out.read_bytes()).hexdigest()}
(root/"diagnostics/data_handoff_package.json").write_text(json.dumps(summary,indent=2),encoding="utf8")
print(json.dumps(summary,indent=2))

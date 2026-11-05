"""Read-only full-data acceptance audit; no annotation or split is modified."""
import json,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"baseline"))
from data_tools.dataset_audit import audit_yaml,write_json
data=ROOT/"baseline/configs/data.received_20261102.yaml"
start=time.perf_counter()
print("Starting full read-only audit of 2380 images",flush=True)
report=audit_yaml(data,require_test=False)
report["elapsed_seconds"]=time.perf_counter()-start
report["source_delivery"]="four Google Drive ZIP parts received 2026-11-02 China time"
report["test_split_available"]=False
report["formal_acceptance_passed"]=False
report["formal_blockers"]=["No independent test split","Print-process/part grouping not supplied","Training protocol not yet shared with member 5"]
write_json(ROOT/"diagnostics/received_dataset_audit.json",report)
print(json.dumps({k:report[k] for k in ("passed","counts","errors","warnings","group_status","dataset_sha256","elapsed_seconds")},ensure_ascii=False,indent=2),flush=True)

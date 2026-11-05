"""Cryptographically compare the new yolo.zip with the previous delivered dataset."""
import hashlib,json,time,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
old_inventory=json.loads((ROOT/"diagnostics/dataset_archive_inventory.json").read_text(encoding="utf8"))
extracted=json.loads((ROOT/"diagnostics/dataset_extraction_manifest.json").read_text(encoding="utf8"))
expected={r["path"].split("/",1)[1]:r["sha256"] for r in extracted}
old_by_relative={r["name"].split("/",1)[1]:r for r in old_inventory["entries"]}
status_path=ROOT/"diagnostics/yolo_source_comparison_progress.json"
status={"status":"running","checked_files":0,"checked_bytes":0}
def save(): status_path.write_text(json.dumps(status,indent=2),encoding="utf8")
save()
for key,entry in old_by_relative.items():
    if key not in expected:
        with zipfile.ZipFile(ROOT/entry["archive"]) as old_zip:
            expected[key]=hashlib.sha256(old_zip.read(entry["name"])).hexdigest()
result={"new_archive":"yolo.zip","comparison":"old four ZIP parts after removing only top-level folder name",
        "total_old_files":len(expected),"same_files":0,"changed":[],"new_paths":[],"missing_paths":[],"example_labels":[]}
seen=set()
try:
    with zipfile.ZipFile(ROOT/"yolo.zip") as z:
        for info in z.infolist():
            if info.is_dir():continue
            key=info.filename.replace("\\","/").split("/",1)[1];seen.add(key)
            h=hashlib.sha256()
            with z.open(info) as src:
                for block in iter(lambda:src.read(1024*1024),b""):
                    h.update(block);status["checked_bytes"]+=len(block)
            digest=h.hexdigest()
            if key not in expected:result["new_paths"].append(key)
            elif digest==expected[key]:result["same_files"]+=1
            else:result["changed"].append({"path":key,"old_sha256":expected[key],"new_sha256":digest})
            status["checked_files"]+=1
            if status["checked_files"]%40==0:save()
        for split in ("train","val"):
            name=f"yolo/labels/{split}/Cracking_Image_20231130103801735_aug.txt"
            result["example_labels"].append({"file":name,"text":z.read(name).decode("utf-8-sig")})
    result["missing_paths"]=sorted(set(expected)-seen)
    result["all_files_identical"]=result["same_files"]==len(expected) and not any(result[k] for k in ("changed","new_paths","missing_paths"))
    (ROOT/"diagnostics/yolo_source_comparison.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf8")
    status.update(status="completed",all_files_identical=result["all_files_identical"],same_files=result["same_files"])
    save()
    print(json.dumps(result,ensure_ascii=False,indent=2))
except Exception as error:
    status.update(status="failed",error=str(error));save();raise

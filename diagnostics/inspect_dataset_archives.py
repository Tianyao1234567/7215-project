"""Inspect Google Drive ZIP parts without modifying archives."""
import collections,json,shutil,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
archives=sorted(ROOT.glob("dataset-*.zip"))
report={"archives":[],"disk_free_bytes":shutil.disk_usage(ROOT).free,"entries":[],"text_files":[]}
seen=collections.defaultdict(list)
for archive in archives:
    row={"file":archive.name,"bytes":archive.stat().st_size}
    with zipfile.ZipFile(archive) as z:
        entries=[i for i in z.infolist() if not i.is_dir()]
        row.update(files=len(entries),uncompressed_bytes=sum(i.file_size for i in entries),
                  extensions=dict(collections.Counter(Path(i.filename).suffix.lower() for i in entries)),
                  sample_paths=[i.filename for i in entries[:6]])
        for i in entries:
            name=i.filename.replace("\\","/")
            info={"archive":archive.name,"name":name,"bytes":i.file_size,"crc32":i.CRC}
            report["entries"].append(info);seen[name.casefold()].append(info)
            if Path(name).suffix.lower() in (".yaml",".yml",".json",".csv",".txt",".md") and i.file_size<100000:
                content=z.read(i).decode("utf-8-sig",errors="replace")
                report["text_files"].append({"archive":archive.name,"name":name,"text":content})
    report["archives"].append(row)
report["total_uncompressed_bytes"]=sum(x["uncompressed_bytes"] for x in report["archives"])
report["duplicate_paths"]=[items for items in seen.values() if len(items)>1]
out=ROOT/"diagnostics"/"dataset_archive_inventory.json"
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print(json.dumps({k:v for k,v in report.items() if k not in ("entries","text_files","duplicate_paths")},ensure_ascii=False,indent=2))
print(json.dumps({"duplicate_paths":len(report["duplicate_paths"]),"text_file_count":len(report["text_files"]),
                  "non_label_text":[t for t in report["text_files"] if Path(t["name"]).suffix.lower()!=".txt"][:20],
                  "label_samples":[t for t in report["text_files"] if Path(t["name"]).suffix.lower()==".txt"][:8]},
                 ensure_ascii=False,indent=2))

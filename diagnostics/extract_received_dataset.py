"""Extract received dataset parts safely; archives remain untouched."""
import datetime,hashlib,json,os,re,shutil,stat,traceback,zipfile
from pathlib import Path,PurePosixPath
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/"datasets"/"received_20261102"
STATUS=ROOT/"diagnostics"/"dataset_extraction_status.json"
state={"status":"running","pid":os.getpid(),"output":str(OUT),"extracted_files":0,"bytes_written":0,"skipped_caches":[]}
def write_state():
    STATUS.write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding="utf8")
try:
    OUT.mkdir(parents=True,exist_ok=True)
    record=[]
    for archive in sorted(ROOT.glob("dataset-*.zip")):
        state["current_archive"]=archive.name;write_state()
        with zipfile.ZipFile(archive) as z:
            for info in z.infolist():
                name=info.filename.replace("\\","/")
                p=PurePosixPath(name)
                if p.is_absolute() or ".." in p.parts or any(":" in part for part in p.parts):
                    raise ValueError("Unsafe archive path: "+name)
                if stat.S_ISLNK(info.external_attr>>16) or info.flag_bits&1:
                    raise ValueError("Unsupported link/encrypted member: "+name)
                if info.is_dir(): continue
                if p.suffix.lower()==".cache":
                    state["skipped_caches"].append(name);continue
                dest=OUT.joinpath(*p.parts)
                if not dest.resolve().is_relative_to(OUT.resolve()):
                    raise ValueError("Extraction would leave the received-data folder")
                dest.parent.mkdir(parents=True,exist_ok=True)
                if dest.exists():
                    raise FileExistsError("Refusing overwrite: "+str(dest))
                h=hashlib.sha256()
                with z.open(info) as src,dest.open("xb") as dst:
                    while True:
                        chunk=src.read(1024*1024)
                        if not chunk: break
                        dst.write(chunk);h.update(chunk)
                if dest.stat().st_size!=info.file_size: raise RuntimeError("Size mismatch: "+name)
                record.append({"archive":archive.name,"path":name,"bytes":info.file_size,"sha256":h.hexdigest()})
                state["extracted_files"]+=1;state["bytes_written"]+=info.file_size
                if state["extracted_files"]%50==0:write_state()
    (ROOT/"diagnostics"/"dataset_extraction_manifest.json").write_text(json.dumps(record,ensure_ascii=False,indent=2),encoding="utf8")
    state.update(status="completed",completed=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                 crc_verified=True,source_archives_preserved=True)
except Exception as error:
    state.update(status="failed",error=str(error),traceback=traceback.format_exc())
write_state()

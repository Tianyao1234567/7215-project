"""Safely merge the four downloaded archives without altering the input files."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r'D:\Desktop\7215\project\new')
TARGET = ROOT / 'received'
STATUS = ROOT / 'extraction_status.json'


def save(path, obj):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def main():
    started = time.time()
    ROOT.mkdir(parents=True, exist_ok=True)
    TARGET.mkdir(parents=True, exist_ok=True)
    archives = sorted(SOURCE.glob('dataset-20261105T105219Z-1-*.zip'))
    if len(archives) != 4:
        raise ValueError(f'Expected four independent ZIP archives, found {len(archives)}')
    inventory = {}
    for archive in archives:
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                name = item.filename.replace('\\', '/')
                rel = PurePosixPath(name)
                if rel.is_absolute() or '..' in rel.parts or ':' in name:
                    raise ValueError(f'Unsafe ZIP path: {name}')
                if (item.external_attr >> 16) & 0o170000 == 0o120000:
                    raise ValueError(f'ZIP symlink rejected: {name}')
                old = inventory.get(name)
                if old and (old['crc32'], old['size']) != (item.CRC, item.file_size):
                    raise ValueError(f'Conflicting archive members: {name}')
                inventory[name] = {'archive': archive.name, 'crc32': item.CRC,
                                   'size': item.file_size, 'directory': item.is_dir()}
    save(ROOT / 'archive_inventory.json', inventory)
    records = []
    count = 0
    byte_count = 0
    for archive in archives:
        with zipfile.ZipFile(archive) as z:
            for item in z.infolist():
                name = item.filename.replace('\\', '/')
                destination = (TARGET / Path(*PurePosixPath(name).parts)).resolve()
                destination.relative_to(TARGET.resolve())
                if item.is_dir():
                    destination.mkdir(parents=True, exist_ok=True)
                    continue
                destination.parent.mkdir(parents=True, exist_ok=True)
                h = hashlib.sha256()
                temporary = destination.with_name(destination.name + '.extracting')
                with z.open(item) as inp, temporary.open('wb') as output:
                    for block in iter(lambda: inp.read(1024*1024), b''):
                        output.write(block)
                        h.update(block)
                if temporary.stat().st_size != item.file_size:
                    raise ValueError(f'Wrong extracted length: {name}')
                os.replace(temporary, destination)
                records.append({'path': name, 'archive': archive.name,
                                'sha256': h.hexdigest(), 'bytes': item.file_size})
                count += 1
                byte_count += item.file_size
                if count % 500 == 0:
                    state = {'status': 'extracting', 'files': count, 'bytes': byte_count,
                             'elapsed_seconds': round(time.time()-started, 1)}
                    save(STATUS, state)
                    print(json.dumps(state), flush=True)
        print(f'Archive finished: {archive.name}', flush=True)
    if len(records) != sum(not v['directory'] for v in inventory.values()):
        raise ValueError('Unexpected archive overlap or extraction count')
    save(ROOT / 'extraction_manifest.json', records)
    state = {'status': 'completed', 'files': count, 'bytes': byte_count,
             'elapsed_seconds': round(time.time()-started, 1), 'target': str(TARGET)}
    save(STATUS, state)
    print(json.dumps(state), flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception as exc:
        ROOT.mkdir(parents=True, exist_ok=True)
        save(STATUS, {'status': 'failed', 'error': str(exc)})
        raise

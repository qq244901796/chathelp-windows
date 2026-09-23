"""Supplement PyPI source archives with exact native-library upstream sources."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tarfile
import zipfile
from collect_sources import ROOT, DEST, fetch

QT = "https://download.qt.io/archive/qt/6.11/6.11.2/submodules/"
SOURCES = [
    ("flatbuffers", "25.12.19", "https://github.com/google/flatbuffers/archive/refs/tags/v25.12.19.tar.gz", "flatbuffers-25.12.19.tar.gz"),
    ("onnxruntime", "1.30.0", "https://github.com/microsoft/onnxruntime/archive/refs/tags/v1.30.0.tar.gz", "onnxruntime-1.30.0.tar.gz"),
    ("pywin32", "312", "https://github.com/mhammond/pywin32/archive/refs/tags/b312.tar.gz", "pywin32-312.tar.gz"),
    ("rapidocr-onnxruntime", "1.4.4", "https://github.com/RapidAI/RapidOCR/archive/refs/tags/v1.4.4.tar.gz", "RapidOCR-1.4.4.tar.gz"),
    ("PySide6", "6.11.2", "https://download.qt.io/official_releases/QtForPython/pyside6/PySide6-6.11.2-src/pyside-setup-everywhere-src-6.11.2.tar.xz", "pyside-setup-everywhere-src-6.11.2.tar.xz"),
    ("GEOS", "3.13.1", "https://download.osgeo.org/geos/geos-3.13.1.tar.bz2", "geos-3.13.1.tar.bz2"),
    ("Python", "3.11.6", "https://www.python.org/ftp/python/3.11.6/Python-3.11.6.tar.xz", "Python-3.11.6.tar.xz"),
] + [(module, "6.11.2", QT + f"{module}-everywhere-src-6.11.2.tar.xz", f"{module}-everywhere-src-6.11.2.tar.xz")
     for module in ("qtbase", "qtsvg", "qtimageformats", "qttranslations")]


def notices(name, archive):
    """Read regular text notices only, with traversal and size limits; never extract code."""
    count = 0
    with tarfile.open(archive, "r:*") as source:
        for member in source:
            path = PurePosixPath(member.name)
            base = path.name.lower()
            if (not member.isfile() or member.size > 2000000 or path.is_absolute() or ".." in path.parts):
                continue
            if not (any(w in base for w in ("license", "licence", "copying", "copyright", "notice")) or "LICENSES" in path.parts):
                continue
            if path.suffix.lower() in (".py", ".cpp", ".h", ".png", ".jpg", ".cmake", ".sh"):
                continue
            data = source.extractfile(member).read()
            try:
                data.decode("utf-8")
            except UnicodeDecodeError:
                continue
            target = ROOT / "licenses" / "native" / name / Path(*path.parts[1:])
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
            count += 1
    return count


def run(item):
    name, version, url, filename = item
    record = dict(name=name, version=version, status="downloaded", **fetch(url, filename))
    record["notice_count"] = notices(name, DEST / filename)
    return record


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    manifest = ROOT / "source-manifest.json"
    records = {p["name"]: p for p in json.loads(manifest.read_text(encoding="utf-8"))}
    with ThreadPoolExecutor(max_workers=4) as pool:
        tasks = {pool.submit(run, item): item[0] for item in SOURCES}
        for future in as_completed(tasks):
            name = tasks[future]
            try:
                records[name] = future.result()
                print(name, "downloaded", records[name]["notice_count"], "notices", flush=True)
            except Exception as error:
                print(name, "FAILED", type(error).__name__, str(error)[:150], flush=True)
    if records["PySide6"]["status"] == "downloaded":
        for name in ("PySide6_Addons", "PySide6_Essentials", "shiboken6"):
            records[name] = dict(records["PySide6"], name=name)
    manifest.write_text(json.dumps(sorted(records.values(), key=lambda p: p["name"].lower()), ensure_ascii=False, indent=2), encoding="utf-8")
    target = ROOT / "licenses" / "python" / "LICENSE.txt"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(Path(sys.base_prefix) / "LICENSE.txt", target)
    missing = [p["name"] for p in records.values() if p["status"] != "downloaded"]
    print("Unresolved:", missing, flush=True)
    return bool(missing)


if __name__ == "__main__":
    sys.exit(main())

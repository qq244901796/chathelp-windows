"""Reproduce an audited ZIP from public source URLs and recorded ZIP metadata.

No downloaded source is executed. Every input and the final output are hashed.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", type=Path, default=ROOT / "outputs/sources")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/reproduced-sources.zip")
    args = parser.parse_args()
    specification = json.loads((ROOT / "release/source-archive.json").read_text(encoding="utf-8"))
    args.cache.mkdir(parents=True, exist_ok=True)
    def fetch(item):
        path = args.cache / item["file"]
        if not path.exists():
            request = urllib.request.Request(item["url"], headers={"User-Agent": "ChatHelp-source-archive"})
            with urllib.request.urlopen(request, timeout=180) as response, path.open("wb") as output:
                shutil.copyfileobj(response, output, length=1024 * 1024)
        if digest(path) != item["sha256"]:
            raise ValueError("Source hash mismatch: " + item["file"])
        print("Verified", item["file"], flush=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(fetch, specification["sources"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(args.output, "w", zipfile.ZIP_STORED) as output:
        output.comment = base64.b64decode(specification["comment"])
        for entry in specification["entries"]:
            info = zipfile.ZipInfo(entry["filename"], tuple(entry["date_time"]))
            for attribute in ("compress_type", "create_system", "create_version", "extract_version",
                              "flag_bits", "internal_attr", "external_attr", "volume", "file_size"):
                setattr(info, attribute, entry[attribute])
            info.extra = base64.b64decode(entry["extra"])
            info.comment = base64.b64decode(entry["comment"])
            with output.open(info, "w") as target:
                if "data" in entry:
                    target.write(base64.b64decode(entry["data"]))
                else:
                    with (args.cache / Path(entry["filename"]).name).open("rb") as source:
                        shutil.copyfileobj(source, target, length=1024 * 1024)
    actual = digest(args.output)
    if actual != specification["sha256"]:
        raise ValueError("Reproduced archive checksum mismatch")
    print("Exact archive SHA256:", actual, flush=True)


if __name__ == "__main__":
    main()

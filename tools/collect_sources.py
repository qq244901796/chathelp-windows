"""Fetch exact upstream source distributions for a reproducible public release.

Archives stay outside Git; source-manifest.json is public and contains hashes.
No execution of downloaded setup scripts and no extraction of untrusted paths.
"""
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "outputs" / "sources"


def fetch(url, filename):
    target = DEST / filename
    if not target.exists():
        req = urllib.request.Request(url, headers={"User-Agent": "ChatHelp-source-compliance/1.0"})
        partial = target.with_suffix(target.suffix + ".part")
        with urllib.request.urlopen(req, timeout=60) as source, partial.open("wb") as output:
            while chunk := source.read(1024 * 1024):
                output.write(chunk)
        partial.replace(target)
    return {"file": target.name, "url": url, "sha256": hashlib.file_digest(target.open("rb"), "sha256").hexdigest(),
            "bytes": target.stat().st_size}


def package_source(package):
    name, version = package["name"], package["version"]
    req = urllib.request.Request(f"https://pypi.org/pypi/{name}/{version}/json",
                                 headers={"User-Agent": "ChatHelp-source-compliance/1.0"})
    with urllib.request.urlopen(req, timeout=30) as response:
        release = json.load(response)
    sdists = [item for item in release["urls"] if item["packagetype"] == "sdist"]
    if not sdists:
        return {"name": name, "version": version, "status": "needs-source", "project_urls": package["project_urls"]}
    item = sdists[0]
    record = fetch(item["url"], item["filename"])
    if record["sha256"] != item["digests"]["sha256"]:
        raise ValueError(f"Source checksum mismatch: {name}")
    return {"name": name, "version": version, "status": "downloaded", **record}


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    packages = json.loads((ROOT / "dependencies.json").read_text(encoding="utf-8"))
    records = []
    with ThreadPoolExecutor(max_workers=4) as pool:
        jobs = {pool.submit(package_source, p): p["name"] for p in packages}
        for future in as_completed(jobs):
            name = jobs[future]
            try:
                record = future.result()
                print(name, record["status"], flush=True)
            except Exception as error:
                record = {"name": name, "status": "failed", "error": type(error).__name__}
                print(name, "failed", type(error).__name__, flush=True)
            records.append(record)
    path = ROOT / "source-manifest.json"
    path.write_text(json.dumps(sorted(records, key=lambda p: p["name"].lower()), ensure_ascii=False, indent=2), encoding="utf-8")
    unresolved = [r["name"] for r in records if r["status"] != "downloaded"]
    print("Unresolved:", ", ".join(unresolved), flush=True)
    return bool(unresolved)


if __name__ == "__main__":
    sys.exit(main())

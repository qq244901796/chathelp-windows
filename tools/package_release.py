"""Package only an audited clean build, source archives and public documents."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from app.version import VERSION


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    output = ROOT / "outputs/releases"
    output.mkdir(parents=True, exist_ok=True)
    app = ROOT / "dist/chathelp-glm"
    assert (app / "chathelp-glm.exe").is_file()
    assert not (app / "config.json").exists(), "Do not distribute personal settings"
    for name in ("README.md", "LICENSE", "NOTICE", "COPYING", "ABOUT.md", "PRIVACY.md", "LICENSING.md",
                 "THIRD_PARTY_NOTICES.md", "BUILDING.md", "CHANGELOG.md", "TESTING.md",
                 "dependencies.json", "source-manifest.json", "requirements-lock.txt"):
        shutil.copyfile(ROOT / name, app / name)
    shutil.copyfile(ROOT / "source-manifest.json", app / "_internal/source-manifest.json")
    shutil.copytree(ROOT / "licenses", app / "_internal/licenses", dirs_exist_ok=True)
    records = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    files = {}
    for record in records:
        assert record["status"] == "downloaded", record["name"]
        path = ROOT / "outputs/sources" / record["file"]
        if record["file"] not in files:
            assert path.is_file() and digest(path) == record["sha256"], record["name"]
            files[record["file"]] = path
    prefix = "chathelp-windows-" + VERSION
    binary = output / (prefix + "-x64.zip")
    with zipfile.ZipFile(binary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for path in sorted(app.rglob("*")):
            if path.is_file():
                archive.write(path, "chathelp-glm/" + path.relative_to(app).as_posix())
    sources = output / (prefix + "-dependency-sources.zip")
    with zipfile.ZipFile(sources, "w", zipfile.ZIP_STORED) as archive:
        for name, path in sorted(files.items()):
            archive.write(path, "sources/" + name)
        for name in ("source-manifest.json", "BUILDING.md", "LICENSING.md", "COPYING", "requirements-lock.txt"):
            archive.write(ROOT / name, name)
    project = output / (prefix + "-project-source.zip")
    subprocess.run(["git", "archive", "--format=zip", "--prefix=" + prefix + "/", "-o", str(project), "HEAD"], cwd=ROOT, check=True)
    for name in ("source-manifest.json", "CHANGELOG.md"):
        shutil.copyfile(ROOT / name, output / name)
    shutil.copyfile(ROOT / "README.md", output / "INSTALL.txt")
    assets = [binary, sources, project, output / "source-manifest.json", output / "CHANGELOG.md", output / "INSTALL.txt"]
    (output / "SHA256SUMS.txt").write_text("".join(digest(p) + "  " + p.name + "\n" for p in assets), encoding="utf-8")
    for path in assets:
        print(path.name, path.stat().st_size, flush=True)


if __name__ == "__main__":
    main()

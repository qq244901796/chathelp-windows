"""Collect installed distribution notices and freeze the exact build environment.

Run only in the isolated release virtual environment. No credentials are read.
"""
import hashlib
import importlib.metadata as metadata
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]


def main():
    dest = ROOT / "licenses" / "third-party"
    dest.mkdir(parents=True, exist_ok=True)
    packages = []
    for dist in sorted(metadata.distributions(), key=lambda d: d.metadata["Name"].lower()):
        name, version = dist.metadata["Name"], dist.version
        if name.lower() == "pip":
            continue
        license_label = dist.metadata.get("License-Expression") or dist.metadata.get("License") or ""
        if not license_label or len(license_label) > 120:
            license_label = "; ".join(c.rsplit(" :: ", 1)[-1] for c in dist.metadata.get_all("Classifier", [])
                                      if c.startswith("License ::")) or "See bundled license files"
        copied = []
        for file in dist.files or []:
            if ("licenses" in Path(str(file)).parts or any(word in Path(str(file)).name.lower()
                    for word in ("license", "licence", "copying", "notice", "copyright"))):
                original = Path(dist.locate_file(file))
                if not original.is_file() or original.suffix.lower() in (".pyc", ".pyd", ".dll"):
                    continue
                target = dest / name / str(file).replace("../", "parent/").replace("..\\", "parent/")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(original, target)
                copied.append(str(target.relative_to(ROOT)).replace("\\", "/"))
        # Metadata preserves upstream license expressions and source project links.
        package_dir = dest / name
        package_dir.mkdir(parents=True, exist_ok=True)
        (package_dir / "METADATA.txt").write_text(dist.read_text("METADATA") or "", encoding="utf-8")
        packages.append(dict(name=name, version=version, license=license_label,
                             notices=copied, project_urls=dist.metadata.get_all("Project-URL", [])))
    (ROOT / "dependencies.json").write_text(json.dumps(packages, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "requirements-lock.txt").write_text("\n".join(f"{p['name']}=={p['version']}" for p in packages) + "\n", encoding="utf-8")
    table = ["# 第三方依赖与许可", "", "以下为本次 Windows 构建的锁定环境。完整文本位于 `licenses/third-party/`，对应源码见 Release 的 source manifest。",
             "", "| 组件 | 版本 | 许可（以完整文本为准） |", "| --- | --- | --- |"]
    table += [f"| {p['name']} | {p['version']} | {p['license'].replace('|', '/').replace(chr(10), ' ')} |" for p in packages]
    table += ["", "PySide6/Qt 的动态库以独立文件分发，允许按其许可证替换、调试修改；不施加禁止逆向调试修改库的额外条款。",
              "RapidOCR 的模型和相关许可随包保留；Python 与其内置第三方组件见 `licenses/python/`。",
              "PyInstaller 仅用于构建，其分发例外随完整许可证保留。其他构建工具不一定包含在程序中。"]
    (ROOT / "THIRD_PARTY_NOTICES.md").write_text("\n".join(table) + "\n", encoding="utf-8")
    print(f"Collected {len(packages)} distributions; {sum(len(p['notices']) for p in packages)} notice files.")
    print("Packages lacking separate license files: " + ", ".join(p["name"] for p in packages if not p["notices"]))


if __name__ == "__main__":
    main()

# 第三方依赖与许可

以下为本次 Windows 构建的锁定环境。完整文本位于 `licenses/third-party/`，对应源码见 Release 的 source manifest。

| 组件 | 版本 | 许可（以完整文本为准） |
| --- | --- | --- |
| altgraph | 0.17.5 | MIT |
| annotated-types | 0.8.0 | MIT |
| anthropic | 1.8.0 | MIT |
| anyio | 4.15.1 | MIT |
| certifi | 2026.7.22 | MPL-2.0 |
| cffi | 2.1.1 | MIT-0 |
| charset-normalizer | 3.5.1 | MIT |
| colorama | 0.4.6 | BSD License |
| cryptography | 50.0.1 | Apache-2.0 OR BSD-3-Clause |
| darkdetect | 0.8.0 | BSD-3-Clause |
| distro | 1.9.0 | Apache License, Version 2.0 |
| docstring_parser | 0.18.0 | MIT |
| flatbuffers | 25.12.19 | Apache 2.0 |
| google-auth | 2.58.0 | Apache 2.0 |
| google-genai | 2.25.0 | Apache-2.0 |
| h11 | 0.16.0 | MIT |
| httpcore | 1.0.9 | BSD-3-Clause |
| httpcore2 | 2.13.0 | BSD-3-Clause |
| httpx | 0.28.1 | BSD-3-Clause |
| httpx2 | 2.13.0 | BSD-3-Clause |
| idna | 3.20 | BSD-3-Clause |
| jiter | 0.17.0 | MIT |
| numpy | 2.4.6 | BSD-3-Clause AND 0BSD AND MIT AND Zlib AND CC0-1.0 |
| onnxruntime | 1.30.0 | MIT License |
| openai | 3.19.0 | Apache-2.0 |
| opencv-python | 5.0.0.93 | Apache 2.0 |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause |
| pefile | 2024.8.26 | MIT |
| pillow | 12.3.0 | MIT-CMU |
| protobuf | 7.36.2 | 3-Clause BSD License |
| pyasn1 | 0.6.4 | BSD-2-Clause |
| pyasn1_modules | 0.4.2 | BSD |
| pyclipper | 1.4.0 | MIT |
| pycparser | 3.0 | BSD-3-Clause |
| pydantic | 2.13.5 | MIT |
| pydantic_core | 2.46.5 | MIT |
| pyinstaller | 6.22.3 | GNU General Public License v2 (GPLv2) |
| pyinstaller-hooks-contrib | 2026.7 | Apache Software License; GNU General Public License v2 (GPLv2) |
| PySide6 | 6.11.2 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| PySide6-Fluent-Widgets | 1.11.3 | GPLv3 |
| PySide6_Addons | 6.11.2 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| PySide6_Essentials | 6.11.2 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| PySideSix-Frameless-Window | 0.8.2 | LGPLv3 |
| pywin32 | 312 | PSF |
| pywin32-ctypes | 0.2.3 | BSD-3-Clause |
| PyYAML | 6.0.3 | MIT |
| rapidocr-onnxruntime | 1.4.4 | Apache-2.0 |
| requests | 2.34.2 | Apache-2.0 |
| setuptools | 65.5.0 | MIT License |
| shapely | 2.1.2 | BSD 3-Clause |
| shiboken6 | 6.11.2 | LGPL-3.0-only OR GPL-2.0-only OR GPL-3.0-only |
| six | 1.17.0 | MIT |
| sniffio | 1.3.1 | MIT OR Apache-2.0 |
| tenacity | 9.1.4 | Apache 2.0 |
| tqdm | 4.70.1 | MPL-2.0 AND MIT |
| truststore | 0.10.4 | MIT |
| typesafe-sdk | 0.7.1 | MIT |
| typing-inspection | 0.4.4 | MIT |
| typing_extensions | 4.16.0 | PSF-2.0 |
| urllib3 | 2.8.0 | MIT |
| websockets | 16.1.1 | BSD-3-Clause |
| windows-capture | 2.0.1 | MIT |

PySide6/Qt 的动态库以独立文件分发，允许按其许可证替换、调试修改；不施加禁止逆向调试修改库的额外条款。
RapidOCR 的模型和相关许可随包保留；Python 与其内置第三方组件见 `licenses/python/`。
PyInstaller 仅用于构建，其分发例外随完整许可证保留。其他构建工具不一定包含在程序中。

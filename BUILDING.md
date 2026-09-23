# 构建与对应源码

测试环境：Windows 11 x64、CPython 3.11.6 x64。安装 Windows SDK/Visual C++ 运行库并使用 ASCII 路径。无需模型密钥即可构建和运行本地测试。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-lock.txt
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\pyinstaller.exe --noconfirm --clean jev.spec
```

也可执行 build.bat。将整个 dist/chathelp-glm 目录压缩发送，不能只复制 exe。构建不要求签名证书。依赖锁定用于重建同样的依赖组合，不承诺不同机器逐字节产物一致。

`requirements.txt` 是上游宽松依赖范围，正式构建请使用 `requirements-lock.txt`。`tools/collect_licenses.py` 从独立构建环境生成许可清单；`tools/collect_sources.py` 和 `tools/collect_native_sources.py` 下载对应源码并记录 SHA256。不要在含其他个人 Python 包的全局环境生成清单。

## 修改依赖

从同 Release 下载 dependency-sources.zip，按 source-manifest.json 核验；原始归档内保留各项目的构建系统与使用说明。PySide6/Shiboken 来自 pyside-setup-everywhere-src-6.11.2，Qt 来自 6.11.2 的 qtbase、qtsvg、qtimageformats、qttranslations 模块；实际使用的 QtCore/Gui/Widgets/Network/OpenGL/Xml 等均属于这些模块。打包脚本明确排除未使用的 PDF 与虚拟键盘插件及其 QtWebEngine/QML 依赖。Fluent Widgets 的对应源码来自 PyPI 同版本源码包。Python 原始源码内包含 PCbuild 的 Windows 构建说明。

通常可在独立虚拟环境中安装自己修改后的 wheel，再重新运行 PyInstaller。编译 Qt/PySide6 原生组件需按各源包 README 准备匹配版本的 MSVC、CMake、Ninja 与 Clang；PySide6 构建入口为其 setup.py，Qt 为 configure.bat + CMake。遵照源包文档选择需要的模块，避免引入额外的许可组件。

动态库保存在分发目录 `_internal/PySide6/`、`_internal/shiboken6/`、`_internal/shapely.libs/` 等位置，可用相同架构/兼容 ABI 的修改版本替换；如改变 ABI，应从源码重新打包整个应用。这里不设置签名校验或其他替换限制，允许为调试修改库而逆向分析。请保留各库所需插件及运行时文件。

`chathelp-glm.exe --smoke-test <输出目录>` 只使用合成对话与图片运行离线检查，不采集微信、不保存真实配置；适用于检查冻结包的模块、中文 OCR 和界面资源。

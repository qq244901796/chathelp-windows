# 许可范围与再分发

上游 LICENSE（MIT）与 NOTICE 原文保留。它们说明 Jev 自有代码的来源及授权，不表示整个 Windows 分发包只受 MIT 约束。

本版保留 PySide6-Fluent-Widgets 界面组件，采用其 GPLv3 开源许可。因此将本修改版组合程序按 GPL-3.0-only 分发，完整文本见 COPYING；本分支新增代码、文档与原创图标也按 GPL-3.0-only 提供，Copyright (c) 2026 ChatHelp contributors。上游 MIT 部分继续保留 MIT 声明，其他依赖保持原许可。

允许依许可证使用、研究、修改和再分发，包括商业用途。GPL 不等于“禁止商用”；上游 NOTICE 中提到的商业授权是有关组件的另一种许可选项，本版未购买或使用该选项。再分发此组合程序时应履行 GPL 的完整对应源码与许可保留义务，不能以本仓库保留的 MIT 文件为由闭源分发。

## 对应源码和构建

完整项目源码、测试、构建脚本与依赖锁定见同版本 tag 和 Release 中的 project-source.zip；依赖源码见同处 dependency-sources.zip。source-manifest.json 记录每份源码的确切版本、上游 URL 与 SHA256。源码提供位置与二进制在同一 Release，无额外收费：

https://github.com/qq244901796/chathelp-windows/releases/tag/v1.0.0-glm

源包含 GPL 界面组件源码、Qt/PySide6/Shiboken 对应源码及 GEOS 等依赖源码。构建步骤见 BUILDING.md。没有安装锁、授权服务器或必须使用维护者私钥的机制；可自行修改、构建和运行。此测试版 exe 未进行 Authenticode 签名。

## Qt / PySide6 与其他依赖

使用 Qt/PySide6 开源选项，保留适用的 LGPLv3/GPLv3 文本、例外及第三方许可。Qt、PySide6、GEOS 等动态库以独立文件提供，允许按其许可替换、调试与逆向分析修改部分；不施加禁止上述行为的额外条款。替换方法及 ABI 注意事项见 BUILDING.md。

依赖版本、版权与完整文本见 THIRD_PARTY_NOTICES.md、dependencies.json、licenses/。源码归档保留原始源树与构建说明，依赖没有本分支补丁。RapidOCR 的模型来自其原项目/PP-OCR 系列，相关 Apache-2.0 文本和声明一并提供。Python 及其内置第三方组件见 licenses/python/。

在线模型服务、其他聊天平台和第三方商标不属于本软件开源授权。本项目仅说明软件再分发处理，不承诺任何平台允许所有自动化使用场景。

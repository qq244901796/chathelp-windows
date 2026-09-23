"""Display bundled notices offline; never read a user's configuration."""
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTabWidget, QTextBrowser, QPushButton


def show_legal(parent):
    root = Path(__file__).resolve().parents[1]
    dialog = QDialog(parent)
    dialog.setWindowTitle("ChatHelp · 关于、许可与隐私")
    dialog.resize(680, 520)
    layout = QVBoxLayout(dialog)
    tabs = QTabWidget()
    for title, filename in (("关于", "ABOUT.md"), ("隐私", "PRIVACY.md"),
                            ("许可说明", "LICENSING.md"), ("第三方", "THIRD_PARTY_NOTICES.md"),
                            ("上游声明", "NOTICE"), ("MIT", "LICENSE"), ("GPLv3", "COPYING")):
        view = QTextBrowser()
        view.setOpenExternalLinks(True)
        path = root / filename
        text = path.read_text(encoding="utf-8") if path.is_file() else "请查看发布包随附的许可文件。"
        if filename.endswith(".md"):
            view.setMarkdown(text)
        else:
            view.setPlainText(text)
        tabs.addTab(view, title)
    layout.addWidget(tabs)
    close = QPushButton("关闭")
    close.clicked.connect(dialog.accept)
    layout.addWidget(close)
    dialog.exec()

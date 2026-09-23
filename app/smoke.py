"""Explicit, offline packaged-app check with synthetic inputs and no user settings."""
import json
import os
from pathlib import Path
import tempfile
import traceback


def run(output):
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    destination = Path(output).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    result = {"synthetic_only": True, "network_used": False}
    try:
        import socket
        # Blocks all sockets for the complete smoke check, including OCR initialization.
        def blocked(*args, **kwargs):
            raise RuntimeError("Network is disabled during smoke test")
        socket.socket.connect = blocked
        from app import settings
        from app.overlay import Overlay
        from app.ocr import _engine
        from PIL import Image, ImageDraw, ImageFont
        from PySide6.QtGui import QFontDatabase
        from PySide6.QtWidgets import QApplication
        import numpy as np
        with tempfile.TemporaryDirectory() as temporary:
            settings._CONFIG = Path(temporary) / "config.json"
            settings._read_env = lambda name: ""
            font_path = str(Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts/msyh.ttc")
            app = QApplication.instance() or QApplication([])
            QFontDatabase.addApplicationFont(font_path)
            for filename in ("segoeui.ttf", "segoeuib.ttf", "arial.ttf", "consola.ttf"):
                QFontDatabase.addApplicationFont(str(Path(font_path).with_name(filename)))
            overlay = Overlay(on_fill=lambda text: None)
            overlay.set_capture(False, "离线测试 · 使用虚构数据")
            overlay.open_settings()
            overlay.win.show()
            overlay.app.processEvents()
            assert overlay._provider_of(overlay.jev) == "zhipu"
            assert overlay.draft.keyEdit.isHidden()
            overlay.win.grab().save(str(destination / "settings.png"))
            canvas = Image.new("RGB", (1000, 170), "white")
            ImageDraw.Draw(canvas).text((30, 40), "你好，明天下午三点见面", font=ImageFont.truetype(font_path, 48), fill="black")
            rows, _ = _engine()(np.asarray(canvas), use_cls=False)
            assert "明天下午三点" in "".join(row[1] for row in rows)
            from core.bigmodel import parse_object
            assert parse_object('{"replies":["好的","可以","收到"]}')["replies"][0] == "好的"
            root = Path(__file__).resolve().parents[1]
            for name in ("COPYING", "LICENSE", "NOTICE", "ABOUT.md", "PRIVACY.md", "LICENSING.md", "source-manifest.json"):
                assert (root / name).is_file(), name
            assert not settings._CONFIG.exists()
            overlay.win.close()
            overlay.app.processEvents()
        result.update(ok=True, ocr=True, settings=True, notices=True)
    except Exception:
        result.update(ok=False, error=traceback.format_exc())
    (destination / "smoke.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0 if result["ok"] else 1

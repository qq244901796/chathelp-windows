import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

import socket
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, Mock

from app import settings


class DesktopTests(unittest.TestCase):
    def test_ocr_without_network(self):
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        from app.ocr import _engine
        canvas = Image.new("RGB", (1080, 300), "white")
        painter = ImageDraw.Draw(canvas)
        font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 48)
        painter.text((35, 40), "你好，明天下午三点见面", fill="black", font=font)
        painter.text((35, 150), "好的，我们到时联系", fill="black", font=font)
        with patch.object(socket.socket, "connect", side_effect=AssertionError("OCR attempted network")):
            rows, _ = _engine()(np.asarray(canvas), use_cls=False)
        text = "".join(row[1] for row in rows)
        self.assertIn("明天下午三点", text)
        self.assertIn("到时联系", text)

    def test_settings_ui_uses_one_key_and_test_does_not_save(self):
        from app.overlay import Overlay
        from PySide6.QtTest import QTest
        with tempfile.TemporaryDirectory() as temp, patch.object(settings, "_CONFIG", Path(temp) / "config.json"), \
                patch.object(settings, "_read_env", return_value=""), patch.object(settings, "_set_key") as write:
            overlay = Overlay(on_fill=lambda text: None)
            try:
                overlay.open_settings()
                self.assertEqual(overlay._provider_of(overlay.jev), "zhipu")
                self.assertTrue(overlay.draft.keyEdit.isHidden())
                overlay.jev.keyEdit.setText("synthetic-ui-token")
                config = overlay._form_config()
                self.assertEqual(config["judge_api_key"], config["draft_api_key"])
                with patch("core.engine.analyze", return_value={}) as analyze:
                    overlay._test_flow()
                    for _ in range(100):
                        QTest.qWait(10)
                        if overlay.testButton.isEnabled():
                            break
                    self.assertTrue(overlay.testButton.isEnabled())
                    analyze.assert_called_once()
                self.assertFalse((Path(temp) / "config.json").exists())
                write.assert_not_called()
                overlay._save()
                self.assertTrue((Path(temp) / "config.json").exists())
                self.assertNotIn("synthetic-ui-token", (Path(temp) / "config.json").read_text(encoding="utf-8"))
            finally:
                overlay.win.close()
                overlay.app.processEvents()

    def test_fill_rejects_stale_result_without_touching_clipboard(self):
        import main
        from core.session import Session
        fake_overlay = Mock()
        fake_overlay.current_chat.return_value = "当前"
        with patch.object(main, "ov", fake_overlay, create=True), \
                patch.object(main, "session", Session()), \
                patch.object(main, "chats", {}), \
                patch.object(main, "state", dict(chat="当前", busy=False, hwnd=1, area=(0, 0, 10, 10))), \
                patch.object(settings, "reply_target", return_value=False), patch.object(main, "fill") as fill:
            chat = main.chat_of("当前")
            chat["result"] = {"candidates": ["合成回复"]}
            chat["ticket"] = main.session.ticket("当前", chat["rev"], None)
            main.session.invalidate()
            with self.assertRaises(RuntimeError):
                main.fill_reply("合成回复")
            fill.assert_not_called()


if __name__ == "__main__":
    unittest.main()

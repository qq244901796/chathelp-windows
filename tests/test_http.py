import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
import unittest
from unittest.mock import patch, Mock

from core import bigmodel
from core.jev_client import JevError


class WireTests(unittest.TestCase):
    def test_real_http_payload_retry_and_no_redirect(self):
        seen = []
        responses = [429, 200, 302, 401]

        class Handler(BaseHTTPRequestHandler):
            def do_POST(self):
                seen.append((self.path, self.headers.get("Authorization"),
                             json.loads(self.rfile.read(int(self.headers["Content-Length"])))))
                status = responses.pop(0)
                self.send_response(status)
                self.send_header("Location", "/should-never-follow")
                self.send_header("Retry-After", "0")
                self.end_headers()
                self.wfile.write(json.dumps({"choices": [{"finish_reason": "stop", "message": {
                    "content": '{"ok":true}'}}]}).encode())

            def log_message(self, *args):
                pass

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.object(bigmodel, "BIGMODEL_BASE", f"http://127.0.0.1:{server.server_port}"), \
                    patch.object(bigmodel.time, "sleep"):
                self.assertTrue(bigmodel.complete("system", "虚构对话", "synthetic-wire")[0]["ok"])
                for _ in range(2):
                    with self.assertRaises(JevError):
                        bigmodel.complete("system", "虚构对话", "synthetic-wire")
            self.assertEqual(len(seen), 4)
            self.assertTrue(all(path == "/chat/completions" for path, _, _ in seen))
            self.assertTrue(all(auth == "Bearer synthetic-wire" for _, auth, _ in seen))
            self.assertEqual(seen[0][2]["response_format"], {"type": "json_object"})
            self.assertNotIn("questions", seen[0][2])
        finally:
            server.shutdown()
            server.server_close()
            thread.join()

    def test_fill_emits_paste_but_never_enter(self):
        import app.fill as filling
        user = Mock()
        user.GetForegroundWindow.return_value = 123
        with patch.object(filling, "u32", user), patch.object(filling, "set_clipboard") as clip, \
                patch("app.capture.unminimize"), patch.object(filling.time, "sleep"), \
                patch.object(filling.ctypes.windll.dwmapi, "DwmGetWindowAttribute", return_value=0):
            filling.fill(123, (10, 20, 100, 200), "虚构回复")
        clip.assert_called_once_with("虚构回复")
        keys = [call.args[0] for call in user.keybd_event.call_args_list]
        self.assertEqual(keys, [0x11, 0x23, 0x23, 0x11, 0x11, 0x56, 0x56, 0x11])
        self.assertNotIn(0x0D, keys)
        self.assertEqual(user.mouse_event.call_count, 2)


if __name__ == "__main__":
    unittest.main()

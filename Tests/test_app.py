# Copyright © 2026 liw10152-vanessa. All rights reserved.
import json
import sys
import threading
import unittest
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app


class FakeController:
    def __init__(self):
        self.actions = []

    def perform(self, action):
        self.actions.append(action)


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.controller = FakeController()
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), app.make_handler("123456", cls.controller))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def test_health_does_not_require_pairing(self):
        with urllib.request.urlopen(self.base + "/health") as response:
            self.assertEqual(json.load(response)["ok"], True)

    def test_state_requires_pairing(self):
        with self.assertRaises(urllib.error.HTTPError) as caught:
            urllib.request.urlopen(self.base + "/api/state")
        self.assertEqual(caught.exception.code, 401)

    def test_remote_shell_can_reload_without_code(self):
        with urllib.request.urlopen(self.base + "/") as response:
            html = response.read().decode("utf-8")
        self.assertIn("视频遥控器", html)
        self.assertIn("X-Pair-Code", html)

    @mock.patch.object(app, "current_state")
    def test_action_is_dispatched(self, state):
        state.return_value = {"controls": app.GENERIC_CONTROLS}
        request = urllib.request.Request(
            self.base + "/api/action",
            data=json.dumps({"action": "playPause"}).encode(),
            headers={"Content-Type": "application/json", "X-Pair-Code": "123456"},
            method="POST",
        )
        with urllib.request.urlopen(request) as response:
            self.assertEqual(json.load(response)["ok"], True)
        self.assertEqual(self.controller.actions[-1], "playPause")


class ProfileTests(unittest.TestCase):
    @mock.patch.object(app, "run_helper")
    def test_bilibili_is_detected(self, helper):
        helper.return_value.stdout = json.dumps({
            "appName": "哔哩哔哩", "bundleIdentifier": "com.bilibili.bilibiliPC",
            "accessibilityTrusted": True,
        })
        state = app.current_state()
        self.assertEqual(state["profile"], "哔哩哔哩")
        self.assertIn("speedUp", state["controls"])


if __name__ == "__main__":
    unittest.main()

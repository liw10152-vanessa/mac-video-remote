#!/usr/bin/env python3
# Copyright © 2026 liw10152-vanessa. All rights reserved.
# Personal-use permission is described in LICENSE.md.
"""Local-only iPhone remote for video playback on macOS."""

import argparse
import ipaddress
import json
import os
import secrets
import signal
import socket
import subprocess
import threading
import time
from collections import deque
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent
HELPER = ROOT / "build" / "remote-helper"
WEB_UI = ROOT / "Sources" / "MacVideoRemote" / "Resources" / "index.html"

PROFILES = {
    "com.bilibili.bilibiliPC": {
        "name": "哔哩哔哩",
        "controls": ["playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
                     "speedNormal", "speedDouble", "speedUp", "speedDown", "fullscreen", "mute",
                     "volumeDown", "volumeUp"],
    },
    "com.quark.desktop": {
        "name": "夸克",
        "controls": ["playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
                     "speedNormal", "speedDouble", "speedUp", "speedDown", "fullscreen", "mute",
                     "volumeDown", "volumeUp"],
    },
    "com.bytedance.douyin.desktop": {
        "name": "抖音",
        "controls": ["playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
                     "fullscreen", "mute", "volumeDown", "volumeUp"],
    },
    "com.xingin.discover": {
        "name": "小红书",
        "controls": ["playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
                     "fullscreen", "mute", "volumeDown", "volumeUp"],
    },
}

BROWSERS = {
    "com.apple.Safari": "Safari 网页视频",
    "com.google.Chrome": "Chrome 网页视频",
    "com.microsoft.edgemac": "Edge 网页视频",
    "company.thebrowser.Browser": "Arc 网页视频",
    "com.brave.Browser": "Brave 网页视频",
    "org.mozilla.firefox": "Firefox 网页视频",
}

GENERIC_CONTROLS = ["playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
                    "speedNormal", "speedDouble", "fullscreen", "mute", "volumeDown", "volumeUp"]
BROWSER_FALLBACK_CONTROLS = [
    "playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
    "fullscreen", "mute", "volumeDown", "volumeUp",
]
BROWSER_CONTROLS = [
    "playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
    "speedHalf", "speedNormal", "speed125", "speed150", "speedDouble", "speedUp", "speedDown",
    "fullscreen", "mute", "volumeDown", "volumeUp",
]
BROWSER_EXTENSION_ACTIONS = {
    "playPause", "seekBackward", "seekForward", "holdFastStart", "holdFastEnd",
    "speedHalf", "speedNormal", "speed125", "speed150", "speedDouble", "speedUp", "speedDown",
    "mute",
}

KEY_ACTIONS = {
    "playPause": (49, ""),       # Space
    "seekBackward": (123, ""),  # Left arrow
    "seekForward": (124, ""),   # Right arrow
    "fullscreen": (3, ""),      # F
    "mute": (46, ""),           # M
    "speedNormal": (18, "shift"),
    "speedDouble": (19, "shift"),
    "speedUp": (30, ""),        # ]
    "speedDown": (33, ""),      # [
}


def run_helper(*arguments, check=False):
    return subprocess.run([str(HELPER), *map(str, arguments)], capture_output=True, text=True, check=check)


def load_or_create_pairing_code():
    config_dir = Path.home() / "Library" / "Application Support" / "MacVideoRemote"
    code_file = config_dir / "pairing-code"
    try:
        existing = code_file.read_text(encoding="utf-8").strip()
        if len(existing) == 6 and existing.isdigit():
            return existing
    except FileNotFoundError:
        pass
    config_dir.mkdir(parents=True, exist_ok=True)
    code = f"{secrets.randbelow(1_000_000):06d}"
    code_file.write_text(code + "\n", encoding="utf-8")
    os.chmod(code_file, 0o600)
    return code


def discover_lan_ipv4():
    """Return a private Wi-Fi/Ethernet IPv4 address suitable for iPhone access."""
    for interface in ("en0", "en1"):
        try:
            result = subprocess.run(
                ["/usr/sbin/ipconfig", "getifaddr", interface],
                capture_output=True,
                text=True,
                check=False,
            )
            candidate = result.stdout.strip()
            address = ipaddress.ip_address(candidate)
            if address.version == 4 and address.is_private and not address.is_loopback:
                return candidate
        except (OSError, ValueError):
            continue
    return None


class BrowserCommandBroker:
    """Small authenticated command queue for the optional Chromium extension."""

    def __init__(self):
        self._lock = threading.Lock()
        self._commands = deque(maxlen=32)
        self._sequence = 0
        self._last_seen = 0.0

    @property
    def connected(self):
        with self._lock:
            return self._last_seen > 0 and time.monotonic() - self._last_seen < 3.0

    def publish(self, action):
        with self._lock:
            self._sequence += 1
            self._commands.append({"id": self._sequence, "action": action})
            return self._sequence

    def poll(self, since=None):
        with self._lock:
            self._last_seen = time.monotonic()
            if since is None:
                return {"cursor": self._sequence, "commands": []}
            commands = [item for item in self._commands if item["id"] > since]
            return {"cursor": self._sequence, "commands": commands}


def current_state(browser_broker=None):
    try:
        raw = json.loads(run_helper("state", check=True).stdout)
    except (subprocess.SubprocessError, json.JSONDecodeError, OSError):
        raw = {"appName": "未知 App", "bundleIdentifier": "unknown", "accessibilityTrusted": False}
    bundle_identifier = raw["bundleIdentifier"]
    if bundle_identifier in BROWSERS:
        enhanced = bool(browser_broker and browser_broker.connected)
        return {
            **raw,
            "profile": BROWSERS[bundle_identifier],
            "controls": BROWSER_CONTROLS if enhanced else BROWSER_FALLBACK_CONTROLS,
            "controlMode": "browser-extension" if enhanced else "keyboard",
            "message": "网页增强控制已连接" if enhanced else "通用按键模式；安装扩展可获得精确倍速",
        }
    profile = PROFILES.get(bundle_identifier, {"name": "通用视频", "controls": GENERIC_CONTROLS})
    return {
        **raw,
        "profile": profile["name"],
        "controls": profile["controls"],
        "controlMode": "keyboard",
        "message": "控制 Mac 当前最前面的应用",
    }


class Controller:
    def __init__(self):
        self._lock = threading.Lock()
        self._hold_process = None
        self._hold_timeout = None

    def perform(self, action):
        if action == "holdFastStart":
            self.start_hold()
        elif action == "holdFastEnd":
            self.stop_hold()
        elif action in ("volumeUp", "volumeDown"):
            delta = 6 if action == "volumeUp" else -6
            script = f"set volume output volume ((output volume of (get volume settings)) + ({delta}))"
            subprocess.Popen(["/usr/bin/osascript", "-e", script], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif action in KEY_ACTIONS:
            key, flags = KEY_ACTIONS[action]
            subprocess.Popen([str(HELPER), "tap", str(key), flags], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            raise ValueError("未知控制指令")

    def start_hold(self):
        with self._lock:
            self._stop_hold_locked()
            self._hold_process = subprocess.Popen([str(HELPER), "hold", "124"],
                                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self._hold_timeout = threading.Timer(10.0, self.stop_hold)
            self._hold_timeout.daemon = True
            self._hold_timeout.start()

    def stop_hold(self):
        with self._lock:
            self._stop_hold_locked()

    def _stop_hold_locked(self):
        if self._hold_timeout:
            self._hold_timeout.cancel()
            self._hold_timeout = None
        if self._hold_process and self._hold_process.poll() is None:
            self._hold_process.terminate()
            try:
                self._hold_process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                self._hold_process.kill()
        self._hold_process = None


def make_handler(pairing_code, controller, browser_broker=None):
    browser_broker = browser_broker or BrowserCommandBroker()

    class RequestHandler(BaseHTTPRequestHandler):
        server_version = "MacVideoRemote/0.2"

        def log_message(self, fmt, *args):
            return

        def send_json(self, status, payload):
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(data)

        def authenticated(self, parsed):
            query_code = parse_qs(parsed.query).get("code", [None])[0]
            return secrets.compare_digest(query_code or self.headers.get("X-Pair-Code", ""), pairing_code)

        def do_GET(self):
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                return self.send_json(200, {"ok": True, "message": "Mac Video Remote is running"})
            if parsed.path == "/":
                data = WEB_UI.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(data)))
                self.send_header("Cache-Control", "no-store")
                self.end_headers()
                return self.wfile.write(data)
            if not self.authenticated(parsed):
                return self.send_json(401, {"ok": False, "message": "配对码不正确"})
            if parsed.path == "/api/state":
                return self.send_json(200, current_state(browser_broker))
            if parsed.path == "/api/browser/poll":
                raw_since = parse_qs(parsed.query).get("since", [None])[0]
                try:
                    since = int(raw_since) if raw_since is not None else None
                except ValueError:
                    return self.send_json(400, {"ok": False, "message": "since 必须是整数"})
                return self.send_json(200, browser_broker.poll(since))
            return self.send_json(404, {"ok": False, "message": "Not Found"})

        def do_POST(self):
            parsed = urlparse(self.path)
            if not self.authenticated(parsed):
                return self.send_json(401, {"ok": False, "message": "配对码不正确"})
            if parsed.path != "/api/action":
                return self.send_json(404, {"ok": False, "message": "Not Found"})
            try:
                length = min(int(self.headers.get("Content-Length", 0)), 4096)
                action = json.loads(self.rfile.read(length))["action"]
                state = current_state(browser_broker)
                if action not in state["controls"]:
                    raise ValueError("当前配置不支持该指令")
                if state["controlMode"] == "browser-extension" and action in BROWSER_EXTENSION_ACTIONS:
                    browser_broker.publish(action)
                    transport = "browser-extension"
                else:
                    controller.perform(action)
                    transport = "keyboard"
                return self.send_json(200, {"ok": True, "message": action, "transport": transport})
            except (ValueError, KeyError, json.JSONDecodeError) as error:
                return self.send_json(400, {"ok": False, "message": str(error)})

    return RequestHandler


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--code", help="固定六位配对码，仅用于测试")
    args = parser.parse_args()
    if not HELPER.exists():
        raise SystemExit("缺少原生辅助程序，请先运行 ./scripts/build.sh")

    pairing_code = args.code or load_or_create_pairing_code()
    hostname = socket.gethostname().split(".")[0] + ".local"
    lan_ip = discover_lan_ipv4()
    controller = Controller()
    browser_broker = BrowserCommandBroker()
    server = ThreadingHTTPServer(
        ("0.0.0.0", args.port),
        make_handler(pairing_code, controller, browser_broker),
    )

    def stop_server(*_):
        controller.stop_hold()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGINT, stop_server)
    signal.signal(signal.SIGTERM, stop_server)
    run_helper("prompt")
    recommended_url = (
        f"http://{lan_ip}:{args.port}/?code={pairing_code}"
        if lan_ip
        else f"http://{hostname}:{args.port}/?code={pairing_code}"
    )
    backup_url = f"http://{hostname}:{args.port}/?code={pairing_code}"
    print(f"""
Mac Video Remote 已启动
在 iPhone Safari 打开（推荐，添加到主屏幕也使用这个地址）：
{recommended_url}

备用 .local 地址：
{backup_url}

配对码：{pairing_code}
首次使用请在“系统设置 → 隐私与安全性 → 辅助功能”允许 Terminal 控制电脑。
按 Control-C 停止服务。
""")
    server.serve_forever()
    server.server_close()


if __name__ == "__main__":
    main()

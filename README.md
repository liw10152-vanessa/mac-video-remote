# Mac Video Remote

[简体中文](README.zh-CN.md) · English

![Mac Video Remote — control Mac video playback from an iPhone](assets/social-preview.jpg)

**Control video playback on your Mac from an iPhone over local Wi-Fi.** Pause, seek, adjust speed, change volume, enter fullscreen, or hold to fast-forward—without installing an iPhone app.

[![macOS 13+](https://img.shields.io/badge/macOS-13%2B-111827?logo=apple)](#requirements)
[![iPhone Safari](https://img.shields.io/badge/iPhone-Safari-2563EB?logo=safari)](#quick-start)
[![Tests](https://img.shields.io/badge/tests-4%20passing-16A34A)](#development)
[![License](https://img.shields.io/badge/license-personal%20use-orange)](LICENSE.md)

> This is a public source-available project, not an open-source project. Copyright is retained by the author. Personal, non-commercial use of the unmodified software is permitted under the [license](LICENSE.md).

## Why

Sometimes the Mac is just far enough away that pausing a video or changing playback speed means getting up. Mac Video Remote turns any iPhone browser into a focused media remote for the frontmost Mac app.

## Features

- Play/pause, seek backward/forward, fullscreen, mute, and system volume
- 1× and 2× playback shortcuts plus app-specific speed controls
- Press-and-hold fast-forward that releases immediately when your finger lifts
- Automatic profiles for Quark (`com.quark.desktop`) and Bilibili (`com.bilibili.bilibiliPC`)
- Generic fallback for video websites and other media apps
- No iPhone app, account, cloud service, analytics, or third-party dependency
- Local-network pairing protected by a persistent private code
- Native macOS keyboard events through public `CGEvent` and Accessibility APIs

## Actual iPhone interface

<p align="center">
  <img src="assets/iphone-remote.png" width="300" alt="Actual Mac Video Remote interface rendered at iPhone size">
</p>

The app name and active profile shown at the top update automatically based on the frontmost Mac application.

## Requirements

- macOS 13 or later on Apple silicon
- iPhone and Mac connected to the same trusted Wi-Fi network
- Python 3 and Apple Clang command-line tools (included on the development Mac)
- Accessibility permission for Terminal

## Quick start

```bash
git clone https://github.com/liw10152-vanessa/mac-video-remote.git
cd mac-video-remote
./scripts/run.sh
```

Alternatively, double-click `启动视频遥控器.command` in Finder.

On first launch:

1. Open **System Settings → Privacy & Security → Accessibility**.
2. Allow Terminal to control the Mac, then restart the service.
3. Keep the terminal window open.
4. Open the printed `http://your-mac.local:8765/?code=...` URL in iPhone Safari.
5. Use Safari's Share menu to **Add to Home Screen**.

The pairing code is generated once and stored with owner-only file permissions in:

```text
~/Library/Application Support/MacVideoRemote/pairing-code
```

The web interface removes the code from the visible address bar after pairing and keeps it only in local browser storage.

## Controls and compatibility

| Control | Sent to the Mac | Notes |
| --- | --- | --- |
| Play / pause | Space | Works in most focused video players |
| Seek backward / forward | Left / Right Arrow | Jump duration depends on the player |
| Hold to fast-forward | Repeated Right Arrow key-down | Automatically releases after a safety timeout |
| 1× / 2× | Shift+1 / Shift+2 | Confirmed for Bilibili; other apps may vary |
| Fullscreen / mute | F / M | Requires the player to have keyboard focus |
| Volume | macOS system volume | Works independently of player shortcuts |

Before walking away, start the video and click the player once so it has keyboard focus. Commands are sent to the frontmost application.

## Privacy and security

- The service runs locally and does not upload browsing or playback data.
- The pairing file is created with `0600` permissions.
- Pairing checks use constant-time comparison.
- Long-press input has a server-side release timeout to avoid a stuck key.
- Traffic is plain HTTP on the local network; use only a trusted Wi-Fi network.
- Anyone who knows the pairing URL while the service is running can send controls. Do not publish or share it.

See [SECURITY.md](SECURITY.md) for the threat model and reporting guidance.

## Architecture

The project intentionally stays small:

- `app.py` — local HTTP API, pairing, profile detection, and command dispatch
- `native/remote_helper.m` — native macOS app detection and `CGEvent` keyboard synthesis
- `Sources/MacVideoRemote/Resources/index.html` — dependency-free iPhone remote UI
- `Tests/test_app.py` — pairing, dispatch, and profile tests

More detail is available in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Development

```bash
./scripts/build.sh
PYTHONPYCACHEPREFIX=/tmp/mac-video-remote-pycache \
  python3 -m unittest discover -s Tests -v
```

## Roadmap

- Signed menu-bar macOS application
- QR-code pairing
- Configurable per-app shortcuts
- Native iOS companion after the macOS app is packaged
- Additional verified player profiles

Feature ideas and bug reports are welcome through [GitHub Issues](https://github.com/liw10152-vanessa/mac-video-remote/issues). Review [CONTRIBUTING.md](CONTRIBUTING.md) before submitting code.

## Copyright and license

Copyright © 2026 `liw10152-vanessa`. All rights reserved.

The software is source-available for inspection and portfolio presentation. The [project license](LICENSE.md) permits personal, non-commercial use of the unmodified software but does not permit redistribution, derivative works, sublicensing, or commercial use without prior written permission.

This project is independent and is not affiliated with, endorsed by, or sponsored by Apple, Bilibili, or Quark. Product and company names are used only to describe compatibility.

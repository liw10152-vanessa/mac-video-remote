# Architecture

Mac Video Remote uses a deliberately small local-only architecture.

```text
iPhone Safari
    │ local HTTP + pairing code
    ▼
Python HTTP server (`app.py`)
    ├── frontmost-app profile selection
    ├── pairing and action validation
    ├── authenticated browser-command queue
    ├── hold-process lifecycle and safety timeout
    └── system-volume AppleScript
        │                         │ localhost polling
        ▼                         ▼
Native helper (`remote_helper.m`)
    ├── NSWorkspace frontmost application lookup
    ├── Accessibility trust status
    └── CGEvent keyboard tap / repeated key-down / key-up
                                  Chromium extension
                                  └── active HTML5 `<video>` control
```

## Design decisions

### Browser remote instead of an iOS application

The iPhone interface is a dependency-free webpage served directly by the Mac. This avoids App Store distribution and lets a user add the remote to the iPhone Home Screen immediately.

### Native helper instead of a Python GUI dependency

The helper uses public macOS frameworks for frontmost-application detection and keyboard events. Python handles only the small HTTP and state layer.

### Player profiles instead of private media APIs

Profiles map remote actions to documented or commonly supported keyboard controls. This avoids private playback frameworks and keeps compatibility logic explicit.

### Optional browser extension for exact web control

Websites do not share a standard keyboard shortcut for playback speed. The optional Manifest V3 extension polls an authenticated localhost queue only from a focused page containing video, then operates on the largest visible HTML5 video. A new extension session initializes at the newest queue cursor so stale actions are never replayed.

If the extension has not polled recently, the server automatically reports keyboard mode and uses the normal frontmost-app fallback. System volume and fullscreen remain native controls.

### Persistent local pairing code

The code is created once with `0600` permissions so an iPhone Home Screen shortcut remains usable. It is transmitted only on the local HTTP connection and removed from the visible address bar after the first page load.

## Security boundaries

This design assumes a trusted LAN. It does not provide TLS, public-internet authentication, user accounts, or device identity verification. See [SECURITY.md](../SECURITY.md).

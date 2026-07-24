# Changelog

All notable changes to Mac Video Remote are documented here.

## Unreleased

### Added

- Automatic profiles for Douyin and Rednote/Xiaohongshu
- Browser detection for Safari, Chrome, Edge, Arc, Brave, and Firefox
- Optional local Chromium extension for exact HTML5 video control
- 0.5×, 1.25×, 1.5×, and direct webpage playback-speed actions
- Authenticated browser-command queue with stale-command protection
- Google AI Studio deployment-boundary guide to prevent nonfunctional cloud remotes
- English and Chinese product documentation
- Original social-preview artwork and a real iPhone-size UI screenshot
- Personal-use source-available license and explicit copyright notices
- Security policy, contribution policy, architecture guide, and Issue templates
- Server-side safety timeout for hold-to-fast-forward
- Pairing-code removal from the visible browser address after connection

### Changed

- Webpages automatically switch between enhanced extension control and keyboard fallback
- Hold-to-fast-forward uses temporary 3× speed in enhanced webpage mode
- Corrected Bilibili speed-up/down key codes to `]` and `[`
- Corrected outdated Swift Package and rotating-code statements
- Clarified supported applications, privacy boundaries, and network risks

## 0.1.0 — 2026-07-22

- Initial local-network iPhone remote
- Bilibili, Quark, and generic application profiles
- Play/pause, seek, speed, fullscreen, mute, volume, and hold-to-fast-forward controls
- Persistent pairing code with owner-only file permissions
- Native macOS `CGEvent` helper and automated API tests

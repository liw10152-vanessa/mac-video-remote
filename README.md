# Mac Video Remote

用 iPhone 控制 Mac 上正在播放的视频。它会识别当前前台 App，在哔哩哔哩、夸克和其他视频网页之间自动选择控制配置。

## 当前功能

- 播放 / 暂停、前后跳转、全屏、静音和系统音量
- 1×、2× 与倍速增减快捷控制
- 按住手机按钮时持续发送键盘右方向键，松手立即释放，适配播放器的“长按临时倍速”行为
- 自动识别 `com.quark.desktop` 与 `com.bilibili.bilibiliPC`
- iPhone 无需安装 App，Safari 即开即用
- 仅监听本地网络，并要求每次启动随机生成的六位配对码

## 使用方法

要求 macOS 13 或更高版本。Mac 与 iPhone 需要在同一个 Wi‑Fi 网络；无需安装 Python 包。

```bash
chmod +x scripts/run.sh
./scripts/run.sh
```

首次启动会弹出辅助功能授权提示。在“系统设置 → 隐私与安全性 → 辅助功能”中允许 Terminal（或未来打包的 Mac App）控制电脑，然后重启服务。

终端会显示一个类似下面的网址，在 iPhone Safari 中打开即可。配对码首次运行时生成并保存在当前用户的 `Library/Application Support/MacVideoRemote`，以后不会变化，因此可以把页面“添加到主屏幕”：

```text
http://your-mac.local:8765/?code=123456
```

也可以在 Finder 中双击 `启动视频遥控器.command`。保持终端窗口开启；按 Control-C 即可停止。

## 已知边界

- “长按临时快进”依赖播放器支持长按键盘右方向键；哔哩哔哩网页/客户端和多数国内网页播放器采用这种交互。
- 固定倍速由当前播放器的快捷键决定。哔哩哔哩支持 Shift+1/Shift+2；夸克版本变化时，固定倍速可能需要更新配置，但长按快进仍可使用。
- 当前为可直接运行的 Swift Package。安装完整 Xcode 后可将同一控制协议封装成菜单栏 Mac App 和原生 iOS App。

## 隐私与安全

控制服务不连接云端，不上传浏览记录或播放内容。配对码在每次启动时随机变化。不要把带配对码的网址发给同一局域网中的其他人。

## 开发与验证

```bash
./scripts/build.sh
python3 -m unittest discover -s tests -v
```

代码使用公开的 macOS `CGEvent`、Accessibility 和本地 HTTP API。原生辅助程序源码只有一个 Objective-C 文件，可直接审查。

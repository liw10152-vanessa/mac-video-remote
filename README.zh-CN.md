# Mac Video Remote

简体中文 · [English](README.md)

![Mac Video Remote：用 iPhone 控制 Mac 视频播放](assets/social-preview.jpg)

**通过同一 Wi-Fi，用 iPhone 控制 Mac 上的视频播放。** 支持播放暂停、快进快退、倍速、音量、全屏，以及“按住临时快进”；iPhone 无需安装 App。

> 这是公开源代码展示项目，不是开源项目。作者保留版权；未经许可不得复制、修改、分发或商业使用。许可允许个人以非商业目的运行未经修改的软件，详情见 [LICENSE.md](LICENSE.md)。

## 它解决什么问题

当 Mac 离座位有一点距离时，暂停视频或修改倍速都需要站起来。Mac Video Remote 把 iPhone Safari 变成一个专注的视频遥控器，控制 Mac 当前最前面的应用。

## 主要功能

- 播放暂停、前后跳转、全屏、静音和系统音量
- 1×、2×及应用专用倍速控制
- 手指按住时临时快进，松手立即释放
- 自动识别夸克和哔哩哔哩客户端
- 其他视频网页和应用自动使用通用配置
- 无云端、无账号、无统计分析、无第三方运行依赖
- 局域网配对码保护
- 使用公开的 macOS `CGEvent` 与辅助功能 API

## 真实手机界面

<p align="center">
  <img src="assets/iphone-remote.png" width="300" alt="以 iPhone 尺寸渲染的真实遥控界面">
</p>

页面顶部会根据 Mac 当前最前面的应用自动显示应用名称和控制配置。

## 系统要求

- Apple 芯片 Mac，macOS 13 或更高版本
- Mac 和 iPhone 连接同一个可信 Wi-Fi
- Python 3 与 Apple Clang 命令行工具
- 给 Terminal 辅助功能权限

## 启动方法

在 Finder 中双击：

```text
启动视频遥控器.command
```

也可以在终端运行：

```bash
cd "/path/to/mac-video-remote"
./scripts/run.sh
```

第一次启动：

1. 打开“系统设置 → 隐私与安全性 → 辅助功能”。
2. 允许 Terminal 控制 Mac，然后重新启动服务。
3. 保持终端窗口开启。
4. 在 iPhone Safari 打开终端显示的完整网址。
5. 在 Safari 分享菜单中选择“添加到主屏幕”。

配对码只在第一次运行时生成，保存在：

```text
~/Library/Application Support/MacVideoRemote/pairing-code
```

文件权限为 `0600`，只有当前 Mac 用户可以读取。网页配对成功后会自动从地址栏隐藏配对码。

## 使用前的准备

1. 打开夸克、哔哩哔哩或视频网页。
2. 开始播放视频。
3. 点击一下视频画面，让播放器获得键盘焦点。
4. 保持视频应用或浏览器在最前面。
5. 再使用 iPhone 遥控。

遥控指令会发送给 Mac 当前最前面的应用。如果你切换到其他软件，按键也会发送给新的前台应用。

## 按钮说明

| 手机按钮 | Mac 指令 | 说明 |
| --- | --- | --- |
| 播放 / 暂停 | 空格 | 大多数播放器支持 |
| 前后跳转 | 左 / 右方向键 | 秒数由播放器决定 |
| 按住临时快进 | 持续发送右方向键按下事件 | 服务器设有自动释放保险 |
| 1× / 2× | Shift+1 / Shift+2 | 哔哩哔哩已确认，其他应用可能不同 |
| 全屏 / 静音 | F / M | 播放器需要获得键盘焦点 |
| 音量 | Mac 系统音量 | 不依赖播放器快捷键 |

## 隐私与安全

- 不连接云端，不上传浏览记录或播放内容。
- 配对码文件只有当前用户可读。
- 服务端使用恒定时间比较配对码。
- 长按设有自动释放，避免断网时方向键卡住。
- 局域网通信使用普通 HTTP，因此只应在可信 Wi-Fi 中运行。
- 不要公开包含配对码的控制网址。

更完整的安全边界见 [SECURITY.md](SECURITY.md)。

## 当前边界

- 长按临时快进依赖播放器支持长按右方向键。
- 固定倍速由播放器快捷键决定；播放器升级后可能需要更新配置。
- 当前版本通过终端运行，尚未打包成签名的菜单栏 App。
- Mac 睡眠或终端服务停止后，iPhone 无法继续连接。

## 开发与测试

```bash
./scripts/build.sh
PYTHONPYCACHEPREFIX=/tmp/mac-video-remote-pycache \
  python3 -m unittest discover -s Tests -v
```

项目结构见 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)，更新记录见 [CHANGELOG.md](CHANGELOG.md)。

## 版权与许可

Copyright © 2026 `liw10152-vanessa`. All rights reserved.

本项目公开源代码用于查看、评估和个人作品展示。许可允许个人以非商业目的运行未经修改的软件；未经书面许可，不得重新分发、制作衍生作品、再许可或商业使用。完整条款见 [LICENSE.md](LICENSE.md)。

本项目为独立作品，与 Apple、哔哩哔哩或夸克不存在隶属、授权、赞助或背书关系。相关名称仅用于说明兼容性。

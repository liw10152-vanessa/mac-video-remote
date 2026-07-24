# Google AI Studio 与 Mac Video Remote

Google AI Studio 可以发布项目介绍页或本地遥控器启动引导页，但不能托管真正的 Mac 控制后端。

## 为什么云端版本不能直接控制 Mac

真正的遥控流程需要：

1. Mac 本机运行 `app.py`；
2. Objective-C Helper 读取当前前台应用；
3. Terminal 获得 macOS“辅助功能”权限；
4. Helper 使用 `CGEvent` 向本机播放器发送按键；
5. iPhone 通过同一 Wi-Fi 访问 Mac 的 `.local:8765` 地址。

Cloud Run 或 `ai.studio` 页面运行在 Google 云端，无法获得用户 Mac 的辅助功能权限，也无法执行仓库里的 Objective-C Helper。把 `/api/action` 改成云端模拟接口只会让按钮看起来可用，不能控制电脑。

此外，`https://*.ai.studio` 页面直接访问局域网中的 `http://*.local:8765` 可能受到浏览器混合内容和私有网络访问策略限制，不应作为核心控制链路。

## 推荐用途

AI Studio 发布页应作为“安装与启动助手”：

- 解释必须先在 Mac 运行本机服务；
- 提示 Mac 与 iPhone连接同一可信 Wi-Fi；
- 让用户在手机 Safari 输入终端显示的完整本地网址；
- 展示按钮和兼容应用；
- 链接 GitHub 仓库和中文使用说明；
- 明确说明云端页面本身不会读取或保存配对码。

## 不应做的事情

- 不要删除或替换 `app.py`、`native/remote_helper.m` 和启动脚本；
- 不要使用固定配对码；
- 不要声称 Cloud Run API 可以发送 Mac 键盘事件；
- 不要把配对码、局域网地址或浏览记录上传到云端；
- 不要要求用户把本地服务暴露到公网。

实际遥控器始终由 Mac 本机启动：

```text
启动视频遥控器.command
```

然后在 iPhone Safari 打开终端显示的完整网址。

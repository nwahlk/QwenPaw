# 频道配置

CoPaw 支持 11+ 通信频道，通过统一的 Channel 接口管理消息收发。

## 已支持频道

| 频道 | 说明 | 所需配置 |
|------|------|----------|
| **Console** | Web 控制台（默认） | 无需额外配置 |
| **钉钉** | 钉钉群机器人 | AppKey、AppSecret、Token |
| **飞书** | 飞书应用机器人 | AppID、AppSecret |
| **微信** | 微信 iLink Bot | Bot 配置 |
| **企业微信** | 企业微信应用 | CorpID、AgentID、Secret |
| **Discord** | Discord Bot | Bot Token |
| **Telegram** | Telegram Bot | Bot Token |
| **QQ** | QQ 频道机器人 | AppID、Token |
| **iMessage** | Apple iMessage | 仅限 macOS |
| **Matrix** | Matrix 协议 | Homeserver URL、Token |
| **Mattermost** | Mattermost | URL、Token |
| **MQTT** | MQTT 协议 | Broker URL、Topic |
| **Voice** | 语音通话 (Twilio) | Account SID、Token |
| **小艺** | 华为小艺 | 设备授权 |

---

## 频道配置方法

### 通过控制台配置

1. 打开 http://127.0.0.1:8088/
2. 进入 **设置 → 频道**
3. 选择要启用的频道并填写配置信息

### 通过配置文件

在 `~/.copaw/config.json` 中配置频道参数。

### 禁用特定频道

默认 `iessage` 被禁用。通过环境变量禁用更多频道：

```bash
export COPAW_DISABLED_CHANNELS=imessage,matrix,mattermost
```

---

## 频道消息渲染

CoPaw 通过 `Renderer` 模块将 Agent 响应适配到不同频道的消息格式：

- **Markdown → 富文本**（飞书、钉钉）
- **Markdown → HTML**（Telegram、Discord）
- **纯文本回退**（SMS、语音）

## 自定义频道

可以通过继承 `BaseChannel` 类实现自定义频道。自定义频道文件放在工作目录下会自动加载。

详细配置步骤请参考 [官方文档 - 频道配置](https://copaw.agentscope.io/docs/channels)。

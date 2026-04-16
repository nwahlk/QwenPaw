# 项目架构

## 整体架构

CoPaw 采用**模块化分层架构**，核心由 Agent 系统、Channel 系统、Skills 系统、Provider 系统四大模块组成。

```
┌─────────────────────────────────────────────────────┐
│                    频道层 (Channels)                  │
│  Console | 钉钉 | 飞书 | 微信 | Discord | Telegram  │
│  QQ | iMessage | Matrix | Mattermost | MQTT | Voice │
└──────────────────────┬──────────────────────────────┘
                       │ 统一消息队列
┌──────────────────────▼──────────────────────────────┐
│                   Agent 系统层                        │
│  CoPawAgent (ReActAgent) | 多 Agent 管理器            │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │
│  │  Memory   │ │  Skills  │ │  Tool Execution  │    │
│  │  Manager  │ │  Pool    │ │  (工具执行引擎)   │    │
│  └──────────┘ └──────────┘ └──────────────────┘    │
└──────────────────────┬──────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────┐
│                   服务层                              │
│  ┌────────────┐ ┌───────────┐ ┌──────────────────┐  │
│  │  Provider   │ │  Security  │ │  Token Usage     │  │
│  │  Manager    │ │  Guard     │ │  Tracker         │  │
│  └────────────┘ └───────────┘ └──────────────────┘  │
│  ┌────────────┐ ┌───────────┐ ┌──────────────────┐  │
│  │  MCP Client │ │  Cron     │ │  Tunnel          │  │
│  │  Manager    │ │  Scheduler│ │  Services        │  │
│  └────────────┘ └───────────┘ └──────────────────┘  │
└──────────────────────────┬──────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────┐
│                   基础设施层                          │
│  FastAPI + Uvicorn | SQLite | File System            │
│  Docker | supervisord                                │
└─────────────────────────────────────────────────────┘
```

## 核心模块

### 1. Agent 系统 (`src/copaw/agents/`)

CoPawAgent 继承自 AgentScope 的 ReActAgent，是系统的核心智能体。

- **Agent 类**: `CoPawAgent` — 支持 ReAct 推理、工具调用、记忆管理
- **Skills 池**: 双层技能架构（内置 + 自定义），自动发现与加载
- **Memory**: 持久化记忆系统，支持自动压缩与搜索
- **Hooks**: Agent 生命周期钩子（初始化、工具调用前后、响应生成等）
- **Command Handler**: 魔法命令处理器（`/stop`、`/reset` 等）

### 2. Channel 系统 (`src/copaw/app/channels/`)

统一频道接口，通过 `UnifiedQueueManager` 管理消息路由。

- **Base Channel**: 定义频道基础接口与消息渲染
- **Registry**: 频道注册与动态加载
- **Command Registry**: 频道级命令注册

已实现频道：
| 频道 | 模块 | 说明 |
|------|------|------|
| Console | `console/` | Web 控制台 |
| 钉钉 | `dingtalk/` | 钉钉机器人 |
| 飞书 | `feishu/` | 飞书应用 |
| 微信 | `weixin/` | 微信 iLink Bot |
| 企业微信 | `wecom/` | 企业微信 |
| Discord | `discord_/` | Discord Bot |
| Telegram | `telegram/` | Telegram Bot |
| QQ | `qq/` | QQ 频道 |
| iMessage | `imessage/` | Apple iMessage |
| Matrix | `matrix/` | Matrix 协议 |
| Mattermost | `mattermost/` | Mattermost |
| MQTT | `mqtt/` | MQTT 协议 |
| Voice | `voice/` | 语音通话 (Twilio) |
| 小艺 | `xiaoyi/` | 华为小艺 |

### 3. Provider 系统 (`src/copaw/providers/`)

LLM 供应商管理，支持多供应商、速率限制、自动重试。

- **ProviderManager**: 供应商注册、选择、切换
- **RateLimiter**: QPM 滑动窗口流控
- **RetryChatModel**: 指数退避重试

已实现供应商：
| 供应商 | 说明 |
|--------|------|
| OpenAI | OpenAI 及兼容 API |
| Anthropic | Claude 系列 |
| Gemini | Google Gemini |
| DashScope | 阿里通义千问 |
| Ollama | 本地 Ollama |
| llama.cpp | 本地 llama.cpp |
| LM Studio | 本地 LM Studio |

### 4. Web 应用 (`src/copaw/app/`)

基于 FastAPI 的 Web 服务。

- **动态路由**: 多 Agent 运行器，按 workspace 路由
- **API Routers**: RESTful API 接口
- **MCP Client**: MCP 客户端管理
- **Workspace**: 工作空间管理

### 5. 安全系统 (`src/copaw/security/`)

多层安全防护：

- **ToolGuard**: 拦截危险 Shell 命令（`rm -rf /`、fork 炸弹、反向 shell 等）
- **SkillScanner**: 技能安全扫描（提示词注入、命令注入、硬编码密钥检测）
- **FileAccessGuard**: 敏感路径访问限制

## 数据流

```
用户消息 → Channel → UnifiedQueueManager → Agent
                                              │
                                        ┌─────▼─────┐
                                        │ ReAct Loop │
                                        │  思考→行动  │
                                        │  →观察→... │
                                        └─────┬─────┘
                                              │
                              ┌───────────────┼───────────────┐
                              ▼               ▼               ▼
                         Skills          Tools           Memory
                         (技能调用)     (工具执行)      (记忆检索)
                              │               │               │
                              └───────────────┼───────────────┘
                                              ▼
                                         LLM Provider
                                         (模型推理)
                                              │
                                              ▼
                                       回复 → Channel → 用户
```

## 技术选型

| 层级 | 技术 | 选择理由 |
|------|------|----------|
| 后端框架 | FastAPI + Uvicorn | 异步高性能，自动 OpenAPI 文档 |
| Agent 框架 | AgentScope | 成熟的 Agent 抽象，工具调用支持 |
| 前端 | React 18 + TypeScript + Ant Design | 组件丰富，类型安全 |
| 构建工具 | Vite | 快速构建与热更新 |
| 状态管理 | Zustand | 轻量级，适合中等复杂度应用 |
| 定时任务 | APScheduler | 灵活的 cron 调度 |
| 浏览器自动化 | Playwright | 跨浏览器支持 |
| 容器化 | Docker + supervisord | 一键部署，进程管理 |

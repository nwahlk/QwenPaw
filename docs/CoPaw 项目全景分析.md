# CoPaw 项目全景分析

> **版本**: 1.0.1b1 | **许可证**: Apache 2.0 | **开发团队**: AgentScope (Alibaba)
> **仓库**: https://github.com/agentscope-ai/CoPaw

---

## 一、项目概述

CoPaw 是一个**自托管个人 AI 助手框架**，可运行在本地或云端，支持同时连接 14+ 种即时通讯渠道（钉钉、飞书、微信、Discord、Telegram、QQ、iMessage 等），通过**多代理系统**和**技能插件架构**实现可扩展的智能助手能力。

**核心定位**: "Works for you, grows with you." —— 一个为个人用户设计的、可成长的自托管 AI 助手。

---

## 二、目录结构总览

```
QwenPaw/
├── src/copaw/                    # Python 后端核心源码
│   ├── __main__.py               # python -m copaw 入口
│   ├── __version__.py            # 版本号定义
│   ├── constant.py               # 常量与环境变量定义
│   ├── agents/                   # 代理核心模块
│   │   ├── react_agent.py        # CoPawAgent 实现 (ReActAgent + ToolGuardMixin)
│   │   ├── model_factory.py      # 模型工厂
│   │   ├── prompt.py             # 系统提示词构建
│   │   ├── skills_manager.py     # 技能管理器 (~2500行)
│   │   ├── skills_hub.py         # 技能市场客户端 (ClawHub等)
│   │   ├── tool_guard_mixin.py   # 工具安全守卫混入
│   │   ├── command_handler.py    # 命令处理器
│   │   ├── routing_chat_model.py # 模型路由
│   │   ├── schema.py             # 数据模型
│   │   ├── skills/               # 16个内置技能
│   │   ├── tools/                # 14个内置工具
│   │   ├── hooks/                # 代理生命周期钩子
│   │   ├── memory/               # 记忆管理系统
│   │   ├── md_files/             # 多语言提示词模板 (en/zh/ru/ja)
│   │   └── utils/                # 代理工具函数
│   ├── app/                      # FastAPI 应用层
│   │   ├── _app.py               # 应用创建与生命周期管理
│   │   ├── auth.py               # 认证中间件
│   │   ├── multi_agent_manager.py# 多代理管理器
│   │   ├── agent_config_watcher.py # 配置热重载
│   │   ├── migration.py          # 数据迁移 (~815行)
│   │   ├── routers/              # 20+ API 路由模块
│   │   ├── channels/             # 14个渠道集成
│   │   ├── crons/                # 定时任务系统
│   │   ├── runner/               # 请求处理引擎
│   │   ├── workspace/            # 工作空间管理
│   │   ├── mcp/                  # MCP 协议集成
│   │   └── approvals/            # 审批服务
│   ├── cli/                      # CLI 命令行 (click)
│   ├── config/                   # 配置管理系统
│   ├── providers/                # LLM 提供商集成
│   ├── security/                 # 安全子系统
│   ├── local_models/             # 本地模型支持 (llama.cpp)
│   ├── token_usage/              # Token 用量追踪
│   ├── tokenizer/                # 分词器数据
│   ├── tunnel/                   # Cloudflare 隧道
│   ├── envs/                     # 环境变量持久化
│   └── utils/                    # 通用工具
├── console/                      # React 管理控制台前端
│   └── src/
│       ├── api/                  # API 客户端模块
│       ├── pages/                # 页面 (Agent/Chat/Control/Settings/Login)
│       ├── components/           # 通用组件
│       ├── layouts/              # 布局组件
│       └── locales/              # 国际化 (en/zh/ja/ru)
├── website/                      # Vite 公共文档网站
│   └── public/docs/              # 双语文档 (24个页面)
├── tests/                        # 测试
│   ├── unit/                     # 单元测试
│   └── integrated/               # 集成测试
├── deploy/                       # Docker 部署
├── scripts/                      # 构建/安装脚本
└── .github/                      # CI/CD 与社区自动化
```

---

## 三、系统架构设计

### 3.1 整体架构图

```
                    CLI (click)                    Console (React/TypeScript)
                         |                                    |
                         v                                    v
                    FastAPI App
                    /    |    \
          Auth      AgentContext     CORS
          Middleware Middleware     Middleware
                    |
    +---------------+---------------+
    |               |               |
 API Routers   AgentApp Router   Voice Router
 (20+ routes)  (agentscope)     (Twilio)
    |
    v
DynamicMultiAgentRunner
    |
    v
MultiAgentManager (懒加载, 零停机热重载)
    |
    +--> Workspace (agent "default")
    |      |-- AgentRunner --> CoPawAgent (ReActAgent + ToolGuardMixin)
    |      |     |-- Toolkit (内置工具 + 技能 + MCP工具)
    |      |     |-- MemoryManager (ReMeLight 语义记忆)
    |      |     |-- Hooks (Bootstrap, MemoryCompaction)
    |      |-- ChannelManager --> [Console, DingTalk, Feishu, ...]
    |      |-- CronManager (APScheduler)
    |      |-- MCPClientManager (热重载)
    |      |-- AgentConfigWatcher (自动重载)
    |
    +--> Workspace (agent "qa_bot")     # 独立运行时
    +--> Workspace (agent "custom_...")  # 独立运行时

ProviderManager --> [OpenAI, Anthropic, Gemini, Ollama, DashScope, ...]
                     |
                     v
              RetryChatModel --> LLMRateLimiter (QPM + 并发信号量)

LocalModelManager --> LlamaCppBackend (llama.cpp 服务)
```

### 3.2 多代理系统

**MultiAgentManager** (`src/copaw/app/multi_agent_manager.py`):
- 管理多个独立 `Workspace` 实例
- **懒加载**: 工作空间在首次请求时创建
- **零停机热重载**: 创建新实例 → 原子替换 → 优雅停止旧实例
- **并行启动**: 所有启用代理通过 `asyncio.gather` 并发启动
- **线程安全**: 使用 `asyncio.Lock`

**Workspace** (`src/copaw/app/workspace/workspace.py`):
每个工作空间是完整的独立代理运行时，包含：

| 组件 | 优先级 | 可复用 | 说明 |
|------|--------|--------|------|
| AgentRunner | 10 | 否 | 请求处理引擎 |
| MemoryManager | 20 | 是 | ReMeLight 语义记忆 |
| MCPClientManager | 20 | 否 | MCP 工具客户端 |
| ChatManager | 20 | 是 | 会话管理 |
| ChannelManager | 30 | 否 | 通讯渠道 |
| CronManager | 40 | 否 | 定时任务 |
| AgentConfigWatcher | 50 | 否 | 配置热重载 |
| MCPConfigWatcher | 51 | 否 | MCP 配置热重载 |

**ServiceManager** (`src/copaw/app/workspace/service_manager.py`):
声明式服务容器，管理生命周期（启动/停止）、依赖排序、并发初始化和跨重载复用。

### 3.3 代理实现

**CoPawAgent** (`src/copaw/agents/react_agent.py`):
- 继承链: `CoPawAgent -> ToolGuardMixin -> ReActAgent`
- 14 个内置工具 (shell、文件读写、搜索、浏览器等)
- 动态技能加载
- 记忆管理 + 自动压缩钩子
- Bootstrap 引导 (首次交互)
- MCP 客户端注册与恢复
- 非多模态模型的媒体块过滤

### 3.4 前端架构

**管理控制台** (`console/`):
- **技术栈**: React 18 + TypeScript + Vite 6 + Ant Design 5
- **状态管理**: Zustand 5
- **路由**: React Router v7
- **国际化**: i18next (en/zh/ja/ru)
- **UI 组件库**: @agentscope-ai/chat + @agentscope-ai/design

**公共网站** (`website/`):
- **技术栈**: React 18 + TypeScript + Vite 6 + TailwindCSS 4
- **包管理**: pnpm
- **功能**: 产品介绍、文档站点 (24个双语文档页)

---

## 四、核心功能模块

### 4.1 API 接口层

基于 **FastAPI**，20+ 路由模块，统一挂载在 `/api` 前缀下：

| 路由模块 | 文件 | 核心端点 |
|---------|------|---------|
| `agents` | `agents.py` | 多代理 CRUD、启用/禁用 |
| `agent` | `agent.py` | 单代理文件管理、记忆、语言、系统提示词 |
| `config` | `config.py` | 渠道配置、心跳、模型路由、时区、安全设置 |
| `console` | `console.py` | SSE 流式聊天、停止、上传、推送消息 |
| `cron` | `crons/api.py` | 定时任务管理 |
| `local_models` | `local_models.py` | 本地模型管理 |
| `mcp` | `mcp.py` | MCP 服务端管理 |
| `providers` | `providers.py` | LLM 提供商/模型 CRUD、测试、发现、活跃模型 |
| `skills` | `skills.py` | 技能 CRUD、市场搜索/安装、技能池 (30+ 端点) |
| `tools` | `tools.py` | 内置工具启用/禁用 |
| `workspace` | `workspace.py` | 工作空间上传/下载 |
| `envs` | `envs.py` | 环境变量管理 |
| `token_usage` | `token_usage.py` | Token 用量追踪 |
| `auth` | `auth.py` | 登录、注册、状态、验证 |
| `files` | `files.py` | 文件上传/下载 |
| `voice` | `voice.py` | Twilio 语音端点 (webhook/WebSocket) |
| `settings` | `settings.py` | 通用设置 |

**Agent 作用域路由**: 所有子路由同时挂载在 `/api/agents/{agentId}/` 下，通过 `AgentContextMiddleware` 从 URL 或 `X-Agent-Id` 请求头提取代理 ID。

**关键接口示例**:
- `POST /console/chat` — SSE 流式聊天（支持断线重连）
- `GET /skills/hub/search` — 搜索技能市场
- `POST /skills/hub/install` — 从市场安装技能（异步）
- `POST /providers/{id}/models/discover` — 自动发现模型
- `POST /auth/login` — 登录认证

### 4.2 技能系统

**三层技能架构**:

```
┌─────────────────────────────────────────┐
│  内置技能 (Builtin)                      │  随应用分发，不可变
│  src/copaw/agents/skills/               │
├─────────────────────────────────────────┤
│  技能池 (Skill Pool)                     │  本地共享仓库
│  ~/.copaw/skill_pool/                   │
├─────────────────────────────────────────┤
│  工作空间技能 (Workspace)                 │  代理级覆盖
│  ~/.copaw/workspaces/<id>/skills/       │
└─────────────────────────────────────────┘
```

**技能定义**: 每个技能是一个目录，至少包含 `SKILL.md` (YAML frontmatter + Markdown 内容):

```yaml
---
name: skill-name
description: 技能描述
tags: [tag1, tag2]
triggers: [触发短语]
---
# 技能内容 (Markdown)
...
```

**16 个内置技能**:

| 技能 | 说明 |
|------|------|
| `browser_cdp` | Chrome DevTools Protocol 自动化 |
| `browser_visible` | 可视化浏览器自动化 (Playwright) |
| `channel_message` | 跨渠道消息发送 |
| `copaw_source_index` | 源代码索引 |
| `cron` | 定时任务管理 |
| `dingtalk_channel` | 钉钉专属功能 |
| `docx` | Word 文档处理 |
| `file_reader` | 文件读取 |
| `guidance` | 用户引导 |
| `himalaya` | 邮件管理 |
| `multi_agent_collaboration` | 多代理协作 |
| `news` | 新闻摘要 |
| `pdf` | PDF 处理 (表单、填充) |
| `pptx` | PowerPoint 处理 |
| `xlsx` | Excel 电子表格处理 |

**技能市场 (ClawHub)**: 支持从 ClawHub、GitHub、LobeHub、ModelScope、skills.sh、skillsmp.com 搜索和安装技能。

### 4.3 模型管理

**提供商抽象** (`src/copaw/providers/`):

| 提供商 | 类型 |
|--------|------|
| OpenAI | 远程 API |
| Anthropic | 远程 API |
| Gemini | 远程 API |
| Ollama | 本地/远程 |
| DashScope (阿里云) | 远程 API |
| ModelScope (魔搭) | 远程 API |
| 自定义提供商 | 用户配置 |

**核心机制**:
- **RateLimiter**: QPM 滑动窗口 (60s) + asyncio.Semaphore 并发控制 + 全局 429 暂停
- **RetryChatModel**: 透明重试包装器，处理 429/5xx 错误，指数退避
- **LocalModelManager**: llama.cpp 后端，支持 HuggingFace/ModelScope 模型下载
- **MultimodalProber**: 自动探测模型多模态能力

### 4.4 聊天渠道

**14 个内置渠道**:

| 渠道 | SDK/协议 | 说明 |
|------|----------|------|
| `console` | Web | 管理控制台 (必装) |
| `dingtalk` | dingtalk-stream | 钉钉机器人 |
| `feishu` | lark-oapi | 飞书/Lark 机器人 |
| `discord` | discord-py | Discord Bot |
| `telegram` | python-telegram-bot | Telegram Bot |
| `qq` | QQ SDK | QQ 机器人 |
| `imessage` | AppleScript | iMessage (仅 macOS) |
| `wecom` | wecom-aibot-python-sdk | 企业微信 |
| `weixin` | Custom | 微信 (iLink Bot) |
| `matrix` | matrix-nio | Matrix 协议 |
| `mattermost` | API | Mattermost |
| `mqtt` | paho-mqtt | MQTT 协议 |
| `voice` | twilio | Twilio 语音通话 |
| `xiaoyi` | Custom | 小艺 (华为 A2A 协议) |

**消息处理管线**:

```
渠道接收消息 → 优先级队列入队 → 批量合并 → 命令分发
    → 工具守卫审批检查 → Agent 执行 → 消息渲染 → 渠道发送 → 会话持久化
```

**优先级路由**:
- `critical` (0): `/stop` 命令
- `high` (10): `/status`, `/restart` 等控制命令
- `normal` (20): 普通对话
- `low` (30): 批量操作

### 4.5 记忆系统

| 组件 | 文件 | 说明 |
|------|------|------|
| BaseMemoryManager | `memory/base_memory_manager.py` | 抽象基类 |
| ReMeLightMemoryManager | `memory/reme_light_memory_manager.py` | ReMe-Light 语义记忆实现 |
| AgentMdManager | `memory/agent_md_manager.py` | 代理人格 Markdown 文件管理 |
| BootstrapHook | `hooks/bootstrap.py` | 首次交互引导 |
| MemoryCompactionHook | `hooks/memory_compaction.py` | 上下文自动压缩 |

**人格文件** (多语言: en/zh/ru/ja):
- `AGENTS.md` — 代理能力描述
- `SOUL.md` — 人格/性格定义
- `PROFILE.md` — 用户画像
- `BOOTSTRAP.md` — 首次引导
- `HEARTBEAT.md` — 心跳查询
- `MEMORY.md` — 记忆指令

### 4.6 安全系统

**双层安全架构**:

```
┌─────────────────────────────────────────┐
│  Tool Guard (工具守卫)                    │  工具调用前参数扫描
│  ├── Engine (规则引擎)                    │
│  ├── FileGuardian (文件守卫)              │
│  ├── RuleGuardian (规则守卫)              │
│  └── Approval (审批流)                    │
├─────────────────────────────────────────┤
│  Skill Scanner (技能扫描器)               │  安装前静态分析
│  ├── PatternAnalyzer (模式分析)            │
│  └── 8类签名规则                          │
└─────────────────────────────────────────┘
```

**Tool Guard 规则** (YAML): 覆盖 rm/mv、fork bomb、反向 shell、权限提升、系统重启、进程终止、base64 混淆执行等。

**Skill Scanner 签名规则**: 命令注入、数据泄露、硬编码密钥、混淆、提示注入、社工攻击、供应链风险、未授权工具使用。

### 4.7 定时任务

- **引擎**: APScheduler (AsyncIOScheduler)
- **触发器**: Cron 表达式 + 间隔触发
- **心跳**: 基于 `HEARTBEAT.md` 的定期自查询
- **持久化**: `jobs.json` (每个代理独立)
- **并发控制**: 每任务信号量 + 活跃时段支持

### 4.8 MCP 集成

- **传输协议**: stdio, streamable_http, sse
- **热重载**: 配置变更时自动重连
- **默认配置**: Tavily Search (检测 `TAVILY_API_KEY` 自动启用)

---

## 五、中间件与拦截器

| 中间件 | 文件 | 说明 |
|--------|------|------|
| AgentContextMiddleware | `routers/agent_scoped.py` | 从 URL/Header 提取 agentId |
| AuthMiddleware | `app/auth.py` | JWT 认证 (HMAC-SHA256, 7天有效期) |
| CORSMiddleware | `_app.py` | 跨域控制 |
| ToolGuardMixin | `agents/tool_guard_mixin.py` | 工具调用前安全扫描 |
| SkillScanner | `security/skill_scanner/` | 技能安装前静态分析 |

---

## 六、配置管理

### 6.1 配置文件体系

| 文件 | 位置 | 说明 |
|------|------|------|
| `config.json` | `~/.copaw/config.json` | 全局配置 |
| `agent.json` | `~/.copaw/workspaces/<id>/agent.json` | 代理配置 |
| `envs.json` | `~/.copaw.secret/envs.json` | 持久化环境变量 (权限 0o600) |
| `auth.json` | `~/.copaw.secret/auth.json` | 认证数据 |
| `jobs.json` | 每个代理工作空间 | 定时任务定义 |
| `skill.json` | 每个工作空间/技能池 | 技能清单 |

### 6.2 关键环境变量

| 变量 | 默认值 | 说明 |
|------|--------|------|
| `COPAW_WORKING_DIR` | `~/.copaw` | 工作目录根 |
| `COPAW_SECRET_DIR` | `${WORKING_DIR}.secret` | 密钥目录 |
| `COPAW_PORT` | `8088` | 监听端口 |
| `COPAW_LOG_LEVEL` | `info` | 日志级别 |
| `COPAW_AUTH_ENABLED` | `false` | 启用 Web 认证 |
| `COPAW_LLM_MAX_RETRIES` | `3` | LLM 重试次数 |
| `COPAW_LLM_MAX_QPM` | `600` | 每分钟查询上限 |
| `COPAW_LLM_MAX_CONCURRENT` | `10` | 最大并发 LLM 调用 |
| `COPAW_DISABLED_CHANNELS` | (空) | 渠道黑名单 |
| `COPAW_ENABLED_CHANNELS` | (空) | 渠道白名单 |

### 6.3 配置热重载

`AgentConfigWatcher` 每 2 秒轮询 `agent.json` 的 mtime，变更时自动重载渠道、心跳等配置，无需重启。

---

## 七、部署运维

### 7.1 Docker 部署

```yaml
# docker-compose.yml
services:
  copaw:
    image: agentscope/copaw:latest
    restart: always
    ports:
      - "127.0.0.1:8088:8088"
    volumes:
      - copaw-data:/app/working
      - copaw-secrets:/app/working.secret
```

**Dockerfile 特性**:
- 多阶段构建 (Console 前端 + Python 运行时)
- 内置 Chromium + XFCE4 桌面环境 + Xvfb (用于浏览器自动化)
- Supervisord 管理 4 个进程 (Xvfb → XFCE4 → D-Bus → CoPaw App)
- 支持多架构: linux/amd64, linux/arm64

### 7.2 安装方式

| 方式 | 说明 |
|------|------|
| PyPI | `pip install copaw` |
| Docker | `docker pull agentscope/copaw` |
| 桌面 | Windows (NSIS) / macOS (.app) 安装包 |
| 脚本 | 一键安装脚本 (curl/bash, PowerShell) |

### 7.3 CI/CD 流水线

| 工作流 | 触发 | 说明 |
|--------|------|------|
| `tests.yml` | Push/PR | 单元测试 + 集成测试 + 覆盖率 (Python 3.10/3.13, Ubuntu/macOS/Windows) |
| `docker-release.yml` | Release | 多架构 Docker 镜像构建推送 |
| `publish-pypi.yml` | Release | Python Wheel 构建发布 |
| `desktop-release.yml` | Release | 桌面安装包构建 |
| `deploy-website.yml` | Release | 文档网站部署到 GitHub Pages |
| `pre-commit.yml` | Push | 代码质量检查 (black, flake8, mypy) |

### 7.4 数据持久化

无传统数据库，全部基于文件存储:
- 配置: JSON 文件
- 会话: JSON 文件
- 记忆: ReMe-Light 语义索引
- 日志: 文件日志 (`copaw.log`)，macOS 支持轮转 (5MB × 3)

---

## 八、技术栈总结

### 后端

| 类别 | 技术 |
|------|------|
| 语言 | Python 3.10-3.13 |
| Web 框架 | FastAPI + Uvicorn |
| Agent 框架 | AgentScope 1.0.18 + agentscope-runtime 1.1.3 |
| 定时任务 | APScheduler |
| 浏览器自动化 | Playwright |
| 语义记忆 | ReMe-Light (reme-ai) |
| 序列化 | Pydantic |
| CLI | Click |

### 前端 (管理控制台)

| 类别 | 技术 |
|------|------|
| 框架 | React 18 + TypeScript |
| 构建 | Vite 6 |
| UI 组件 | Ant Design 5 |
| 状态管理 | Zustand 5 |
| 路由 | React Router v7 |
| 国际化 | i18next |

### 代码质量

| 工具 | 说明 |
|------|------|
| black | 代码格式化 (line-length=79) |
| flake8 | Linting |
| mypy | 类型检查 |
| pylint | 静态分析 |
| pre-commit | Git Hook 管理 |
| prettier | 前端代码格式化 |
| pytest | 单元/集成测试 |

---

## 九、关键设计模式

1. **多代理隔离**: 每个 Agent 运行在独立 Workspace 中，拥有完整的运行时组件栈
2. **插件化架构**: 渠道和技能均遵循注册-发现-加载的插件模式，支持热重载
3. **优先级队列**: 消息通过四级优先级路由，确保关键命令可抢占普通对话
4. **流式优先**: 所有 Agent 响应使用 SSE 流式传输，支持 TaskTracker 取消
5. **零停机热重载**: 配置变更时原子替换实例，不影响正在处理的请求
6. **安全纵深防御**: Tool Guard (运行时) + Skill Scanner (安装时) 双层安全
7. **声明式服务管理**: ServiceManager 通过优先级和依赖关系管理组件生命周期

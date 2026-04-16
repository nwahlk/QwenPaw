# 配置参考

## 环境变量

### 核心配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `COPAW_WORKING_DIR` | `~/.copaw` | 工作目录（配置、记忆、Skills） |
| `COPAW_SECRET_DIR` | `~/.copaw.secret` | 密钥目录（API Key、模型配置） |
| `COPAW_PORT` | `8088` | Web 服务端口 |
| `COPAW_LOG_LEVEL` | `info` | 日志级别 (debug/info/warning/error) |
| `COPAW_DISABLED_CHANNELS` | `imessage` | 禁用的频道列表（逗号分隔） |

### 认证配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `COPAW_AUTH_ENABLED` | `false` | 是否启用 Web 登录认证 |
| `COPAW_AUTH_USERNAME` | — | Web 登录用户名 |
| `COPAW_AUTH_PASSWORD` | — | Web 登录密码 |

### LLM 流控

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `COPAW_LLM_MAX_CONCURRENT` | `10` | 最大并发 LLM 调用数 |
| `COPAW_LLM_MAX_QPM` | `600` | 每分钟最大查询数 |

### 网络配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `COPAW_CORS_ORIGINS` | `*` | CORS 允许的来源 |

### 模型 API Key

| 变量名 | 说明 |
|--------|------|
| `DASHSCOPE_API_KEY` | 阿里通义千问 API Key |
| `OPENAI_API_KEY` | OpenAI API Key |
| `ANTHROPIC_API_KEY` | Anthropic (Claude) API Key |
| `GOOGLE_API_KEY` | Google Gemini API Key |
| `TAVILY_API_KEY` | Tavily 网页搜索 API Key |

### 其他

| 变量名 | 说明 |
|--------|------|
| `PLAYWRIGHT_CHROMIUM_EXECUTABLE_PATH` | Playwright Chromium 可执行文件路径 |

---

## 配置文件

配置文件位于工作目录（默认 `~/.copaw`）下：

| 文件 | 说明 |
|------|------|
| `config.json` | 主配置文件（模型、Agent、Skills 等） |
| `jobs.json` | 定时任务（Cron Jobs） |
| `chats.json` | 聊天历史记录 |
| `HEARTBEAT.md` | 心跳摘要模板 |
| `token_usage.json` | Token 使用统计 |
| `.env` | 环境变量（密钥等敏感信息） |

---

## 模型配置

在控制台 **设置 → 模型** 中配置，或通过 `copaw init` 交互式配置。

支持的供应商：
- **OpenAI** — GPT-4o、GPT-4o-mini 等
- **Anthropic** — Claude 4.5 Sonnet、Claude 3.5 Haiku 等
- **Google Gemini** — Gemini 2.5 Pro、Gemini 2.5 Flash 等
- **DashScope** — 通义千问系列
- **Ollama** — 本地部署模型
- **llama.cpp** — 本地部署模型
- **LM Studio** — 本地部署模型
- **自定义** — OpenAI 兼容 API

---

## 本地模型配置

### llama.cpp

无需额外安装，在 Web 界面中点击 `Download Llama.cpp` 即可自动配置。

### Ollama

1. 安装 Ollama: https://ollama.ai
2. 下载模型: `ollama pull qwen2.5:7b`
3. 在 CoPaw 设置 → 模型中选择 Ollama，填入 Base URL: `http://localhost:11434`

### LM Studio

1. 安装 LM Studio: https://lmstudio.ai
2. 下载并启动模型
3. 在 CoPaw 设置 → 模型中选择 LM Studio，填入 Base URL: `http://localhost:1234/v1`

> 使用 Docker 时，Base URL 需改为 `http://host.docker.internal:<端口>`。

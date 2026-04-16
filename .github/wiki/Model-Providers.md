# 模型供应商

CoPaw 支持多种 LLM 供应商，包括云端 API 和本地部署。

## 云端供应商

### OpenAI

| 模型 | 说明 |
|------|------|
| GPT-4o | 多模态旗舰模型 |
| GPT-4o-mini | 轻量多模态模型 |
| o1 / o3 | 推理模型 |

配置：API Key + Base URL（可选，用于兼容 API）

### Anthropic (Claude)

| 模型 | 说明 |
|------|------|
| Claude Opus 4.6 | 最强模型 |
| Claude Sonnet 4.6 | 平衡性能与速度 |
| Claude Haiku 4.5 | 最快速度 |

配置：API Key

### Google Gemini

| 模型 | 说明 |
|------|------|
| Gemini 2.5 Pro | 旗舰模型 |
| Gemini 2.5 Flash | 快速模型 |

配置：API Key

### DashScope (通义千问)

| 模型 | 说明 |
|------|------|
| qwen-max | 旗舰模型 |
| qwen-plus | 增强模型 |
| qwen-turbo | 快速模型 |

配置：API Key（环境变量 `DASHSCOPE_API_KEY`）

---

## 本地供应商

### Ollama

支持所有 Ollama 模型（如 qwen2.5、llama3、mistral 等）。

配置：
- Base URL: `http://localhost:11434`
- 无需 API Key

```bash
# 安装 Ollama
pip install copaw[ollama]

# 拉取模型
ollama pull qwen2.5:7b
```

### llama.cpp

跨平台本地推理引擎。

配置：
- 无需额外安装，在 Web 界面中点击 `Download Llama.cpp` 即可
- 无需 API Key

### LM Studio

带 GUI 的本地模型服务。

配置：
- Base URL: `http://localhost:1234/v1`
- 无需 API Key

---

## 自定义供应商

CoPaw 支持 OpenAI 兼容 API，可连接任何兼容的模型服务：

1. 打开 **设置 → 模型**
2. 选择 "自定义" 供应商
3. 填入 Base URL 和 API Key
4. 配置可用模型列表

---

## 速率限制与重试

CoPaw 内置 LLM 流控机制：

- **QPM 限制**: 默认每分钟最多 600 次查询（可通过 `COPAW_LLM_MAX_QPM` 调整）
- **并发限制**: 默认最多 10 个并发调用（可通过 `COPAW_LLM_MAX_CONCURRENT` 调整）
- **自动重试**: 指数退避重试，处理速率限制和临时错误

---

## 大小模型协同

CoPaw 支持多模型路由，不同任务可使用不同模型（路线图中，进行中）。

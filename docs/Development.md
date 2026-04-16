# 开发指南

## 从源码构建

### 前置要求

- Python 3.10 ~ 3.13
- Node.js 18+
- Git

### 步骤

```bash
# 1. 克隆仓库
git clone https://github.com/agentscope-ai/CoPaw.git
cd CoPaw

# 2. 构建前端控制台
cd console
npm ci
npm run build
cd ..

# 3. 复制构建产物
mkdir -p src/copaw/console
cp -R console/dist/. src/copaw/console/

# 4. 安装 Python 包（开发模式）
pip install -e ".[dev,full]"

# 5. 初始化并运行
copaw init --defaults
copaw app
```

### 安装 Pre-commit 钩子

```bash
pre-commit install
pre-commit run --all-files
```

---

## 运行测试

```bash
# 运行所有测试
pytest

# 运行单元测试
pytest tests/unit/

# 运行集成测试
pytest tests/integrated/

# 排除慢速测试
pytest -m "not slow"

# 查看覆盖率
pytest --cov=copaw
```

---

## 项目依赖

### 核心依赖

| 包 | 版本 | 用途 |
|----|------|------|
| agentscope | 1.0.18 | Agent 框架 |
| agentscope-runtime | 1.1.3 | 运行时 |
| fastapi | — | Web 框架（通过 uvicorn） |
| uvicorn | >=0.40.0 | ASGI 服务器 |
| apscheduler | >=3.11.2 | 定时任务 |
| playwright | >=1.49.0 | 浏览器自动化 |

### 频道 SDK

| 包 | 用途 |
|----|------|
| discord-py | Discord 频道 |
| dingtalk-stream | 钉钉频道 |
| lark-oapi | 飞书频道 |
| python-telegram-bot | Telegram 频道 |
| twilio | 语音通话 |
| matrix-nio | Matrix 频道 |
| paho-mqtt | MQTT 频道 |
| wecom-aibot-python-sdk | 企业微信 |

### 可选依赖

| 组 | 安装方式 | 用途 |
|----|----------|------|
| dev | `pip install copaw[dev]` | 测试、pre-commit |
| local | `pip install copaw[local]` | HuggingFace 模型下载 |
| llamacpp | `pip install copaw[llamacpp]` | llama.cpp 支持 |
| ollama | `pip install copaw[ollama]` | Ollama 支持 |
| mlx | `pip install copaw[mlx]` | Apple MLX 支持 |
| whisper | `pip install copaw[whisper]` | OpenAI Whisper 语音 |
| full | `pip install copaw[full]` | 全部可选依赖 |

---

## 代码规范

- **代码风格**: Black
- **类型注解**: 必须添加
- **Pre-commit**: 提交前自动检查
- **测试**: 新功能必须有测试

---

## 贡献流程

1. Fork 仓库
2. 创建特性分支 (`git checkout -b feature/xxx`)
3. 提交更改 (`git commit -m 'feat(scope): message'`)
4. 推送到分支 (`git push origin feature/xxx`)
5. 创建 Pull Request

### 提交格式

```
<type>(<scope>): <description>
```

类型：`feat`、`fix`、`docs`、`style`、`refactor`、`test`、`chore`

### 欢迎贡献的方向

- 新频道适配
- 新模型供应商
- 新 Skills
- 新 MCP 客户端
- UI/UX 优化
- Windows 路径兼容性改进
- 文档改进

详细贡献指南请参考 [CONTRIBUTING.md](https://github.com/agentscope-ai/CoPaw/blob/main/CONTRIBUTING_zh.md)。

---

## 版本更新

当 `git pull` 更新到大版本后：

1. 重新构建前端：`cd console && npm ci && npm run build && cd ..`
2. 重新安装：`pip install -e .`
3. 重启：`copaw app`
4. 清除浏览器缓存：`Ctrl+Shift+R`

---

## 构建 Docker 镜像

```bash
# 参见 scripts/README.md
docker build -t agentscope/copaw:latest -f deploy/Dockerfile .
```

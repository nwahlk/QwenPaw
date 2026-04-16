# 项目结构

```
QwenPaw/
├── .github/
│   ├── ISSUE_TEMPLATE/          # Issue 模板
│   ├── PULL_REQUEST_TEMPLATE.md # PR 模板
│   ├── workflows/               # GitHub Actions CI/CD
│   └── wiki/                    # Wiki 文档源文件
│
├── console/                     # Web 控制台（React 前端）
│   ├── public/                  # 静态资源
│   ├── src/
│   │   ├── api/                 # API 客户端模块
│   │   ├── components/          # React 组件
│   │   ├── pages/               # 页面组件
│   │   │   ├── Agent/           # Agent 管理页
│   │   │   ├── Chat/            # 聊天页
│   │   │   ├── Control/         # 控制面板
│   │   │   ├── Settings/        # 设置页
│   │   │   └── Login/           # 登录页
│   │   ├── stores/              # Zustand 状态管理
│   │   └── styles/              # CSS/Less 样式
│   ├── package.json
│   └── vite.config.ts
│
├── deploy/                      # 部署配置
│   ├── Dockerfile               # Docker 镜像构建
│   ├── entrypoint.sh            # 容器入口脚本
│   └── config/                  # 部署配置文件
│
├── scripts/                     # 构建 & 打包脚本
│   └── pack/                    # 桌面应用打包
│
├── src/copaw/                   # Python 主代码
│   ├── __init__.py
│   ├── __version__.py           # 版本号
│   │
│   ├── agents/                  # Agent 核心
│   │   ├── agent.py             # CoPawAgent 主类
│   │   ├── skills/              # 内置技能（17+ 个）
│   │   │   ├── browser_cdp/     # Chrome DevTools 自动化
│   │   │   ├── browser_visible/ # 可见浏览器自动化
│   │   │   ├── channel_message/ # 跨频道消息
│   │   │   ├── cron/            # 定时任务
│   │   │   ├── docx/            # Word 文档处理
│   │   │   ├── pdf/             # PDF 处理
│   │   │   ├── pptx/            # PPT 处理
│   │   │   ├── xlsx/            # Excel 处理
│   │   │   ├── file_reader/     # 文件读取
│   │   │   ├── news/            # 新闻摘要
│   │   │   ├── himalaya/        # 邮件/日历
│   │   │   ├── guidance/        # 用户引导
│   │   │   ├── multi_agent_collaboration/  # 多 Agent 协作
│   │   │   ├── copaw_source_index/          # 源码索引
│   │   │   └── ...              # 更多技能
│   │   ├── memory/              # 记忆管理器
│   │   │   ├── memory_manager.py
│   │   │   └── compactor.py     # 记忆压缩
│   │   ├── hooks/               # Agent 生命周期钩子
│   │   └── md_files/            # 引导文档
│   │
│   ├── app/                     # FastAPI Web 应用
│   │   ├── app.py               # 应用入口
│   │   ├── channels/            # 频道适配器（11+）
│   │   │   ├── base.py          # 频道基类
│   │   │   ├── console/         # 控制台频道
│   │   │   ├── dingtalk/        # 钉钉
│   │   │   ├── feishu/          # 飞书
│   │   │   ├── weixin/          # 微信
│   │   │   ├── wecom/           # 企业微信
│   │   │   ├── discord_/        # Discord
│   │   │   ├── telegram/        # Telegram
│   │   │   ├── qq/              # QQ
│   │   │   ├── imessage/        # iMessage
│   │   │   ├── matrix/          # Matrix
│   │   │   ├── mattermost/      # Mattermost
│   │   │   ├── mqtt/            # MQTT
│   │   │   ├── voice/           # 语音 (Twilio)
│   │   │   ├── xiaoyi/          # 华为小艺
│   │   │   ├── manager.py       # 频道管理器
│   │   │   ├── registry.py      # 频道注册
│   │   │   └── unified_queue_manager.py  # 统一消息队列
│   │   ├── routers/             # API 路由
│   │   │   ├── agent.py         # 单 Agent 接口
│   │   │   ├── agents.py        # 多 Agent 管理
│   │   │   ├── config.py        # 配置接口
│   │   │   ├── console.py       # 控制台接口
│   │   │   ├── providers.py     # 模型供应商接口
│   │   │   ├── skills.py        # 技能接口
│   │   │   ├── mcp.py           # MCP 接口
│   │   │   ├── files.py         # 文件上传/下载
│   │   │   ├── auth.py          # 认证
│   │   │   ├── envs.py          # 环境变量
│   │   │   ├── messages.py      # 消息接口
│   │   │   ├── tools.py         # 工具接口
│   │   │   ├── voice.py         # 语音接口
│   │   │   ├── token_usage.py   # Token 使用统计
│   │   │   ├── local_models.py  # 本地模型
│   │   │   └── workspace.py     # 工作空间
│   │   ├── workspace/           # 工作空间管理
│   │   └── mcp/                 # MCP 客户端管理
│   │
│   ├── cli/                     # CLI 命令行
│   │   └── main.py              # CLI 入口
│   │
│   ├── config/                  # 配置管理
│   ├── envs/                    # 环境变量处理
│   ├── local_models/            # 本地模型供应商
│   ├── providers/               # LLM 供应商实现
│   │   ├── provider_manager.py  # 供应商管理
│   │   ├── rate_limiter.py      # 速率限制
│   │   ├── openai_provider.py   # OpenAI
│   │   ├── anthropic_provider.py # Anthropic (Claude)
│   │   ├── gemini_provider.py   # Google Gemini
│   │   ├── ollama_provider.py   # Ollama
│   │   └── retry_chat_model.py  # 重试机制
│   │
│   ├── security/                # 安全模块
│   │   ├── tool_guard/          # 工具防护
│   │   │   └── rules/           # 危险命令规则
│   │   └── skill_scanner/       # 技能安全扫描
│   │       ├── rules/           # 扫描规则
│   │       └── data/            # 扫描数据
│   │
│   ├── token_usage/             # Token 使用追踪
│   ├── tokenizer/               # 分词器工具
│   ├── tunnel/                  # 隧道服务
│   └── utils/                   # 通用工具函数
│
├── tests/                       # 测试
│   ├── unit/                    # 单元测试
│   └── integrated/              # 集成测试
│
├── website/                     # 文档网站
│   └── public/docs/             # 文档内容
│
├── pyproject.toml               # Python 项目配置
├── setup.py                     # 安装脚本
├── docker-compose.yml           # Docker Compose
├── .pre-commit-config.yaml      # Pre-commit 钩子
├── README.md                    # 英文 README
├── README_zh.md                 # 中文 README
├── README_ja.md                 # 日文 README
├── README_ru.md                 # 俄文 README
├── CONTRIBUTING.md              # 贡献指南
└── SECURITY.md                  # 安全策略
```

## 代码统计

- **Python 代码**: ~28,500 行
- **内置技能**: 17+
- **通信频道**: 11+
- **API 路由**: 20+
- **支持语言**: 英文、中文、日文、俄文

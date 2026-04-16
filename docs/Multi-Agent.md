# 多智能体系统

CoPaw 支持创建多个独立智能体（Agent），各司其职，通过协作技能互相通信共同完成复杂任务。

## 核心概念

### Agent

每个 Agent 是一个独立的 CoPawAgent 实例，拥有：
- 独立的配置（模型、Skills、记忆）
- 独立的聊天历史
- 独立的身份和角色设定

### 工作空间 (Workspace)

多个 Agent 运行在同一个工作空间中，通过统一消息队列协调。

---

## Agent 管理

### 通过 CLI

```bash
# 查看所有 Agent
copaw agents

# 创建新 Agent
copaw agents --create

# 删除 Agent
copaw agents --delete <agent_id>
```

### 通过 API

```bash
# 创建 Agent
curl -X POST http://127.0.0.1:8088/api/agents/create \
  -H "Content-Type: application/json" \
  -d '{"name": "研究员", "description": "负责信息检索"}'

# 列出 Agent
curl http://127.0.0.1:8088/api/agents

# 启用/禁用
curl -X POST http://127.0.0.1:8088/api/agents/{agent_id}/enable
curl -X POST http://127.0.0.1:8088/api/agents/{agent_id}/disable
```

### 通过控制台

打开 http://127.0.0.1:8088/ → **Agent 管理** 页面。

---

## Agent 协作

### 启用协作技能

1. 为需要协作的 Agent 启用 `multi_agent_collaboration` 技能
2. Agent 间通过消息传递机制互相通信
3. 支持任务分发与结果汇总

### 后台任务

支持通过 CLI `--background` 标志执行后台任务：

```bash
copaw agents --run --background "搜索最新的 AI 论文并生成摘要"
```

### 优先级队列

所有 Agent 共享统一优先级队列系统：

- 高优先级任务优先执行
- 支持 `/stop` 命令取消正在执行的任务

---

## 使用场景

| 场景 | Agent 配置 |
|------|-----------|
| **内容创作** | 研究员 Agent（搜集资料）+ 写手 Agent（生成内容） |
| **代码开发** | 架构师 Agent（设计方案）+ 开发者 Agent（编写代码）+ 审查员 Agent（代码审查） |
| **信息监控** | 监控 Agent（定时检索）+ 分析 Agent（数据分析）+ 通知 Agent（推送摘要） |

---

## 配置示例

```json
{
  "agents": [
    {
      "name": "研究员",
      "description": "负责信息检索和资料搜集",
      "model": "qwen-max",
      "skills": ["news", "file_reader", "browser_cdp"],
      "enabled": true
    },
    {
      "name": "写手",
      "description": "负责内容创作和编辑",
      "model": "qwen-plus",
      "skills": ["docx", "pptx", "multi_agent_collaboration"],
      "enabled": true
    }
  ]
}
```

详细文档请参考 [官方文档 - 多智能体](https://copaw.agentscope.io/docs/multi-agent)。

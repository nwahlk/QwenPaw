# Skills 系统

CoPaw 的能力通过 **Skills** 扩展。每个 Skill 是一个独立模块，包含提示词、工具定义和元数据。

## 内置技能

### 文档处理

| 技能 | 说明 |
|------|------|
| **pdf** | PDF 读取、摘要、表单填写 |
| **docx** | Word 文档读取与创建 |
| **pptx** | PPT 读取、编辑与创建 |
| **xlsx** | Excel 读取与操作 |

### 浏览器自动化

| 技能 | 说明 |
|------|------|
| **browser_cdp** | 通过 Chrome DevTools Protocol 控制浏览器 |
| **browser_visible** | 可见浏览器自动化（Playwright） |

### 通信与协作

| 技能 | 说明 |
|------|------|
| **channel_message** | 跨频道发送消息 |
| **multi_agent_collaboration** | 多 Agent 间通信与协作 |
| **himalaya** | 邮件收发与日历管理 |

### 信息获取

| 技能 | 说明 |
|------|------|
| **news** | 新闻聚合与摘要 |
| **file_reader** | 本地文件读取与搜索 |
| **copaw_source_index** | CoPaw 源码索引与检索 |

### 任务调度

| 技能 | 说明 |
|------|------|
| **cron** | 定时任务创建与管理 |

### 引导

| 技能 | 说明 |
|------|------|
| **guidance** | 新用户引导与使用帮助 |

---

## 技能启用/禁用

### 通过控制台

**设置 → Skills** → 启用/禁用对应技能

### 通过 API

```bash
# 启用技能
curl -X POST http://127.0.0.1:8088/api/skills/{skill_id}/enable

# 禁用技能
curl -X POST http://127.0.0.1:8088/api/skills/{skill_id}/disable
```

---

## 自定义技能

### 技能结构

每个技能是一个目录，包含：

```
my_skill/
├── SKILL.md       # 技能定义（必须）— 包含提示词、元数据、使用规则
├── tools.py       # 工具实现（可选）
└── resources/     # 资源文件（可选）
```

### SKILL.md 格式

```markdown
---
name: my_skill
description: 技能描述
version: 1.0.0
tags: [tag1, tag2]
---

## 技能说明

描述这个技能做什么、什么时候用。

## 使用规则

- 何时使用此技能
- 何时不应使用
- 使用限制

## 命令示例

具体的命令调用示例。
```

### 自动加载

将自定义技能目录放在以下位置即可自动加载：

- 工作目录下的 `skills/` 文件夹
- 通过 `config.json` 中的 skills 配置指定路径

---

## 技能安全

安装技能前，CoPaw 会自动进行安全扫描，检测：

- **提示词注入** — 恶意提示词绕过安全限制
- **命令注入** — 在工具参数中注入系统命令
- **硬编码密钥** — 技能中包含 API Key 等敏感信息
- **数据外泄** — 技能尝试将数据发送到外部服务器

详细开发文档请参考 [官方文档 - Skills](https://copaw.agentscope.io/docs/skills)。

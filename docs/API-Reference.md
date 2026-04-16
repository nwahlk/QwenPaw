# API 接口文档

CoPaw 提供 RESTful API，所有接口前缀为 `/api`。

## Agent 管理

### 创建 Agent

```
POST /api/agents/create
```

### 获取 Agent 列表

```
GET /api/agents
```

### 获取 Agent 详情

```
GET /api/agents/{agent_id}
```

### 更新 Agent

```
PUT /api/agents/{agent_id}
```

### 删除 Agent

```
DELETE /api/agents/{agent_id}
```

### 启用/禁用 Agent

```
POST /api/agents/{agent_id}/enable
POST /api/agents/{agent_id}/disable
```

---

## 聊天

### 流式聊天

```
POST /api/chat/stream
```

返回 SSE (Server-Sent Events) 流式响应。

### 获取聊天列表

```
GET /api/chats
```

### 创建聊天

```
POST /api/chats
```

### 删除聊天

```
DELETE /api/chats/{chat_id}
```

### 获取消息

```
GET /api/messages
```

---

## 模型供应商

### 获取供应商列表

```
GET /api/providers
```

### 获取供应商详情

```
GET /api/providers/{provider_id}
```

### 更新供应商

```
PUT /api/providers/{provider_id}
```

### 检查供应商可用性

```
POST /api/providers/check
```

---

## Skills

### 获取技能列表

```
GET /api/skills
```

### 获取技能详情

```
GET /api/skills/{skill_id}
```

### 启用/禁用技能

```
POST /api/skills/{skill_id}/enable
POST /api/skills/{skill_id}/disable
```

### 技能流式接口

```
GET /api/skills/stream
```

---

## 配置

### 获取配置

```
GET /api/config
```

### 更新配置

```
PUT /api/config
```

### 获取环境变量

```
GET /api/envs
```

### 更新环境变量

```
PUT /api/envs
```

### 获取设置

```
GET /api/settings
```

---

## 控制台

### 控制台推送

```
POST /api/console/push
```

### 获取控制台历史

```
GET /api/console/history
```

---

## 文件

### 上传文件

```
POST /api/files/upload
```

### 获取文件

```
GET /api/files/{file_id}
```

---

## MCP

### 获取 MCP 客户端列表

```
GET /api/mcp
```

### 创建 MCP 客户端

```
POST /api/mcp
```

### 删除 MCP 客户端

```
DELETE /api/mcp/{mcp_id}
```

---

## 工具

### 获取工具列表

```
GET /api/tools
```

---

## 本地模型

### 本地模型管理

```
GET /api/local-models
```

---

## 语音

### 语音接口

```
GET /api/voice
```

---

## Token 使用

### 获取 Token 使用统计

```
GET /api/token-usage
```

---

## 认证

### 登录

```
POST /api/auth/login
```

> 需要设置 `COPAW_AUTH_ENABLED=true` 后才可用。

---

## 工作空间

### 工作空间管理

```
GET /api/workspace
```

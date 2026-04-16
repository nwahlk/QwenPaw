# 09 — API 接口规格（引导版模板）

---

| 项 | 值 |
|---|---|
| 模块编号 | M1-QA |
| 模块名称 | 投研问答助手 |
| 文档版本 | v0.1 |
| 阶段 | Design（How — 契约真源） |
| Base URL | `/api/v1/agent` |

---

> **本文是全部 API 端点的契约真源**。`05` 定义"用户要什么"，**09（本文）定义"后端必须返回什么"**，`13` 的测试断言以本文为准。

## 1. 端点总览

| # | 端点 | 方法 | 功能 | 成功码 |
|---|------|------|------|--------|
| 1 | `/api/v1/agent/capabilities` | GET | 能力探测 | 200 |
| 2 | `/api/v1/agent/ask` | POST | 问答提交 | 200 |
| 3 | `/api/v1/agent/sessions` | GET | 会话列表 | 200 |
| 4 | `/api/v1/agent/sessions` | POST | 新建会话 | 201 |
| 5 | `/api/v1/agent/sessions/<id>` | DELETE | 删除会话 | 200 |
| 6 | `/api/v1/agent/sessions/<id>/records` | GET | 问答记录 | 200 |
| 7 | `/api/v1/agent/health` | GET | 健康检查 | 200 |

## 2. 统一响应规范

### 成功响应

```json
{ "traceId": "tr_abc123...", /* 业务字段 */ }
```

### 错误响应

```json
{ "error": { "code": "EMPTY_QUERY", "message": "请输入问题", "details": {}, "traceId": "tr_..." } }
```

### 错误码清单

| HTTP | error.code | 触发条件 | details |
|------|-----------|----------|---------|
| 400 | `EMPTY_QUERY` | query 为空/null | `{}` |
| 400 | `INVALID_QUERY` | query 超 500 字符 | `{"max_length":500}` |
| 404 | `SESSION_NOT_FOUND` | session_id 不存在 | `{"session_id":"<id>"}` |
| 500 | `SERVER_ERROR` | 服务器内部错误 | `{}` |
| 504 | `LLM_TIMEOUT` | LLM 调用超时 | `{"timeout_ms":30000}` |

## 3. ★ 示例：POST /ask — 问答提交

**请求体**：

| 字段 | 类型 | 必填 | 约束 | 说明 |
|------|------|------|------|------|
| `query` | string | **是** | 1–500 字符 | 用户提问原文 |
| `session_id` | string | **是** | UUID | 目标会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `answer` | string | 是 | 答案文本 |
| `llm_used` | boolean | 是 | 是否使用真实 LLM |
| `model` | string\|null | 是 | 模型标识 |
| `response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `answer_source` | string | 是 | copaw / bailian / demo |

## 4. POST /sessions — 新建会话（请填写）

**请求体**：

| 字段 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `title` | string | 否 | "新会话" | 会话标题 |

**成功响应**（201）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `session_id` | string | 是 | 新建会话的 UUID |
| `title` | string | 是 | 会话标题（默认"新会话"） |
| `created_at` | string | 是 | 创建时间（ISO-8601） |
| `updated_at` | string | 是 | 更新时间（ISO-8601） |
| `query_count` | integer | 是 | 问答次数，初始为 0 |

## 5. GET /sessions — 会话列表（请填写）

> 无请求体，返回 sessions 数组。每个 session 至少包含 id、title、created_at、query_count。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `sessions` | array | 是 | 会话列表，按 created_at 倒序 |
| `sessions[].id` | string | 是 | 会话 UUID |
| `sessions[].title` | string | 是 | 会话标题 |
| `sessions[].created_at` | string | 是 | 创建时间（ISO-8601） |
| `sessions[].updated_at` | string | 是 | 更新时间（ISO-8601） |
| `sessions[].query_count` | integer | 是 | 问答次数 |

## 6. DELETE /sessions/<id> — 删除会话（请填写）

> 路径参数 session_id，无请求体，返回确认消息。注意级联删除关联记录。

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `session_id` | string (UUID) | 要删除的会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `message` | string | 是 | 删除确认消息 |
| `deleted_records` | integer | 是 | 级联删除的问答记录条数 |

**副作用**：删除该会话关联的全部 QARecord（级联删除，对齐 `10` §5.1 delete_session）。

**错误响应**：session_id 不存在时返回 404 `SESSION_NOT_FOUND`。

## 7. GET /sessions/<id>/records — 问答记录（请填写）

> 路径参数 session_id，返回 records 数组。每条记录含 query、answer、timestamp 等。

**路径参数**：

| 参数 | 类型 | 说明 |
|------|------|------|
| `session_id` | string (UUID) | 目标会话 ID |

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `traceId` | string | 是 | 链路追踪 ID |
| `records` | array | 是 | 问答记录列表，按 timestamp 正序 |
| `records[].id` | string | 是 | 记录 UUID |
| `records[].query` | string | 是 | 用户提问原文 |
| `records[].answer` | string | 是 | AI 回答文本 |
| `records[].llm_used` | boolean | 是 | 是否使用真实 LLM |
| `records[].answer_source` | string | 是 | copaw / bailian / demo |
| `records[].model` | string\|null | 是 | 模型标识 |
| `records[].response_time_ms` | integer | 是 | 响应耗时（毫秒） |
| `records[].timestamp` | string | 是 | 记录时间（ISO-8601） |

**错误响应**：session_id 不存在时返回 404 `SESSION_NOT_FOUND`。

## 8. 参数校验规则汇总

| 端点 | 字段 | 规则 | 失败 HTTP | error.code |
|------|------|------|-----------|-----------|
| POST /ask | `query` | 非空/非空白 | 400 | `EMPTY_QUERY` |
| POST /ask | `query` | ≤ 500 字符 | 400 | `INVALID_QUERY` |
| POST /ask | `session_id` | 非空 | 400 | `INVALID_QUERY` |
| DELETE /sessions/<id> | `session_id`（路径） | UUID 格式合法 | 400 | `INVALID_QUERY` |
| DELETE /sessions/<id> | `session_id`（路径） | 存在性 | 404 | `SESSION_NOT_FOUND` |
| GET /sessions/<id>/records | `session_id`（路径） | UUID 格式合法 | 400 | `INVALID_QUERY` |
| POST /sessions | `title` | ≤ 100 字符（可选） | 400 | `INVALID_QUERY` |

## 9. GET /health — 健康检查

> 无请求体，返回系统健康状态。对应 `05` US-004。

**成功响应**（200）：

| 字段 | 类型 | 必有 | 说明 |
|------|------|------|------|
| `status` | string | 是 | healthy / degraded |
| `uptime` | integer | 是 | 运行时长（秒） |
| `components.storage` | string | 是 | ok / error（数据目录可写性） |
| `components.llm` | string | 是 | ok / unavailable（LLM 可达性） |

---

| 版本 | 日期 | 说明 |
|------|------|------|
| v0.1 | 2026-04-14 | 首版填写 |

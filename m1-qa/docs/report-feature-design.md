# 研报上传与对比分析功能技术方案

> **文档版本**: v1.0  
> **创建日期**: 2026-04-15  
> **对齐规格**: m1-qa 现有代码风格与架构约束  
> **状态**: 提议

---

## 目录

1. [功能概述](#1-功能概述)
2. [API 端点设计](#2-api-端点设计)
3. [数据模型设计](#3-数据模型设计)
4. [对比分析 LLM Prompt 设计](#4-对比分析-llm-prompt-设计)
5. [前后端数据契约](#5-前后端数据契约)
6. [新增配置项](#6-新增配置项)
7. [新增依赖](#7-新增依赖)
8. [存储目录结构](#8-存储目录结构)
9. [实施建议](#9-实施建议)

---

## 1. 功能概述

### 1.1 业务需求

为 m1-qa 投研问答助手新增「研报上传与对比分析」功能模块，支持用户：
- 上传 PDF/DOCX 格式的投研报告
- 管理已上传的研报（查看列表、详情、删除）
- 选择两份研报进行智能对比分析
- 查看对比报告历史记录

### 1.2 设计原则

- **风格一致性**：严格对齐现有 `agent_bp.py` 路由定义模式、`storage.py` 存储层实现、`config.py` 配置管理方式
- **RMW 存储模式**：延续 JSON 文件存储的 Read-Modify-Write 全量读写模式
- **统一响应规范**：复用 `wsgi.py` 中的 `make_error` 错误响应工厂
- **LLM 降级策略**：对比分析功能复用现有 `agent.py` 的三级降级编排

### 1.3 架构位置

`
m1-qa/backend/
├── agent_bp.py          ← 新增 reports 路由组（6 个端点）
├── storage.py           ← 新增 reports/compares 存储方法
├── config.py            ← 新增研报相关配置项
├── agent.py             ← 新增 compare_report 方法（可选，或单独模块）
├── report_parser.py     ← 新增：PDF/DOCX 文本提取模块
└── data/
    ├── reports.json     ← 研报元数据
    ├── compares.json    ← 对比报告元数据
    └── report_files/    ← 实际文件存储目录
`

---

## 2. API 端点设计

### 2.1 统一响应规范（对齐现有代码）

**成功响应格式**：
``json
{
  "traceId": "tr_xxx",
  "...": "业务数据字段"
}
``

**错误响应格式**（复用 `wsgi.make_error`）：
``json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {},
    "traceId": "tr_xxx"
  }
}
``

---

### 2.2 POST /api/v1/agent/reports/upload

**描述**：上传研报文件（multipart/form-data）

**HTTP Method**: `POST`  
**URL**: `/api/v1/agent/reports/upload`  
**Content-Type**: `multipart/form-data`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| file | File | 是 | 研报文件，支持 PDF/DOCX |
| title | String | 否 | 研报标题，默认使用文件名 |

#### 成功响应（201）

``json
{
  "traceId": "tr_abc123",
  "report": {
    "id": "rpt_1713123456789",
    "title": "2024年AI行业深度研究报告",
    "filename": "ai_report_2024.pdf",
    "file_path": "report_files/2026/04/rpt_1713123456789.pdf",
    "file_size": 2048576,
    "file_type": "pdf",
    "text_content": "提取的文本内容...",
    "text_length": 15234,
    "upload_time": "2026-04-15T08:30:00.000Z",
    "status": "ready"
  }
}
``

#### 错误响应

| 状态码 | code | message | 场景 |
|--------|------|---------|------|
| 400 | EMPTY_FILE | 请选择要上传的文件 | 未选择文件 |
| 400 | INVALID_FILE_TYPE | 不支持的文件类型，仅支持 PDF/DOCX | 文件格式不符 |
| 400 | FILE_TOO_LARGE | 文件大小超过限制 | 超过 MAX_REPORT_SIZE |
| 400 | EMPTY_FILENAME | 文件名不能为空 | 文件名为空 |
| 500 | PARSE_ERROR | 文件解析失败，请检查文件是否损坏 | PDF/DOCX 解析异常 |
| 500 | SERVER_ERROR | 服务器繁忙，请稍后重试 | 其他异常 |

---

### 2.3 GET /api/v1/agent/reports

**描述**：获取研报列表

**HTTP Method**: `GET`  
**URL**: `/api/v1/agent/reports`

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | Integer | 否 | 页码，默认 1 |
| page_size | Integer | 否 | 每页条数，默认 20，最大 100 |
| status | String | 否 | 状态过滤：ready/parsing/error |

#### 成功响应（200）

``json
{
  "traceId": "tr_abc123",
  "reports": [
    {
      "id": "rpt_1713123456789",
      "title": "2024年AI行业深度研究报告",
      "filename": "ai_report_2024.pdf",
      "file_size": 2048576,
      "file_type": "pdf",
      "text_length": 15234,
      "upload_time": "2026-04-15T08:30:00.000Z",
      "status": "ready"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 20,
    "total": 35,
    "total_pages": 2
  }
}
``

---

### 2.4 GET /api/v1/agent/reports/<id>

**描述**：获取单份研报详情

**HTTP Method**: `GET`  
**URL**: `/api/v1/agent/reports/<report_id>`

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_id | String | 是 | 研报 ID（格式：rpt_xxx）|

#### 成功响应（200）

``json
{
  "traceId": "tr_abc123",
  "report": {
    "id": "rpt_1713123456789",
    "title": "2024年AI行业深度研究报告",
    "filename": "ai_report_2024.pdf",
    "file_path": "report_files/2026/04/rpt_1713123456789.pdf",
    "file_size": 2048576,
    "file_type": "pdf",
    "text_content": "提取的完整文本内容...",
    "text_length": 15234,
    "upload_time": "2026-04-15T08:30:00.000Z",
    "status": "ready",
    "metadata": {
      "pages": 25,
      "author": "张三",
      "word_count": 15234
    }
  }
}
``

#### 错误响应

| 状态码 | code | message | 场景 |
|--------|------|---------|------|
| 400 | INVALID_REPORT_ID | report_id 格式不合法 | ID 格式不符 |
| 404 | REPORT_NOT_FOUND | 研报不存在 | ID 对应记录不存在 |

---

### 2.5 DELETE /api/v1/agent/reports/<id>

**描述**：删除研报（同时删除文件和元数据）

**HTTP Method**: `DELETE`  
**URL**: `/api/v1/agent/reports/<report_id>`

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_id | String | 是 | 研报 ID |

#### 成功响应（200）

``json
{
  "traceId": "tr_abc123",
  "message": "研报已删除",
  "deleted_id": "rpt_1713123456789"
}
``

#### 错误响应

| 状态码 | code | message | 场景 |
|--------|------|---------|------|
| 400 | INVALID_REPORT_ID | report_id 格式不合法 | ID 格式不符 |
| 404 | REPORT_NOT_FOUND | 研报不存在 | ID 对应记录不存在 |

---

### 2.6 POST /api/v1/agent/reports/compare

**描述**：对比两份研报，生成分析报告

**HTTP Method**: `POST`  
**URL**: `/api/v1/agent/reports/compare`  
**Content-Type**: `application/json`

#### 请求参数

``json
{
  "report_ids": ["rpt_1713123456789", "rpt_1713123456790"],
  "focus_areas": ["行业趋势", "财务数据", "风险因素"]
}
``

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| report_ids | Array[String] | 是 | 两份研报的 ID 数组，长度必须为 2 |
| focus_areas | Array[String] | 否 | 对比关注点，最多 5 个 |

#### 成功响应（200）

``json
{
  "traceId": "tr_abc123",
  "compare": {
    "id": "cmp_1713123500000",
    "report_ids": ["rpt_1713123456789", "rpt_1713123456790"],
    "report_titles": ["2024年AI行业深度研究报告", "2024年半导体行业分析报告"],
    "focus_areas": ["行业趋势", "财务数据", "风险因素"],
    "compare_result": {
      "summary": "两份研报在行业趋势判断上存在差异...",
      "differences": [
        {
          "aspect": "行业趋势",
          "report_a_view": "AI行业处于高速增长期，预计三年翻倍",
          "report_b_view": "半导体行业增速放缓，库存周期见顶",
          "analysis": "两个行业处于不同周期阶段..."
        }
      ],
      "commonalities": [
        "两份报告均看好科技板块长期发展",
        "均提到中美科技竞争的影响"
      ],
      "recommendation": "建议投资者关注 AI 上游芯片供应链机会..."
    },
    "llm_used": true,
    "model": "qwen-turbo",
    "response_time_ms": 3500,
    "create_time": "2026-04-15T08:35:00.000Z"
  }
}
``

#### 错误响应

| 状态码 | code | message | 场景 |
|--------|------|---------|------|
| 400 | INVALID_REPORT_COUNT | 需要且仅需要两份研报进行对比 | report_ids 长度不为 2 |
| 400 | INVALID_REPORT_ID | report_id 格式不合法 | ID 格式不符 |
| 400 | DUPLICATE_REPORT | 不能对比同一份研报 | 两个 ID 相同 |
| 404 | REPORT_NOT_FOUND | 研报不存在 | 指定研报不存在 |
| 500 | SERVER_ERROR | 服务器繁忙，请稍后重试 | LLM 调用异常 |

---

### 2.7 GET /api/v1/agent/reports/compare/<id>

**描述**：获取对比报告详情

**HTTP Method**: `GET`  
**URL**: `/api/v1/agent/reports/compare/<compare_id>`

#### 路径参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| compare_id | String | 是 | 对比报告 ID（格式：cmp_xxx）|

#### 成功响应（200）

``json
{
  "traceId": "tr_abc123",
  "compare": {
    "id": "cmp_1713123500000",
    "report_ids": ["rpt_1713123456789", "rpt_1713123456790"],
    "report_titles": ["2024年AI行业深度研究报告", "2024年半导体行业分析报告"],
    "focus_areas": ["行业趋势", "财务数据", "风险因素"],
    "compare_result": {
      "summary": "两份研报在行业趋势判断上存在差异...",
      "differences": [...],
      "commonalities": [...],
      "recommendation": "..."
    },
    "llm_used": true,
    "model": "qwen-turbo",
    "response_time_ms": 3500,
    "create_time": "2026-04-15T08:35:00.000Z"
  }
}
``

#### 错误响应

| 状态码 | code | message | 场景 |
|--------|------|---------|------|
| 400 | INVALID_COMPARE_ID | compare_id 格式不合法 | ID 格式不符 |
| 404 | COMPARE_NOT_FOUND | 对比报告不存在 | ID 对应记录不存在 |

---

## 3. 数据模型设计

### 3.1 研报元数据 Schema

**文件**: `data/reports.json`  
**格式**: Array of Report

``json
[
  {
    "id": "rpt_1713123456789",
    "title": "2024年AI行业深度研究报告",
    "filename": "ai_report_2024.pdf",
    "file_path": "report_files/2026/04/rpt_1713123456789.pdf",
    "file_size": 2048576,
    "file_type": "pdf",
    "text_content": "提取的文本内容...",
    "text_length": 15234,
    "upload_time": "2026-04-15T08:30:00.000Z",
    "status": "ready",
    "metadata": {
      "pages": 25,
      "author": null,
      "word_count": 15234
    }
  }
]
``

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | String | 是 | 主键，格式 `rpt_{timestamp_ms}` |
| title | String | 是 | 研报标题，最多 200 字符 |
| filename | String | 是 | 原始文件名，最多 255 字符 |
| file_path | String | 是 | 相对于 data_dir 的文件存储路径 |
| file_size | Integer | 是 | 文件大小（字节）|
| file_type | String | 是 | 文件类型：pdf/docx |
| text_content | String | 是 | 提取的文本内容，可为空串 |
| text_length | Integer | 是 | 文本长度（字符数）|
| upload_time | String | 是 | 上传时间，ISO 8601 格式 |
| status | String | 是 | 状态：ready/parsing/error |
| metadata | Object | 否 | 额外元数据 |

---

### 3.2 对比报告 Schema

**文件**: `data/compares.json`  
**格式**: Array of Compare

``json
[
  {
    "id": "cmp_1713123500000",
    "report_ids": ["rpt_1713123456789", "rpt_1713123456790"],
    "report_titles": ["报告A标题", "报告B标题"],
    "focus_areas": ["行业趋势", "财务数据"],
    "compare_result": {
      "summary": "总结...",
      "differences": [...],
      "commonalities": [...],
      "recommendation": "..."
    },
    "llm_used": true,
    "model": "qwen-turbo",
    "response_time_ms": 3500,
    "create_time": "2026-04-15T08:35:00.000Z"
  }
]
``

**字段说明**：

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| id | String | 是 | 主键，格式 `cmp_{timestamp_ms}` |
| report_ids | Array[String] | 是 | 对比的两份研报 ID |
| report_titles | Array[String] | 是 | 两份研报标题快照 |
| focus_areas | Array[String] | 否 | 对比关注点 |
| compare_result | Object | 是 | LLM 生成的对比结果 |
| llm_used | Boolean | 是 | 是否使用了 LLM |
| model | String | 否 | 使用的模型名称 |
| response_time_ms | Integer | 是 | 响应时间（毫秒）|
| create_time | String | 是 | 创建时间，ISO 8601 格式 |

---

### 3.3 ID 格式规范

| 类型 | 格式 | 正则表达式 | 示例 |
|------|------|------------|------|
| 研报 ID | `rpt_{timestamp_ms}` | `^rpt_\d{13,}$` | rpt_1713123456789 |
| 对比 ID | `cmp_{timestamp_ms}` | `^cmp_\d{13,}$` | cmp_1713123500000 |

---

## 4. 对比分析 LLM Prompt 设计

### 4.1 System Prompt

``
你是一位专业的投研分析师，擅长对比分析不同投资研究报告的异同点。

你的任务是根据用户提供的两份研报内容，进行深入对比分析，输出结构化的分析结果。

分析要点：
1. 识别两份报告的核心观点差异
2. 找出共识和共同结论
3. 分析差异背后的原因（方法论、数据源、立场等）
4. 给出综合投资建议

输出要求：
- 客观中立，不带主观偏见
- 论点需有论据支撑
- 结构清晰，便于阅读
- 使用专业但易懂的语言
``

### 4.2 User Prompt 模板

``
请对比分析以下两份投研报告：

【报告 A】标题：{report_a_title}
---
{report_a_content}
---

【报告 B】标题：{report_b_title}
---
{report_b_content}
---

{focus_areas_section}

请按以下 JSON 格式输出分析结果（仅输出 JSON，不要其他内容）：
{
  "summary": "两份研报的整体对比总结（200字以内）",
  "differences": [
    {
      "aspect": "对比维度名称",
      "report_a_view": "报告 A 的观点",
      "report_b_view": "报告 B 的观点",
      "analysis": "差异分析"
    }
  ],
  "commonalities": ["共识点1", "共识点2"],
  "recommendation": "综合投资建议（150字以内）"
}
``

**focus_areas_section 生成逻辑**：
``python
if focus_areas:
    return f"请重点关注以下维度：{', '.join(focus_areas)}"
else:
    return "请自行识别关键对比维度"
``

### 4.3 Prompt 长度控制

由于 LLM 有上下文长度限制，需要对文本内容进行截断：

``python
MAX_PROMPT_LENGTH = 30000  # 约 2 万字中文

def truncate_text(text: str, max_length: int) -> str:
    if len(text) <= max_length:
        return text
    # 优先保留开头和结尾
    head = text[:max_length // 2]
    tail = text[-(max_length // 2):]
    return f"{head}\n\n...[中间部分已省略]...\n\n{tail}"
``

### 4.4 LLM 调用集成方案

在 `agent.py` 中新增 `compare_reports` 方法，复用三级降级策略：

``python
def compare_reports(self, report_a: dict, report_b: dict, focus_areas: list) -> dict:
    """
    对比两份研报，返回分析结果。
    复用三级降级：CoPaw → 百炼 → Demo
    
    返回: {compare_result, llm_used, model, response_time_ms}
    """
    start = time.time()
    
    # 构建 prompt
    system_prompt = self._build_compare_system_prompt()
    user_prompt = self._build_compare_user_prompt(report_a, report_b, focus_areas)
    
    # 第 1 级：CoPaw
    result = self.copaw.compare(system_prompt, user_prompt)
    if result:
        result["response_time_ms"] = int((time.time() - start) * 1000)
        return result
    
    # 第 2 级：百炼
    result = self.bailian.compare(system_prompt, user_prompt)
    if result:
        result["response_time_ms"] = int((time.time() - start) * 1000)
        return result
    
    # 第 3 级：Demo 模式
    return self._generate_demo_compare(report_a, report_b, start)
``

---

## 5. 前后端数据契约

### 5.1 文件上传契约

**Request**:
``
POST /api/v1/agent/reports/upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="file"; filename="report.pdf"
Content-Type: application/pdf

<binary data>
------WebKitFormBoundary
Content-Disposition: form-data; name="title"

2024年AI行业研究报告
------WebKitFormBoundary--
``

**前端代码示例（React + Ant Design Upload）**:
``tsx
import { Upload, Button, message } from 'antd';
import { UploadOutlined } from '@ant-design/icons';

const ReportUpload = () => {
  const uploadProps = {
    name: 'file',
    action: '/api/v1/agent/reports/upload',
    accept: '.pdf,.docx',
    maxCount: 1,
    data: { title: '研报标题' }, // 可选
    onChange(info) {
      if (info.file.status === 'done') {
        message.success('上传成功');
        console.log(info.file.response.report);
      } else if (info.file.status === 'error') {
        message.error(info.file.response.error.message);
      }
    },
  };

  return (
    <Upload {...uploadProps}>
      <Button icon={<UploadOutlined />}>上传研报</Button>
    </Upload>
  );
};
``

### 5.2 研报列表查询契约

**Request**:
``
GET /api/v1/agent/reports?page=1&page_size=20 HTTP/1.1
``

**前端代码示例**:
``tsx
const fetchReports = async (page = 1, pageSize = 20) => {
  const response = await fetch(
    /api/v1/agent/reports?page=&page_size=
  );
  const data = await response.json();
  return data;
};
``

### 5.3 对比分析契约

**Request**:
``json
POST /api/v1/agent/reports/compare
{
  "report_ids": ["rpt_1713123456789", "rpt_1713123456790"],
  "focus_areas": ["行业趋势", "财务数据"]
}
``

**前端代码示例**:
``tsx
const compareReports = async (reportIds: string[], focusAreas?: string[]) => {
  const response = await fetch('/api/v1/agent/reports/compare', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      report_ids: reportIds,
      focus_areas: focusAreas,
    }),
  });
  const data = await response.json();
  return data.compare;
};
``

---

## 6. 新增配置项

在 `config.py` 中新增以下配置：

``python
# ── 研报上传配置 ──
REPORT_UPLOAD_DIR = Path(os.getenv("REPORT_UPLOAD_DIR", os.path.join(DATA_DIR, "report_files")))
MAX_REPORT_SIZE = int(os.getenv("MAX_REPORT_SIZE", "10485760"))  # 10MB
ALLOWED_REPORT_TYPES = os.getenv("ALLOWED_REPORT_TYPES", "pdf,docx").split(",")
MAX_REPORT_TITLE_LENGTH = int(os.getenv("MAX_REPORT_TITLE_LENGTH", "200"))
MAX_COMPARE_TEXT_LENGTH = int(os.getenv("MAX_COMPARE_TEXT_LENGTH", "30000"))  # Prompt 截断阈值
``

**配置项说明**：

| 配置项 | 环境变量 | 默认值 | 说明 |
|--------|----------|--------|------|
| REPORT_UPLOAD_DIR | REPORT_UPLOAD_DIR | data/report_files | 研报文件存储目录 |
| MAX_REPORT_SIZE | MAX_REPORT_SIZE | 10485760 (10MB) | 单个文件最大大小 |
| ALLOWED_REPORT_TYPES | ALLOWED_REPORT_TYPES | pdf,docx | 允许的文件类型 |
| MAX_REPORT_TITLE_LENGTH | MAX_REPORT_TITLE_LENGTH | 200 | 标题最大长度 |
| MAX_COMPARE_TEXT_LENGTH | MAX_COMPARE_TEXT_LENGTH | 30000 | 对比分析文本截断长度 |

---

## 7. 新增依赖

在 `requirements.txt` 中新增：

``
# 研报解析
pdfplumber>=0.10.0    # PDF 文本提取
python-docx>=1.1.0    # DOCX 文本提取
``

**依赖说明**：

| 包名 | 用途 | 版本要求 |
|------|------|----------|
| pdfplumber | PDF 文本提取，支持表格、布局保留 | >=0.10.0 |
| python-docx | DOCX 文本提取 | >=1.1.0 |

**文本提取模块设计** (`report_parser.py`):

``python
"""
研报文本提取模块
支持 PDF、DOCX 格式
"""
import pdfplumber
from docx import Document

def extract_text_from_pdf(file_path: str) -> tuple[str, dict]:
    """
    从 PDF 提取文本
    返回: (文本内容, 元数据)
    """
    text_parts = []
    metadata = {"pages": 0, "author": None}
    
    with pdfplumber.open(file_path) as pdf:
        metadata["pages"] = len(pdf.pages)
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
    
    return "\n\n".join(text_parts), metadata

def extract_text_from_docx(file_path: str) -> tuple[str, dict]:
    """
    从 DOCX 提取文本
    返回: (文本内容, 元数据)
    """
    doc = Document(file_path)
    text_parts = []
    metadata = {"pages": None, "author": doc.core_properties.author}
    
    for para in doc.paragraphs:
        if para.text.strip():
            text_parts.append(para.text)
    
    return "\n\n".join(text_parts), metadata

def extract_text(file_path: str, file_type: str) -> tuple[str, dict]:
    """
    统一入口：根据文件类型调用对应提取器
    """
    if file_type == "pdf":
        return extract_text_from_pdf(file_path)
    elif file_type == "docx":
        return extract_text_from_docx(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")
``

---

## 8. 存储目录结构

``
m1-qa/backend/data/
├── sessions.json           # 现有：会话元数据
├── qa_records.json         # 现有：问答记录
├── reports.json            # 新增：研报元数据
├── compares.json           # 新增：对比报告元数据
└── report_files/           # 新增：研报文件存储
    └── 2026/               # 按年份组织
        └── 04/             # 按月份组织
            ├── rpt_1713123456789.pdf
            ├── rpt_1713123456790.docx
            └── ...
``

**目录组织原则**：
- 按年/月分目录，避免单目录文件过多
- 文件名使用 `rpt_{id}.{ext}` 格式，避免文件名冲突
- 删除研报时同步删除对应文件

---

## 9. 实施建议

### 9.1 实施顺序

1. **Phase 1 - 基础设施**（后端）
   - 新增配置项 (`config.py`)
   - 新增依赖安装 (`requirements.txt`)
   - 实现文本提取模块 (`report_parser.py`)
   - 扩展 Storage 层 (`storage.py`)

2. **Phase 2 - API 实现**（后端）
   - 实现研报上传 API
   - 实现研报列表/详情/删除 API
   - 实现对比分析 API（集成 LLM）
   - 实现对比报告查询 API

3. **Phase 3 - 前端集成**（前端）
   - 研报上传组件
   - 研报列表页面
   - 对比分析页面
   - 对比报告详情页面

### 9.2 关键注意事项

1. **文件上传安全**
   - 校验文件类型（扩展名 + MIME Type）
   - 限制文件大小
   - 防止路径遍历攻击
   - 文件名消毒（移除特殊字符）

2. **LLM 调用优化**
   - 文本内容需截断，避免超出上下文限制
   - 对比分析是耗时操作，考虑前端 Loading 状态
   - 可考虑引入任务队列，支持异步处理

3. **存储一致性**
   - 删除研报时需同步删除文件
   - 使用事务性思维保证 JSON 文件与物理文件一致

4. **错误处理**
   - 文件解析失败需返回友好错误信息
   - LLM 调用失败需有降级方案

---

## 附录 A：错误码清单

| code | message | HTTP Status |
|------|---------|-------------|
| EMPTY_FILE | 请选择要上传的文件 | 400 |
| INVALID_FILE_TYPE | 不支持的文件类型，仅支持 PDF/DOCX | 400 |
| FILE_TOO_LARGE | 文件大小超过限制 | 400 |
| EMPTY_FILENAME | 文件名不能为空 | 400 |
| PARSE_ERROR | 文件解析失败，请检查文件是否损坏 | 500 |
| INVALID_REPORT_ID | report_id 格式不合法 | 400 |
| REPORT_NOT_FOUND | 研报不存在 | 404 |
| INVALID_REPORT_COUNT | 需要且仅需要两份研报进行对比 | 400 |
| DUPLICATE_REPORT | 不能对比同一份研报 | 400 |
| INVALID_COMPARE_ID | compare_id 格式不合法 | 400 |
| COMPARE_NOT_FOUND | 对比报告不存在 | 404 |
| SERVER_ERROR | 服务器繁忙，请稍后重试 | 500 |

---

## 附录 B：参考文件

- `backend/agent_bp.py` — 现有路由定义模式
- `backend/storage.py` — JSON 存储层实现
- `backend/config.py` — 配置管理方式
- `backend/agent.py` — LLM 编排方式
- `backend/wsgi.py` — 蓝图注册与错误处理

---

**文档结束**
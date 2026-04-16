# 投研问答助手 (M1-QA) 压力测试报告

| 项目 | 值 |
|------|------|
| **测试目标** | http://ira.vin |
| **测试日期** | 2026-04-16 |
| **测试工具** | Locust 2.43.4 (headless) |
| **并发用户** | 10 |
| **加压速率** | 2 用户/秒 |
| **持续时间** | 60 秒 |
| **总请求数** | 276 |
| **失败数** | 0 (0.00%) |
| **总吞吐量** | 4.67 req/s |

---

## 1. 测试概览

| 指标 | 值 |
|------|------|
| 平均响应时间 | **109 ms** |
| 最小响应时间 | 45 ms |
| 最大响应时间 | 494 ms |
| P50 (中位数) | 78 ms |
| P90 | 200 ms |
| P95 | 240 ms |
| P99 | 380 ms |
| 错误率 | **0.00%** |

**结论：所有 276 个请求全部成功返回，零失败，P95 < 250ms，系统在 10 并发下表现稳定。**

---

## 2. 各端点性能明细

### 2.1 响应时间排名（按平均耗时降序）

| 端点 | 方法 | 请求数 | 失败 | 平均(ms) | P50(ms) | P90(ms) | P95(ms) | 最大(ms) |
|------|------|--------|------|----------|---------|---------|---------|----------|
| `/api/v1/reports/drafts` | GET | 9 | 0 | 135 | 81 | 270 | 270 | 266 |
| `/api/v1/research/qa/ask` | POST | 12 | 0 | 134 | 77 | 230 | 490 | 495 |
| `/api/v1/sentiment/alerts` | GET | 12 | 0 | 126 | 90 | 190 | 300 | 297 |
| `/api/v1/dashboard/todos` | GET | 22 | 0 | 125 | 82 | 200 | 250 | 377 |
| `/api/v1/compliance/blocks/recent` | GET | 13 | 0 | 122 | 110 | 190 | 230 | 228 |
| `/api/v1/compliance/rules` | GET | 27 | 0 | 108 | 79 | 190 | 230 | 332 |
| `/api/v1/kb/documents` | GET | 19 | 0 | 108 | 79 | 200 | 210 | 212 |
| `/api/v1/sentiment/mock/kpis` | GET | 9 | 0 | 107 | 64 | 280 | 280 | 282 |
| `/api/v1/kb/index/status` | GET | 11 | 0 | 106 | 78 | 240 | 240 | 242 |
| `/api/v1/system/settings` | GET | 7 | 0 | 106 | 71 | 210 | 210 | 209 |
| `/api/v1/compliance/scan` | POST | 28 | 0 | 105 | 73 | 170 | 220 | 469 |
| `/api/v1/dashboard/kpi` | GET | 28 | 0 | 104 | 76 | 190 | 210 | 244 |
| `/api/v1/system/health` | GET | 44 | 0 | 103 | 71 | 200 | 250 | 269 |
| `/api/v1/lineage/search` | GET | 11 | 0 | 96 | 75 | 170 | 210 | 208 |
| `/api/v1/sentiment/watchlist` | GET | 10 | 0 | 94 | 75 | 190 | 190 | 187 |
| `/api/v1/sessions/recent` | GET | 14 | 0 | 92 | 72 | 140 | 250 | 252 |

### 2.2 按业务模块汇总

| 模块 | 请求数 | 平均(ms) | P50(ms) | P95(ms) | 最大(ms) |
|------|--------|----------|---------|---------|----------|
| **合规扫描** (rules + scan + blocks) | 68 | 111 | 79 | 230 | 469 |
| **工作台** (kpi + todos + sessions) | 64 | 108 | 78 | 250 | 377 |
| **系统** (health + settings) | 51 | 103 | 71 | 250 | 269 |
| **知识库** (documents + index) | 30 | 107 | 78 | 240 | 242 |
| **舆情** (alerts + kpis + watchlist) | 31 | 110 | 78 | 300 | 297 |
| **研报问答** (qa/ask) | 12 | 134 | 77 | 490 | 495 |
| **报告** (drafts) | 9 | 135 | 81 | 270 | 266 |
| **血缘** (lineage/search) | 11 | 96 | 75 | 210 | 208 |

---

## 3. 吞吐量分析

| 端点 | req/s |
|------|-------|
| `/api/v1/system/health` | 0.74 |
| `/api/v1/dashboard/kpi` | 0.48 |
| `/api/v1/compliance/scan` | 0.48 |
| `/api/v1/compliance/rules` | 0.46 |
| `/api/v1/dashboard/todos` | 0.37 |
| `/api/v1/kb/documents` | 0.31 |
| 其余端点 | 0.12 ~ 0.24 |
| **总计** | **4.67** |

---

## 4. 响应时间分布

```
P50  ████████░░░░░░░░░░░░  78ms
P66  ██████████░░░░░░░░░░ 100ms
P75  ████████████░░░░░░░░ 150ms
P80  █████████████░░░░░░░ 160ms
P90  ████████████████░░░░ 200ms
P95  ██████████████████░░ 240ms
P99  ██████████████████████████████████ 380ms
MAX  ██████████████████████████████████████████████████ 494ms
```

---

## 5. 关键发现

### 5.1 优势
1. **零错误率** — 全部 276 个请求 100% 成功，系统稳定性良好
2. **低延迟** — 平均响应 109ms，P50 仅 78ms，满足实时交互需求
3. **P95 可控** — 95% 请求在 240ms 内完成，用户体验流畅
4. **合规扫描高性能** — POST `/compliance/scan` 平均仅 105ms，P50 73ms

### 5.2 关注点
1. **问答端点尾部延迟** — `/research/qa/ask` P95 达 490ms，最大 495ms（演示环境 LLM 未配置，为 Mock 响应；生产环境接入 LLM 后需重点关注）
2. **报告端点响应波动** — `/reports/drafts` 平均 135ms，P90 270ms，波动较大
3. **吞吐量上限** — 当前 10 并发 ≈ 4.67 req/s，建议后续阶梯加压（20/50/100 用户）验证天花板

### 5.3 建议
| 优先级 | 建议 |
|--------|------|
| **高** | 接入 LLM 后对 `/research/qa/ask` 单独做压测，设定 SLA ≤ 3s |
| **中** | 对合规扫描 `/compliance/scan` 做 50 并发加压，验证规则引擎并发安全 |
| **中** | 阶梯加压至 50/100 用户，找到系统吞吐瓶颈 |
| **低** | 监控 `/reports/drafts` 响应时间波动，排查是否有数据库慢查询 |

---

## 6. 测试配置

### locustfile 覆盖的 API 端点（16 个）

| 标签 | 端点 | 权重 |
|------|------|------|
| health | `GET /api/v1/system/health` | 5 |
| dashboard | `GET /api/v1/dashboard/kpi` | 4 |
| compliance | `POST /api/v1/compliance/scan` | 4 |
| compliance | `GET /api/v1/compliance/rules` | 3 |
| dashboard | `GET /api/v1/dashboard/todos` | 3 |
| kb | `GET /api/v1/kb/documents` | 3 |
| qa | `POST /api/v1/research/qa/ask` | 2 |
| compliance | `GET /api/v1/compliance/blocks/recent` | 2 |
| kb | `GET /api/v1/kb/index/status` | 2 |
| reports | `GET /api/v1/reports/drafts` | 2 |
| sentiment | `GET /api/v1/sentiment/alerts` | 2 |
| dashboard | `GET /api/v1/sessions/recent` | 2 |
| sentiment | `GET /api/v1/sentiment/mock/kpis` | 1 |
| sentiment | `GET /api/v1/sentiment/watchlist` | 1 |
| lineage | `GET /api/v1/lineage/search` | 1 |
| system | `GET /api/v1/system/settings` | 1 |

### 输出文件

| 文件 | 路径 |
|------|------|
| Locust 脚本 | `m1-qa/backend/locustfile.py` |
| 统计 CSV | `m1-qa/docs/locust_report_stats.csv` |
| 百分位 CSV | `m1-qa/docs/locust_report_stats_history.csv` |
| 失败 CSV | `m1-qa/docs/locust_report_failures.csv` |
| 本报告 | `m1-qa/docs/load-test-report.md` |

---

## 7. 结论

> 在 **10 并发用户、60 秒持续加压** 条件下，http://ira.vin 全部 **16 个 API 端点、276 次请求零失败**，平均响应 109ms，P95 240ms。系统在当前负载下表现稳定且高效，满足投研工作台的实时交互需求。
>
> **总体评级：A（优秀）** — 建议后续接入 LLM 后对问答链路做专项压测，并阶梯加压至 50/100 用户验证系统容量上限。

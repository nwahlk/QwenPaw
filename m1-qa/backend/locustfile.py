"""
投研问答助手 (M1-QA) Locust 压力测试
目标: http://ira.vin
测试场景: 模拟多用户并发访问核心 API 端点
"""

import json
import random
from locust import HttpUser, task, between, tag, events


# ---------------------------------------------------------------------------
# 测试数据
# ---------------------------------------------------------------------------

COMPLIANCE_TEXTS = [
    "本产品年化收益稳定，基本无风险，适合全仓配置。",
    "建议投资者买入该股票，保证收益翻倍。",
    "根据市场分析，该基金长期价值值得关注，投资有风险，入市需谨慎。",
    "该公司基本面良好，市盈率处于合理区间。",
    "稳赚不赔，立刻调仓获取高收益！",
    "经过深入研究，我们认为该债券产品具有较高的配置价值。",
    "该理财产品保本保收益，无风险投资首选。",
    "今日市场整体表现平稳，沪深两市震荡整理。",
]

QA_QUESTIONS = [
    "请介绍一下沪深300指数的特点",
    "如何分析一只基金的投资价值？",
    "什么是量化投资策略？",
    "当前宏观经济对股市有什么影响？",
    "债券基金和股票基金的区别是什么？",
    "如何评估一家公司的财务健康状况？",
]

STOCK_CODES = ["600519", "000858", "601318", "000001", "300750", "002594"]


# ---------------------------------------------------------------------------
# 用户行为定义
# ---------------------------------------------------------------------------

class IRAWorkshopUser(HttpUser):
    """模拟投研助手平台的普通用户行为"""

    wait_time = between(1, 3)
    host = "http://ira.vin"

    def on_start(self):
        """登录获取会话"""
        self.client.post("/api/v1/auth/login", json={
            "username": "demo",
            "password": "ira.vin",
        }, name="/api/v1/auth/login", catch_response=True)

    # ── 高频访问: 首页与健康检查 ──────────────────────────────

    @tag("health")
    @task(5)
    def health_check(self):
        """系统健康检查 — 最高频"""
        self.client.get("/api/v1/system/health", name="/api/v1/system/health")

    @tag("dashboard")
    @task(4)
    def dashboard_kpi(self):
        """工作台 KPI 面板"""
        self.client.get("/api/v1/dashboard/kpi", name="/api/v1/dashboard/kpi")

    @tag("dashboard")
    @task(3)
    def dashboard_todos(self):
        """工作台待办队列"""
        self.client.get("/api/v1/dashboard/todos", name="/api/v1/dashboard/todos")

    @tag("dashboard")
    @task(2)
    def recent_sessions(self):
        """最近会话列表"""
        self.client.get("/api/v1/sessions/recent", name="/api/v1/sessions/recent")

    # ── 核心业务: 合规扫描 ────────────────────────────────────

    @tag("compliance")
    @task(3)
    def compliance_rules(self):
        """获取合规规则集"""
        self.client.get("/api/v1/compliance/rules", name="/api/v1/compliance/rules")

    @tag("compliance")
    @task(4)
    def compliance_scan(self):
        """执行合规扫描 (POST)"""
        text = random.choice(COMPLIANCE_TEXTS)
        self.client.post(
            "/api/v1/compliance/scan",
            json={"text": text},
            name="/api/v1/compliance/scan",
        )

    @tag("compliance")
    @task(2)
    def compliance_recent_blocks(self):
        """获取最近审计流水"""
        self.client.get(
            "/api/v1/compliance/blocks/recent",
            name="/api/v1/compliance/blocks/recent",
        )

    # ── 核心业务: 研报问答 ────────────────────────────────────

    @tag("qa")
    @task(2)
    def qa_ask(self):
        """提交研报问答"""
        question = random.choice(QA_QUESTIONS)
        self.client.post(
            "/api/v1/research/qa/ask",
            json={"question": question},
            headers={"X-Spec-Version": "ira-1.1.0"},
            name="/api/v1/research/qa/ask",
        )

    # ── 知识库 ────────────────────────────────────────────────

    @tag("kb")
    @task(3)
    def kb_documents(self):
        """获取知识库文档列表"""
        self.client.get("/api/v1/kb/documents", name="/api/v1/kb/documents")

    @tag("kb")
    @task(2)
    def kb_index_status(self):
        """获取索引状态"""
        self.client.get("/api/v1/kb/index/status", name="/api/v1/kb/index/status")

    # ── 报告管理 ──────────────────────────────────────────────

    @tag("reports")
    @task(2)
    def reports_list(self):
        """获取报告草稿列表"""
        self.client.get("/api/v1/reports/drafts", name="/api/v1/reports/drafts")

    # ── 舆情监控 ──────────────────────────────────────────────

    @tag("sentiment")
    @task(2)
    def sentiment_alerts(self):
        """获取舆情预警"""
        self.client.get("/api/v1/sentiment/alerts", name="/api/v1/sentiment/alerts")

    @tag("sentiment")
    @task(1)
    def sentiment_kpis(self):
        """获取舆情 KPI"""
        self.client.get(
            "/api/v1/sentiment/mock/kpis",
            name="/api/v1/sentiment/mock/kpis",
        )

    @tag("sentiment")
    @task(1)
    def sentiment_watchlist(self):
        """获取舆情监控列表"""
        self.client.get(
            "/api/v1/sentiment/watchlist",
            name="/api/v1/sentiment/watchlist",
        )

    # ── 数据血缘 ──────────────────────────────────────────────

    @tag("lineage")
    @task(1)
    def lineage_search(self):
        """搜索血缘链路"""
        self.client.get(
            "/api/v1/lineage/search?q=&limit=24",
            name="/api/v1/lineage/search",
        )

    # ── 系统设置 ──────────────────────────────────────────────

    @tag("system")
    @task(1)
    def system_settings(self):
        """获取系统设置"""
        self.client.get(
            "/api/v1/system/settings",
            name="/api/v1/system/settings",
        )

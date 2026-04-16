"""
M1-QA 研报知识库增强问答测试
覆盖: report_storage.search_reports + agent._build_report_context + API 端点
"""
import os
import sys
import time
import uuid

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_report_storage(tmp_path):
    """使用临时目录创建 ReportStorage 实例"""
    from report_storage import ReportStorage
    return ReportStorage(str(tmp_path / "data"))


@pytest.fixture
def seeded_report_storage(tmp_report_storage):
    """预置多条研报记录，用于检索测试"""
    ts_base = int(time.time() * 1000)
    
    # 研报1：AI 行业相关
    r1 = {
        "id": f"rpt_{ts_base}",
        "title": "2024年AI行业深度研究报告",
        "filename": "ai_report.pdf",
        "file_path": f"report_files/2026/04/rpt_{ts_base}.pdf",
        "file_size": 1024,
        "file_type": "pdf",
        "text_content": (
            "AI行业正处于高速增长阶段，预计未来三年市场规模将翻倍。\n"
            "主要驱动因素包括：算力提升、算法突破、应用场景拓展。\n"
            "重点推荐关注 GPU 芯片厂商和 AI 应用层企业。\n"
            "风险提示：估值偏高，注意回调风险。"
        ),
        "text_length": 80,
        "upload_time": "2026-04-15T08:30:00.000000+00:00",
        "status": "ready",
        "metadata": {"pages": 5, "author": None, "word_count": 80},
    }
    
    # 研报2：半导体行业相关
    r2 = {
        "id": f"rpt_{ts_base + 1}",
        "title": "2024年半导体行业分析报告",
        "filename": "semi_report.pdf",
        "file_path": f"report_files/2026/04/rpt_{ts_base + 1}.pdf",
        "file_size": 2048,
        "file_type": "pdf",
        "text_content": (
            "半导体行业当前处于库存周期见顶阶段，增速有所放缓。\n"
            "但先进制程需求依然旺盛，特别是 AI 芯片需求强劲。\n"
            "建议关注具有先进制程能力的龙头企业。\n"
            "风险因素：地缘政治风险、需求不及预期。"
        ),
        "text_length": 85,
        "upload_time": "2026-04-15T08:31:00.000000+00:00",
        "status": "ready",
        "metadata": {"pages": 8, "author": None, "word_count": 85},
    }
    
    # 研报3：不相关主题（医疗）
    r3 = {
        "id": f"rpt_{ts_base + 2}",
        "title": "2024年医疗器械行业研究报告",
        "filename": "medical_report.pdf",
        "file_path": f"report_files/2026/04/rpt_{ts_base + 2}.pdf",
        "file_size": 1536,
        "file_type": "pdf",
        "text_content": (
            "医疗器械行业保持稳健增长，受益于人口老龄化趋势。\n"
            "重点关注高端影像设备和手术机器人领域。\n"
            "政策支持力度大，行业前景广阔。"
        ),
        "text_length": 60,
        "upload_time": "2026-04-15T08:32:00.000000+00:00",
        "status": "ready",
        "metadata": {"pages": 6, "author": None, "word_count": 60},
    }
    
    # 研报4：状态为 error（不应被检索）
    r4 = {
        "id": f"rpt_{ts_base + 3}",
        "title": "损坏的报告",
        "filename": "error_report.pdf",
        "file_path": f"report_files/2026/04/rpt_{ts_base + 3}.pdf",
        "file_size": 512,
        "file_type": "pdf",
        "text_content": "这是一份损坏的报告",
        "text_length": 10,
        "upload_time": "2026-04-15T08:33:00.000000+00:00",
        "status": "error",
        "metadata": {},
    }
    
    tmp_report_storage.create_report(r1)
    tmp_report_storage.create_report(r2)
    tmp_report_storage.create_report(r3)
    tmp_report_storage.create_report(r4)
    
    return tmp_report_storage, [r1, r2, r3, r4]


# ── ReportStorage.search_reports 单元测试 ────────────────────────────────────

class TestReportSearch:

    def test_search_basic(self, seeded_report_storage):
        """基本检索：AI 相关问题应返回 AI 研报"""
        storage, reports = seeded_report_storage
        
        results = storage.search_reports("AI行业发展前景如何", top_k=3)
        
        # 应返回至少 1 条结果
        assert len(results) >= 1
        
        # AI 研报应排在前面（得分最高）
        top_result = results[0]
        assert "AI" in top_result["title"] or "ai" in top_result["title"].lower()
        assert top_result["excerpt"] != ""
        assert top_result["score"] > 0

    def test_search_with_report_ids_filter(self, seeded_report_storage):
        """指定 report_ids 时只检索这些研报"""
        storage, reports = seeded_report_storage
        r1, r2, r3, r4 = reports
        
        # 只在 AI 研报中检索
        results = storage.search_reports(
            "半导体芯片",
            top_k=3,
            report_ids=[r1["id"]],  # 只检索 AI 研报
        )
        
        # 结果应来自 AI 研报（可能得分为 0 所以返回空）
        for r in results:
            assert r["id"] == r1["id"]

    def test_search_no_keywords_match(self, seeded_report_storage):
        """无关键词匹配时返回空列表"""
        storage, reports = seeded_report_storage
        
        # 使用完全不相关的问题
        results = storage.search_reports("xyz123不存在的关键词", top_k=3)
        
        # 得分为 0 时不返回结果
        assert len(results) == 0

    def test_search_excludes_error_status(self, seeded_report_storage):
        """检索应排除 status 为 error 的研报"""
        storage, reports = seeded_report_storage
        r4 = reports[3]  # error 状态的研报
        
        # 使用 error 研报中的内容作为查询
        results = storage.search_reports("损坏的报告", top_k=10)
        
        # error 状态的研报不应出现在结果中
        for r in results:
            assert r["id"] != r4["id"]

    def test_search_empty_query(self, tmp_report_storage):
        """空查询返回空列表"""
        results = tmp_report_storage.search_reports("", top_k=3)
        assert results == []
        
        results = tmp_report_storage.search_reports("   ", top_k=3)
        assert results == []

    def test_search_excerpt_length_limit(self, seeded_report_storage):
        """摘录应受 max_length 限制"""
        storage, reports = seeded_report_storage
        
        results = storage.search_reports("AI", top_k=1, excerpt_max_length=50)
        
        if results:
            excerpt = results[0]["excerpt"]
            assert len(excerpt) <= 50

    def test_keyword_extraction(self):
        """关键词提取测试"""
        from report_storage import ReportStorage
        
        # 中文问题
        kw1 = ReportStorage._extract_keywords("AI行业发展前景")
        assert "ai" in kw1  # 英文单词
        assert any("行业" in k or "发展" in k or "前景" in k for k in kw1)  # 中文片段
        
        # 英文问题
        kw2 = ReportStorage._extract_keywords("What is the AI market size")
        assert "ai" in kw2
        assert "market" in kw2
        assert "size" in kw2

    def test_keyword_score_calculation(self):
        """关键词得分计算测试"""
        from report_storage import ReportStorage
        
        keywords = ["AI", "行业"]
        text = "AI行业正处于高速增长阶段。AI技术发展迅速。"
        
        score = ReportStorage._calc_keyword_score(keywords, text)
        
        # AI 出现 2 次，长度 2；行业出现 1 次，长度 2
        # 得分 = 2*2 + 2*1 = 6
        assert score == 6


# ── Agent 研报上下文构建测试 ────────────────────────────────────────────────

class TestAgentReportContext:

    def test_build_report_context_basic(self, seeded_report_storage):
        """Agent 正确构建研报上下文"""
        import importlib
        import config
        importlib.reload(config)
        from agent import CoPawAgent
        
        storage, reports = seeded_report_storage
        agent = CoPawAgent()
        
        context, sources = agent._build_report_context(
            query="AI行业发展前景",
            report_storage=storage,
            report_ids=None,
        )
        
        # 应返回上下文和来源列表
        assert isinstance(context, str)
        assert isinstance(sources, list)
        
        # 如果有结果，检查格式
        if sources:
            assert "id" in sources[0]
            assert "title" in sources[0]

    def test_build_enhanced_prompt(self):
        """增强 Prompt 格式正确"""
        import importlib
        import config
        importlib.reload(config)
        from agent import CoPawAgent
        
        agent = CoPawAgent()
        
        prompt = agent._build_enhanced_prompt(
            query="AI行业怎么样",
            context_text="【研报：AI报告】\nAI行业很好",
        )
        
        # 检查 Prompt 包含必要元素
        assert "AI行业怎么样" in prompt
        assert "研报" in prompt
        assert "AI报告" in prompt
        assert "AI行业很好" in prompt


# ── API 端点集成测试 ──────────────────────────────────────────────────────────

class TestAskWithReportsAPI:

    def test_ask_without_reports_backward_compat(self, client):
        """不使用研报增强时，行为与原来一致（向后兼容）"""
        # 创建会话
        resp = client.post("/api/v1/agent/sessions", json={"title": "test"})
        session_id = resp.get_json()["session"]["id"]
        
        # 发送不带 use_reports 的请求
        resp = client.post("/api/v1/agent/ask", json={
            "query": "测试问题",
            "session_id": session_id,
        })
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert "answer" in data
        assert "sources" in data  # 新增字段
        assert isinstance(data["sources"], list)

    def test_ask_with_reports_no_report_storage(self, client):
        """启用研报增强但无 report_storage 时正常降级"""
        # 创建会话
        resp = client.post("/api/v1/agent/sessions", json={"title": "test"})
        session_id = resp.get_json()["session"]["id"]
        
        # 发送带 use_reports=True 的请求
        resp = client.post("/api/v1/agent/ask", json={
            "query": "AI行业发展如何",
            "session_id": session_id,
            "use_reports": True,
        })
        
        # 应正常返回，只是 sources 为空
        assert resp.status_code == 200
        data = resp.get_json()
        assert "answer" in data
        assert "sources" in data
        assert isinstance(data["sources"], list)

    def test_ask_with_invalid_report_ids(self, client):
        """report_ids 格式错误时返回 400"""
        # 创建会话
        resp = client.post("/api/v1/agent/sessions", json={"title": "test"})
        session_id = resp.get_json()["session"]["id"]
        
        # 发送格式错误的 report_ids
        resp = client.post("/api/v1/agent/ask", json={
            "query": "测试问题",
            "session_id": session_id,
            "use_reports": True,
            "report_ids": ["invalid_id"],  # 格式不正确
        })
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_ID"

    def test_ask_with_report_ids_not_array(self, client):
        """report_ids 不是数组时返回 400"""
        # 创建会话
        resp = client.post("/api/v1/agent/sessions", json={"title": "test"})
        session_id = resp.get_json()["session"]["id"]
        
        # 发送非数组的 report_ids
        resp = client.post("/api/v1/agent/ask", json={
            "query": "测试问题",
            "session_id": session_id,
            "use_reports": True,
            "report_ids": "not_an_array",
        })
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_QUERY"


# ── 端到端测试 ────────────────────────────────────────────────────────────────

class TestEndToEnd:

    def test_full_flow_with_reports(self, tmp_path):
        """端到端：上传研报 → 基于研报提问"""
        from wsgi import create_app
        from report_storage import ReportStorage
        
        # 创建带研报存储的应用
        app = create_app(data_dir=str(tmp_path / "data"))
        app.config["TESTING"] = True
        
        # 手动创建研报存储并添加数据
        report_storage = ReportStorage(str(tmp_path / "data"))
        ts = int(time.time() * 1000)
        report_storage.create_report({
            "id": f"rpt_{ts}",
            "title": "AI行业研究报告",
            "filename": "ai.pdf",
            "file_path": f"report_files/ai.pdf",
            "file_size": 1024,
            "file_type": "pdf",
            "text_content": "AI行业正在高速发展，市场规模预计三年翻倍。",
            "text_length": 25,
            "upload_time": "2026-04-15T00:00:00+00:00",
            "status": "ready",
            "metadata": {},
        })
        
        # 将 report_storage 注入到 app
        app.report_storage = report_storage
        
        client = app.test_client()
        
        # 创建会话
        resp = client.post("/api/v1/agent/sessions", json={"title": "test"})
        session_id = resp.get_json()["session"]["id"]
        
        # 使用研报增强提问
        resp = client.post("/api/v1/agent/ask", json={
            "query": "AI行业发展怎么样",
            "session_id": session_id,
            "use_reports": True,
        })
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert "answer" in data
        assert "sources" in data
        # 由于有匹配的研报，sources 应该非空
        assert len(data["sources"]) >= 1
        assert data["sources"][0]["title"] == "AI行业研究报告"

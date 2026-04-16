"""
M1-QA 研报功能 API 集成测试
覆盖: report_bp.py 6 个端点 + report_storage.py + report_parser.py
"""
import io
import json
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def tmp_report_storage(tmp_path):
    """使用临时目录创建 ReportStorage 实例"""
    from report_storage import ReportStorage
    return ReportStorage(str(tmp_path / "data"))


@pytest.fixture
def sample_report(tmp_report_storage):
    """预置一条研报记录"""
    ts = int(time.time() * 1000)
    record = {
        "id": f"rpt_{ts}",
        "title": "2024年AI行业深度研究报告",
        "filename": "ai_report_2024.pdf",
        "file_path": f"report_files/2026/04/rpt_{ts}.pdf",
        "file_size": 1024,
        "file_type": "pdf",
        "text_content": "AI行业正处于高速增长阶段，预计未来三年翻倍。",
        "text_length": 25,
        "upload_time": "2026-04-15T08:30:00.000000+00:00",
        "status": "ready",
        "metadata": {"pages": 10, "author": None, "word_count": 25},
    }
    tmp_report_storage.create_report(record)
    return record, tmp_report_storage


@pytest.fixture
def two_reports(tmp_report_storage):
    """预置两条研报记录，用于对比测试"""
    ts1 = int(time.time() * 1000)
    ts2 = ts1 + 1
    r1 = {
        "id": f"rpt_{ts1}",
        "title": "2024年AI行业深度研究报告",
        "filename": "ai_report.pdf",
        "file_path": f"report_files/2026/04/rpt_{ts1}.pdf",
        "file_size": 1024,
        "file_type": "pdf",
        "text_content": "AI行业增速强劲，估值偏高。",
        "text_length": 14,
        "upload_time": "2026-04-15T08:30:00.000000+00:00",
        "status": "ready",
        "metadata": {"pages": 5, "author": None, "word_count": 14},
    }
    r2 = {
        "id": f"rpt_{ts2}",
        "title": "2024年半导体行业分析报告",
        "filename": "semi_report.pdf",
        "file_path": f"report_files/2026/04/rpt_{ts2}.pdf",
        "file_size": 2048,
        "file_type": "pdf",
        "text_content": "半导体行业库存周期见顶，增速放缓。",
        "text_length": 18,
        "upload_time": "2026-04-15T08:31:00.000000+00:00",
        "status": "ready",
        "metadata": {"pages": 8, "author": None, "word_count": 18},
    }
    tmp_report_storage.create_report(r1)
    tmp_report_storage.create_report(r2)
    return r1, r2, tmp_report_storage


# ── ReportStorage 单元测试 ──────────────────────────────────────────────────

class TestReportStorage:

    def test_create_and_get_report(self, tmp_report_storage):
        """创建研报并按 ID 查询"""
        ts = int(time.time() * 1000)
        record = {
            "id": f"rpt_{ts}",
            "title": "测试报告",
            "filename": "test.pdf",
            "file_path": "report_files/2026/04/test.pdf",
            "file_size": 512,
            "file_type": "pdf",
            "text_content": "测试内容",
            "text_length": 4,
            "upload_time": "2026-04-15T00:00:00+00:00",
            "status": "ready",
            "metadata": {},
        }
        created = tmp_report_storage.create_report(record)
        assert created["id"] == record["id"]

        fetched = tmp_report_storage.get_report_by_id(record["id"])
        assert fetched is not None
        assert fetched["title"] == "测试报告"

    def test_get_report_not_found(self, tmp_report_storage):
        """查询不存在的研报返回 None"""
        result = tmp_report_storage.get_report_by_id("rpt_9999999999999")
        assert result is None

    def test_get_reports_pagination(self, tmp_report_storage):
        """分页查询：验证 total 和 items"""
        # 写入 3 条记录
        for i in range(3):
            ts = int(time.time() * 1000) + i
            tmp_report_storage.create_report({
                "id": f"rpt_{ts}",
                "title": f"报告{i}",
                "filename": f"r{i}.pdf",
                "file_path": f"report_files/2026/04/rpt_{ts}.pdf",
                "file_size": 100,
                "file_type": "pdf",
                "text_content": "",
                "text_length": 0,
                "upload_time": "2026-04-15T00:00:00+00:00",
                "status": "ready",
                "metadata": {},
            })

        result = tmp_report_storage.get_reports(page=1, page_size=2)
        assert result["total"] == 3
        assert len(result["items"]) == 2

        result_p2 = tmp_report_storage.get_reports(page=2, page_size=2)
        assert len(result_p2["items"]) == 1

    def test_get_reports_status_filter(self, tmp_report_storage):
        """状态过滤：只返回 ready 状态的记录"""
        ts1 = int(time.time() * 1000)
        ts2 = ts1 + 1
        tmp_report_storage.create_report({
            "id": f"rpt_{ts1}", "title": "A", "filename": "a.pdf",
            "file_path": "", "file_size": 0, "file_type": "pdf",
            "text_content": "", "text_length": 0,
            "upload_time": "2026-01-01T00:00:00+00:00",
            "status": "ready", "metadata": {},
        })
        tmp_report_storage.create_report({
            "id": f"rpt_{ts2}", "title": "B", "filename": "b.pdf",
            "file_path": "", "file_size": 0, "file_type": "pdf",
            "text_content": "", "text_length": 0,
            "upload_time": "2026-01-01T00:00:01+00:00",
            "status": "error", "metadata": {},
        })

        ready = tmp_report_storage.get_reports(status="ready")
        assert ready["total"] == 1
        assert ready["items"][0]["status"] == "ready"

    def test_delete_report(self, sample_report):
        """删除研报后不可再查到"""
        record, storage = sample_report
        deleted = storage.delete_report(record["id"])
        assert deleted["id"] == record["id"]
        assert storage.get_report_by_id(record["id"]) is None

    def test_delete_report_not_found(self, tmp_report_storage):
        """删除不存在的研报抛出 KeyError"""
        with pytest.raises(KeyError):
            tmp_report_storage.delete_report("rpt_9999999999999")

    def test_create_and_get_compare(self, tmp_report_storage):
        """创建对比报告并按 ID 查询"""
        ts = int(time.time() * 1000)
        compare_record = {
            "id": f"cmp_{ts}",
            "report_ids": ["rpt_1111111111111", "rpt_2222222222222"],
            "report_titles": ["报告A", "报告B"],
            "focus_areas": ["行业趋势"],
            "compare_result": {
                "summary": "测试总结",
                "differences": [],
                "commonalities": [],
                "recommendation": "测试建议",
            },
            "llm_used": False,
            "model": None,
            "response_time_ms": 100,
            "create_time": "2026-04-15T08:35:00+00:00",
        }
        tmp_report_storage.create_compare(compare_record)
        fetched = tmp_report_storage.get_compare_by_id(f"cmp_{ts}")
        assert fetched is not None
        assert fetched["report_titles"] == ["报告A", "报告B"]

    def test_get_compare_not_found(self, tmp_report_storage):
        """查询不存在的对比报告返回 None"""
        result = tmp_report_storage.get_compare_by_id("cmp_9999999999999")
        assert result is None


# ── 文件上传 API 测试 ──────────────────────────────────────────────────────────

class TestUploadReportAPI:

    def test_upload_no_file(self, client):
        """未传文件 → 400 EMPTY_FILE"""
        resp = client.post("/api/v1/agent/reports/upload")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "EMPTY_FILE"
        assert "traceId" in data["error"]

    def test_upload_invalid_type(self, client):
        """上传不支持的文件类型 → 400 INVALID_FILE_TYPE"""
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(b"hello"), "test.txt", "text/plain")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"

    def test_upload_file_too_large(self, client):
        """上传超大文件 → 400 FILE_TOO_LARGE"""
        # 生成 11MB 数据（超过默认 10MB 限制）
        big_data = b"x" * (11 * 1024 * 1024)
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(big_data), "big.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "FILE_TOO_LARGE"

    def test_upload_empty_filename(self, client):
        """空文件名 → 400 EMPTY_FILENAME"""
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(b"content"), "", "application/pdf")},
            content_type="multipart/form-data",
        )
        # 空文件名会被 Werkzeug 过滤，触发 EMPTY_FILE 或 EMPTY_FILENAME
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] in ("EMPTY_FILE", "EMPTY_FILENAME")


# ── 研报列表 API 测试 ──────────────────────────────────────────────────────────

class TestListReportsAPI:

    def test_list_reports_empty(self, client):
        """空列表返回 200，研报数组为空"""
        resp = client.get("/api/v1/agent/reports/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["reports"] == []
        assert data["pagination"]["total"] == 0

    def test_list_reports_invalid_page(self, client):
        """非整数 page 参数 → 400"""
        resp = client.get("/api/v1/agent/reports/?page=abc")
        assert resp.status_code == 400

    def test_list_reports_invalid_status(self, client):
        """非法 status 参数 → 400"""
        resp = client.get("/api/v1/agent/reports/?status=invalid")
        assert resp.status_code == 400

    def test_list_reports_no_text_content(self, client, app):
        """列表接口不返回 text_content 字段"""
        # 直接写入一条研报到 app 的 report_storage
        ts = int(time.time() * 1000)
        with app.app_context():
            app.report_storage.create_report({
                "id": f"rpt_{ts}",
                "title": "测试报告",
                "filename": "test.pdf",
                "file_path": f"report_files/2026/04/rpt_{ts}.pdf",
                "file_size": 512,
                "file_type": "pdf",
                "text_content": "这段内容不应该出现在列表接口",
                "text_length": 15,
                "upload_time": "2026-04-15T00:00:00+00:00",
                "status": "ready",
                "metadata": {},
            })

        resp = client.get("/api/v1/agent/reports/")
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["reports"]) == 1
        assert "text_content" not in data["reports"][0]  # 列表不含 text_content


# ── 研报详情 API 测试 ──────────────────────────────────────────────────────────

class TestGetReportAPI:

    def test_get_report_invalid_id(self, client):
        """非法 ID 格式 → 400 INVALID_REPORT_ID"""
        resp = client.get("/api/v1/agent/reports/invalid-id")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_ID"

    def test_get_report_not_found(self, client):
        """不存在的研报 → 404 REPORT_NOT_FOUND"""
        resp = client.get("/api/v1/agent/reports/rpt_9999999999999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "REPORT_NOT_FOUND"

    def test_get_report_success(self, client, app):
        """成功获取研报详情，含 text_content"""
        ts = int(time.time() * 1000)
        report_id = f"rpt_{ts}"
        with app.app_context():
            app.report_storage.create_report({
                "id": report_id,
                "title": "详情测试报告",
                "filename": "detail.pdf",
                "file_path": f"report_files/2026/04/{report_id}.pdf",
                "file_size": 1024,
                "file_type": "pdf",
                "text_content": "详情内容文本",
                "text_length": 6,
                "upload_time": "2026-04-15T00:00:00+00:00",
                "status": "ready",
                "metadata": {"pages": 1, "author": None, "word_count": 6},
            })

        resp = client.get(f"/api/v1/agent/reports/{report_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["report"]["id"] == report_id
        assert data["report"]["text_content"] == "详情内容文本"
        assert "metadata" in data["report"]


# ── 删除研报 API 测试 ──────────────────────────────────────────────────────────

class TestDeleteReportAPI:

    def test_delete_report_invalid_id(self, client):
        """非法 ID → 400 INVALID_REPORT_ID"""
        resp = client.delete("/api/v1/agent/reports/bad_id_format")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_ID"

    def test_delete_report_not_found(self, client):
        """删除不存在的研报 → 404"""
        resp = client.delete("/api/v1/agent/reports/rpt_9999999999999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "REPORT_NOT_FOUND"

    def test_delete_report_success(self, client, app):
        """成功删除研报，再查询返回 404"""
        ts = int(time.time() * 1000)
        report_id = f"rpt_{ts}"
        with app.app_context():
            app.report_storage.create_report({
                "id": report_id,
                "title": "待删报告",
                "filename": "del.pdf",
                "file_path": f"report_files/2026/04/{report_id}.pdf",
                "file_size": 512,
                "file_type": "pdf",
                "text_content": "",
                "text_length": 0,
                "upload_time": "2026-04-15T00:00:00+00:00",
                "status": "ready",
                "metadata": {},
            })

        resp = client.delete(f"/api/v1/agent/reports/{report_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["deleted_id"] == report_id

        # 再次查询应返回 404
        resp2 = client.get(f"/api/v1/agent/reports/{report_id}")
        assert resp2.status_code == 404


# ── 对比分析 API 测试 ──────────────────────────────────────────────────────────

class TestCompareReportsAPI:

    def _seed_two_reports(self, app):
        """向 app 中预置两条研报"""
        ts1 = int(time.time() * 1000)
        ts2 = ts1 + 1
        id1 = f"rpt_{ts1}"
        id2 = f"rpt_{ts2}"
        with app.app_context():
            for rid, title, content in [
                (id1, "AI行业报告", "AI行业增速强劲。"),
                (id2, "半导体行业报告", "半导体库存周期见顶。"),
            ]:
                app.report_storage.create_report({
                    "id": rid,
                    "title": title,
                    "filename": f"{rid}.pdf",
                    "file_path": f"report_files/2026/04/{rid}.pdf",
                    "file_size": 512,
                    "file_type": "pdf",
                    "text_content": content,
                    "text_length": len(content),
                    "upload_time": "2026-04-15T00:00:00+00:00",
                    "status": "ready",
                    "metadata": {},
                })
        return id1, id2

    def test_compare_invalid_count(self, client):
        """report_ids 数量不为 2 → 400 INVALID_REPORT_COUNT"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["rpt_1111111111111"]},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_COUNT"

    def test_compare_invalid_id_format(self, client):
        """非法 ID 格式 → 400 INVALID_REPORT_ID"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["invalid", "rpt_1111111111111"]},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_ID"

    def test_compare_duplicate_ids(self, client):
        """两个相同 ID → 400 DUPLICATE_REPORT"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["rpt_1111111111111", "rpt_1111111111111"]},
        )
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "DUPLICATE_REPORT"

    def test_compare_report_not_found(self, client):
        """研报不存在 → 404 REPORT_NOT_FOUND"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["rpt_1111111111111", "rpt_2222222222222"]},
        )
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "REPORT_NOT_FOUND"

    def test_compare_success(self, client, app):
        """成功对比两份研报，返回 compare 对象"""
        id1, id2 = self._seed_two_reports(app)

        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={
                "report_ids": [id1, id2],
                "focus_areas": ["行业趋势"],
            },
        )
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        compare = data["compare"]
        assert "id" in compare
        assert compare["id"].startswith("cmp_")
        assert compare["report_ids"] == [id1, id2]
        assert "compare_result" in compare
        assert "summary" in compare["compare_result"]
        assert "differences" in compare["compare_result"]
        assert "commonalities" in compare["compare_result"]
        assert "recommendation" in compare["compare_result"]
        assert isinstance(compare["llm_used"], bool)
        assert "response_time_ms" in compare

    def test_compare_focus_areas_limit(self, client, app):
        """focus_areas 超过 5 个时自动截断"""
        id1, id2 = self._seed_two_reports(app)

        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={
                "report_ids": [id1, id2],
                "focus_areas": ["A", "B", "C", "D", "E", "F", "G"],  # 7个，超出限制
            },
        )
        assert resp.status_code == 200
        compare = resp.get_json()["compare"]
        # 只保留前 5 个
        assert len(compare["focus_areas"]) <= 5


# ── 对比报告详情 API 测试 ──────────────────────────────────────────────────────

class TestGetCompareAPI:

    def test_get_compare_invalid_id(self, client):
        """非法 compare_id 格式 → 400 INVALID_COMPARE_ID"""
        resp = client.get("/api/v1/agent/reports/compare/not-valid-id")
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_COMPARE_ID"

    def test_get_compare_not_found(self, client):
        """不存在的对比报告 → 404 COMPARE_NOT_FOUND"""
        resp = client.get("/api/v1/agent/reports/compare/cmp_9999999999999")
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "COMPARE_NOT_FOUND"

    def test_get_compare_success(self, client, app):
        """成功获取对比报告详情"""
        ts = int(time.time() * 1000)
        cmp_id = f"cmp_{ts}"
        with app.app_context():
            app.report_storage.create_compare({
                "id": cmp_id,
                "report_ids": ["rpt_1111111111111", "rpt_2222222222222"],
                "report_titles": ["报告A", "报告B"],
                "focus_areas": ["行业趋势"],
                "compare_result": {
                    "summary": "总结",
                    "differences": [],
                    "commonalities": [],
                    "recommendation": "建议",
                },
                "llm_used": False,
                "model": None,
                "response_time_ms": 100,
                "create_time": "2026-04-15T08:35:00+00:00",
            })

        resp = client.get(f"/api/v1/agent/reports/compare/{cmp_id}")
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["compare"]["id"] == cmp_id
        assert data["compare"]["report_titles"] == ["报告A", "报告B"]


# ── report_parser 单元测试 ──────────────────────────────────────────────────

class TestReportParser:

    def test_extract_unsupported_type(self):
        """不支持的文件类型抛出 ValueError"""
        from report_parser import extract_text
        with pytest.raises(ValueError, match="不支持的文件类型"):
            extract_text("/fake/path/file.xxx", "txt")

    def test_extract_pdf_not_exists(self):
        """不存在的 PDF 文件抛出异常"""
        from report_parser import extract_text_from_pdf
        with pytest.raises(Exception):
            extract_text_from_pdf("/non/existent/file.pdf")

    def test_extract_docx_not_exists(self):
        """不存在的 DOCX 文件抛出异常"""
        from report_parser import extract_text_from_docx
        with pytest.raises(Exception):
            extract_text_from_docx("/non/existent/file.docx")


# ── agent.compare_reports Demo 模式测试 ───────────────────────────────────────

class TestAgentCompareReports:

    def test_compare_demo_mode(self):
        """compare_reports 应返回合法结构（无论 LLM 是否可用）"""
        from agent import CoPawAgent
        agent = CoPawAgent()
        report_a = {"title": "报告A", "text_content": "内容A"}
        report_b = {"title": "报告B", "text_content": "内容B"}

        result = agent.compare_reports(report_a, report_b, [])

        assert "compare_result" in result
        assert "llm_used" in result
        assert isinstance(result["llm_used"], bool)
        assert "response_time_ms" in result
        assert isinstance(result["response_time_ms"], int)
        # compare_result 必须包含指定字段
        cr = result["compare_result"]
        assert "summary" in cr
        assert "differences" in cr
        assert "commonalities" in cr
        assert "recommendation" in cr

    def test_truncate_text(self):
        """文本截断：超过长度时保留首尾"""
        from agent import CoPawAgent
        long_text = "A" * 1000
        truncated = CoPawAgent._truncate_text(long_text, 100)
        assert len(truncated) < len(long_text)
        assert "中间部分已省略" in truncated

    def test_truncate_text_short(self):
        """短文本不截断"""
        from agent import CoPawAgent
        short_text = "短文本"
        result = CoPawAgent._truncate_text(short_text, 100)
        assert result == short_text

    def test_parse_compare_json_valid(self):
        """解析合法 JSON 对比结果"""
        from agent import CoPawAgent
        valid_json = json.dumps({
            "summary": "测试总结",
            "differences": [{"aspect": "趋势", "report_a_view": "A", "report_b_view": "B", "analysis": "差异"}],
            "commonalities": ["共识1"],
            "recommendation": "建议",
        })
        result = CoPawAgent._parse_compare_json(valid_json)
        assert result["summary"] == "测试总结"
        assert len(result["differences"]) == 1
        assert result["commonalities"] == ["共识1"]

    def test_parse_compare_json_invalid(self):
        """解析非法 JSON 时返回备用结构"""
        from agent import CoPawAgent
        result = CoPawAgent._parse_compare_json("这不是JSON内容，是普通文本。")
        assert "summary" in result
        assert "differences" in result
        assert "commonalities" in result
        assert "recommendation" in result

    def test_parse_compare_json_with_markdown(self):
        """解析带 Markdown 代码块的 JSON"""
        from agent import CoPawAgent
        text = '```json\n{"summary": "总结", "differences": [], "commonalities": [], "recommendation": "建议"}\n```'
        result = CoPawAgent._parse_compare_json(text)
        assert result["summary"] == "总结"

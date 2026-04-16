# -*- coding: utf-8 -*-
"""
M1-QA 研报功能集成测试（使用真实测试 PDF 文件）
覆盖: 完整的文件上传 → 解析 → 列表 → 详情 → 对比 → 删除流程
"""
import io
import os
import sys
import time

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# 测试 PDF 文件目录
TEST_REPORTS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "test_reports")


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def test_pdf_paths():
    """获取测试 PDF 文件路径"""
    return {
        "semiconductor": os.path.join(TEST_REPORTS_DIR, "test_report_semiconductor_2024.pdf"),
        "newenergy": os.path.join(TEST_REPORTS_DIR, "test_report_newenergy_2024.pdf"),
        "ai": os.path.join(TEST_REPORTS_DIR, "test_report_ai_2024.pdf"),
    }


@pytest.fixture
def sample_pdf_bytes(test_pdf_paths):
    """读取测试 PDF 文件为字节流"""
    with open(test_pdf_paths["semiconductor"], "rb") as f:
        return f.read()


# ── 文件上传 API 集成测试 ──────────────────────────────────────────────────────

class TestUploadReportIntegration:
    """文件上传 API 集成测试（使用真实 PDF 文件）"""

    def test_upload_pdf_success(self, client, test_pdf_paths):
        """上传真实 PDF 文件成功"""
        # 读取真实测试 PDF
        with open(test_pdf_paths["semiconductor"], "rb") as f:
            pdf_bytes = f.read()
        
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={
                "file": (io.BytesIO(pdf_bytes), "test_report_semiconductor_2024.pdf", "application/pdf"),
                "title": "半导体行业研报"
            },
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 201
        data = resp.get_json()
        assert "traceId" in data
        assert "report" in data
        
        report = data["report"]
        assert report["title"] == "半导体行业研报"
        assert report["file_type"] == "pdf"
        assert report["status"] == "ready"
        assert report["file_size"] > 0
        assert report["text_length"] > 0  # 真实 PDF 应该能提取出文本
        assert "text_content" in report
        assert len(report["text_content"]) > 0  # 文本内容不为空
        assert report["id"].startswith("rpt_")

    def test_upload_pdf_with_default_title(self, client, test_pdf_paths):
        """上传 PDF 不传标题，默认使用文件名"""
        with open(test_pdf_paths["ai"], "rb") as f:
            pdf_bytes = f.read()
        
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={
                "file": (io.BytesIO(pdf_bytes), "test_report_ai_2024.pdf", "application/pdf")
            },
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 201
        report = resp.get_json()["report"]
        # 默认标题应为文件名（去掉扩展名）
        assert "test_report_ai_2024" in report["title"]

    def test_upload_invalid_file_type(self, client):
        """上传不支持的文件类型返回 400"""
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={
                "file": (io.BytesIO(b"hello world"), "test.txt", "text/plain")
            },
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_FILE_TYPE"
        assert "PDF" in data["error"]["message"] or "DOCX" in data["error"]["message"]

    def test_upload_file_too_large(self, client):
        """上传超大文件返回 400"""
        # 生成 11MB 数据（超过默认 10MB 限制）
        big_data = b"x" * (11 * 1024 * 1024)
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={
                "file": (io.BytesIO(big_data), "big_report.pdf", "application/pdf")
            },
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "FILE_TOO_LARGE"

    def test_upload_no_file(self, client):
        """未传文件返回 400"""
        resp = client.post("/api/v1/agent/reports/upload")
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "EMPTY_FILE"

    def test_upload_empty_filename(self, client):
        """空文件名返回 400"""
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={
                "file": (io.BytesIO(b"content"), "", "application/pdf")
            },
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] in ("EMPTY_FILE", "EMPTY_FILENAME")


# ── 研报列表 API 集成测试 ──────────────────────────────────────────────────────

class TestListReportsIntegration:
    """研报列表 API 集成测试"""

    def test_list_empty(self, client):
        """空列表返回空数组"""
        resp = client.get("/api/v1/agent/reports/")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["reports"] == []
        assert data["pagination"]["total"] == 0
        assert data["pagination"]["page"] == 1

    def test_list_with_data(self, client, test_pdf_paths):
        """有数据列表返回正确"""
        # 上传两份研报
        with open(test_pdf_paths["semiconductor"], "rb") as f:
            pdf1 = f.read()
        with open(test_pdf_paths["newenergy"], "rb") as f:
            pdf2 = f.read()
        
        client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf1), "semiconductor.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf2), "newenergy.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        
        resp = client.get("/api/v1/agent/reports/")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data["reports"]) >= 2
        assert data["pagination"]["total"] >= 2
        
        # 列表项不应包含 text_content
        for r in data["reports"]:
            assert "text_content" not in r
            assert "id" in r
            assert "title" in r
            assert "file_size" in r

    def test_list_pagination(self, client, test_pdf_paths):
        """分页参数生效"""
        # 上传 3 份研报
        for name, path in test_pdf_paths.items():
            with open(path, "rb") as f:
                pdf = f.read()
            client.post(
                "/api/v1/agent/reports/upload",
                data={"file": (io.BytesIO(pdf), f"{name}.pdf", "application/pdf")},
                content_type="multipart/form-data",
            )
        
        # 请求第一页，每页 2 条
        resp = client.get("/api/v1/agent/reports/?page=1&page_size=2")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["page_size"] == 2
        assert len(data["reports"]) <= 2

    def test_list_status_filter(self, client, app):
        """状态过滤生效"""
        # 直接写入一条 error 状态的研报
        ts = int(time.time() * 1000)
        with app.app_context():
            app.report_storage.create_report({
                "id": f"rpt_{ts}",
                "title": "错误研报",
                "filename": "error.pdf",
                "file_path": f"report_files/2026/04/rpt_{ts}.pdf",
                "file_size": 0,
                "file_type": "pdf",
                "text_content": "",
                "text_length": 0,
                "upload_time": "2026-04-15T00:00:00+00:00",
                "status": "error",
                "metadata": {},
            })
        
        resp = client.get("/api/v1/agent/reports/?status=error")
        
        assert resp.status_code == 200
        data = resp.get_json()
        for r in data["reports"]:
            assert r["status"] == "error"

    def test_list_invalid_page(self, client):
        """非法分页参数返回 400"""
        resp = client.get("/api/v1/agent/reports/?page=abc")
        
        assert resp.status_code == 400
        assert resp.get_json()["error"]["code"] == "INVALID_QUERY"


# ── 研报详情 API 集成测试 ──────────────────────────────────────────────────────

class TestGetReportIntegration:
    """研报详情 API 集成测试"""

    def test_get_report_success(self, client, test_pdf_paths):
        """成功获取研报详情，包含完整文本内容"""
        # 上传研报
        with open(test_pdf_paths["semiconductor"], "rb") as f:
            pdf = f.read()
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf), "semiconductor.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        report_id = resp.get_json()["report"]["id"]
        
        # 获取详情
        resp = client.get(f"/api/v1/agent/reports/{report_id}")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        report = data["report"]
        assert report["id"] == report_id
        assert "text_content" in report
        assert len(report["text_content"]) > 0  # 应包含完整文本
        assert "metadata" in report

    def test_get_report_not_found(self, client):
        """研报不存在返回 404"""
        resp = client.get("/api/v1/agent/reports/rpt_9999999999999")
        
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "REPORT_NOT_FOUND"

    def test_get_report_invalid_id(self, client):
        """非法 ID 格式返回 400"""
        resp = client.get("/api/v1/agent/reports/invalid-id-format")
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_ID"


# ── 删除研报 API 集成测试 ──────────────────────────────────────────────────────

class TestDeleteReportIntegration:
    """删除研报 API 集成测试"""

    def test_delete_report_success(self, client, test_pdf_paths):
        """成功删除研报"""
        # 上传研报
        with open(test_pdf_paths["ai"], "rb") as f:
            pdf = f.read()
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf), "ai_report.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        report_id = resp.get_json()["report"]["id"]
        
        # 删除研报
        resp = client.delete(f"/api/v1/agent/reports/{report_id}")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["deleted_id"] == report_id
        
        # 再次查询应返回 404
        resp2 = client.get(f"/api/v1/agent/reports/{report_id}")
        assert resp2.status_code == 404

    def test_delete_report_not_found(self, client):
        """删除不存在的研报返回 404"""
        resp = client.delete("/api/v1/agent/reports/rpt_9999999999999")
        
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "REPORT_NOT_FOUND"

    def test_delete_report_invalid_id(self, client):
        """非法 ID 格式返回 400"""
        resp = client.delete("/api/v1/agent/reports/bad-id")
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_ID"


# ── 对比分析 API 集成测试 ──────────────────────────────────────────────────────

class TestCompareReportsIntegration:
    """对比分析 API 集成测试"""

    def _upload_two_reports(self, client, test_pdf_paths):
        """上传两份研报并返回 ID"""
        with open(test_pdf_paths["semiconductor"], "rb") as f:
            pdf1 = f.read()
        with open(test_pdf_paths["newenergy"], "rb") as f:
            pdf2 = f.read()
        
        resp1 = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf1), "semi.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        resp2 = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf2), "newenergy.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        
        id1 = resp1.get_json()["report"]["id"]
        id2 = resp2.get_json()["report"]["id"]
        return id1, id2

    def test_compare_success(self, client, test_pdf_paths):
        """成功对比两份研报"""
        id1, id2 = self._upload_two_reports(client, test_pdf_paths)
        
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={
                "report_ids": [id1, id2],
                "focus_areas": ["行业趋势", "投资建议"],
            },
        )
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        
        compare = data["compare"]
        assert compare["id"].startswith("cmp_")
        assert compare["report_ids"] == [id1, id2]
        assert len(compare["report_titles"]) == 2
        
        # 验证对比结果结构
        result = compare["compare_result"]
        assert "summary" in result
        assert "differences" in result
        assert "commonalities" in result
        assert "recommendation" in result
        
        # 验证响应时间记录
        assert "response_time_ms" in compare
        assert isinstance(compare["response_time_ms"], int)

    def test_compare_missing_report_ids(self, client):
        """缺少 report_ids 参数返回 400"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"focus_areas": ["行业趋势"]},
        )
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_COUNT"

    def test_compare_invalid_count(self, client):
        """report_ids 数量不为 2 返回 400"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["rpt_1111111111111"]},
        )
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_COUNT"

    def test_compare_invalid_id_format(self, client):
        """非法 ID 格式返回 400"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["invalid-id", "rpt_1111111111111"]},
        )
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_REPORT_ID"

    def test_compare_duplicate_ids(self, client):
        """重复 ID 返回 400"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["rpt_1111111111111", "rpt_1111111111111"]},
        )
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "DUPLICATE_REPORT"

    def test_compare_report_not_found(self, client):
        """研报不存在返回 404"""
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": ["rpt_1111111111111", "rpt_2222222222222"]},
        )
        
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "REPORT_NOT_FOUND"

    def test_compare_focus_areas_limit(self, client, test_pdf_paths):
        """关注点超过 5 个自动截断"""
        id1, id2 = self._upload_two_reports(client, test_pdf_paths)
        
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={
                "report_ids": [id1, id2],
                "focus_areas": ["A", "B", "C", "D", "E", "F", "G"],  # 7 个
            },
        )
        
        assert resp.status_code == 200
        compare = resp.get_json()["compare"]
        assert len(compare["focus_areas"]) <= 5


# ── 对比报告详情 API 集成测试 ──────────────────────────────────────────────────

class TestGetCompareIntegration:
    """对比报告详情 API 集成测试"""

    def test_get_compare_success(self, client, test_pdf_paths):
        """成功获取对比报告详情"""
        # 上传两份研报
        with open(test_pdf_paths["semiconductor"], "rb") as f:
            pdf1 = f.read()
        with open(test_pdf_paths["ai"], "rb") as f:
            pdf2 = f.read()
        
        resp1 = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf1), "semi.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        resp2 = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf2), "ai.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        
        id1 = resp1.get_json()["report"]["id"]
        id2 = resp2.get_json()["report"]["id"]
        
        # 执行对比
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={"report_ids": [id1, id2]},
        )
        compare_id = resp.get_json()["compare"]["id"]
        
        # 获取对比报告详情
        resp = client.get(f"/api/v1/agent/reports/compare/{compare_id}")
        
        assert resp.status_code == 200
        data = resp.get_json()
        assert "traceId" in data
        assert data["compare"]["id"] == compare_id
        assert data["compare"]["report_ids"] == [id1, id2]

    def test_get_compare_not_found(self, client):
        """对比报告不存在返回 404"""
        resp = client.get("/api/v1/agent/reports/compare/cmp_9999999999999")
        
        assert resp.status_code == 404
        data = resp.get_json()
        assert data["error"]["code"] == "COMPARE_NOT_FOUND"

    def test_get_compare_invalid_id(self, client):
        """非法 ID 格式返回 400"""
        resp = client.get("/api/v1/agent/reports/compare/not-valid-id")
        
        assert resp.status_code == 400
        data = resp.get_json()
        assert data["error"]["code"] == "INVALID_COMPARE_ID"


# ── 端到端流程测试 ──────────────────────────────────────────────────────────────

class TestReportE2E:
    """端到端流程测试：上传 → 列表 → 详情 → 对比 → 删除"""

    def test_full_workflow(self, client, test_pdf_paths):
        """完整的研报工作流程"""
        # 1. 上传三份研报
        uploaded_ids = []
        for name, path in test_pdf_paths.items():
            with open(path, "rb") as f:
                pdf = f.read()
            resp = client.post(
                "/api/v1/agent/reports/upload",
                data={"file": (io.BytesIO(pdf), f"{name}.pdf", "application/pdf")},
                content_type="multipart/form-data",
            )
            assert resp.status_code == 201
            uploaded_ids.append(resp.get_json()["report"]["id"])
        
        # 2. 查看列表
        resp = client.get("/api/v1/agent/reports/")
        assert resp.status_code == 200
        assert resp.get_json()["pagination"]["total"] >= 3
        
        # 3. 查看详情
        for rid in uploaded_ids:
            resp = client.get(f"/api/v1/agent/reports/{rid}")
            assert resp.status_code == 200
            assert len(resp.get_json()["report"]["text_content"]) > 0
        
        # 4. 执行对比
        resp = client.post(
            "/api/v1/agent/reports/compare",
            json={
                "report_ids": [uploaded_ids[0], uploaded_ids[1]],
                "focus_areas": ["行业趋势", "投资建议"],
            },
        )
        assert resp.status_code == 200
        compare_id = resp.get_json()["compare"]["id"]
        
        # 5. 查看对比报告详情
        resp = client.get(f"/api/v1/agent/reports/compare/{compare_id}")
        assert resp.status_code == 200
        
        # 6. 删除所有研报
        for rid in uploaded_ids:
            resp = client.delete(f"/api/v1/agent/reports/{rid}")
            assert resp.status_code == 200
            assert resp.get_json()["deleted_id"] == rid
        
        # 7. 再次查看列表确认删除
        resp = client.get("/api/v1/agent/reports/")
        reports = resp.get_json()["reports"]
        for rid in uploaded_ids:
            assert rid not in [r["id"] for r in reports]


# ── PDF 文本提取验证测试 ──────────────────────────────────────────────────────

class TestPDFTextExtraction:
    """验证真实 PDF 文件的文本提取效果"""

    def test_extract_semiconductor_report(self, client, test_pdf_paths):
        """验证半导体研报文本提取"""
        with open(test_pdf_paths["semiconductor"], "rb") as f:
            pdf = f.read()
        
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf), "semiconductor.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 201
        report = resp.get_json()["report"]
        text = report["text_content"]
        
        # 验证关键内容被提取
        assert "半导体" in text
        assert "投资建议" in text or "风险提示" in text

    def test_extract_newenergy_report(self, client, test_pdf_paths):
        """验证新能源研报文本提取"""
        with open(test_pdf_paths["newenergy"], "rb") as f:
            pdf = f.read()
        
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf), "newenergy.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 201
        report = resp.get_json()["report"]
        text = report["text_content"]
        
        # 验证关键内容被提取
        assert "新能源" in text or "动力电池" in text

    def test_extract_ai_report(self, client, test_pdf_paths):
        """验证 AI 研报文本提取"""
        with open(test_pdf_paths["ai"], "rb") as f:
            pdf = f.read()
        
        resp = client.post(
            "/api/v1/agent/reports/upload",
            data={"file": (io.BytesIO(pdf), "ai.pdf", "application/pdf")},
            content_type="multipart/form-data",
        )
        
        assert resp.status_code == 201
        report = resp.get_json()["report"]
        text = report["text_content"]
        
        # 验证关键内容被提取
        assert "人工智能" in text or "AI" in text

"""
M1-QA API 集成测试 — TC-M01-001~034 (L2 Integration / L3 Contract)
对齐: 13 §3.1, §3.2
"""
import json
import uuid


# ── TC-M01-001: POST /ask → 200 含 answer/llm_used/traceId ──


def test_ask_success(client):
    """TC-M01-001 (L2): POST /ask 成功返回"""
    # 先创建会话
    resp = client.post("/api/v1/agent/sessions", json={"title": "test"})
    session_id = resp.get_json()["session"]["id"]

    resp = client.post("/api/v1/agent/ask", json={
        "query": "某公司最新评级是什么？",
        "session_id": session_id,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert "answer" in data
    assert "llm_used" in data
    assert isinstance(data["llm_used"], bool)
    assert "traceId" in data
    assert "answer_source" in data
    assert "response_time_ms" in data
    assert "model" in data


# ── TC-M01-002: 空 query → 400 EMPTY_QUERY ──


def test_ask_empty_query(client):
    """TC-M01-002 (L2): 空 query → 400"""
    resp = client.post("/api/v1/agent/ask", json={
        "query": "",
        "session_id": str(uuid.uuid4()),
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "EMPTY_QUERY"


# ── TC-M01-003: query >500 → 400 INVALID_QUERY ──


def test_ask_long_query(client):
    """TC-M01-003 (L2): query >500 字符 → 400"""
    resp_s = client.post("/api/v1/agent/sessions", json={"title": "test"})
    sid = resp_s.get_json()["session"]["id"]
    resp = client.post("/api/v1/agent/ask", json={
        "query": "x" * 501,
        "session_id": sid,
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert data["error"]["code"] == "INVALID_QUERY"


# ── TC-M01-004: 无 API Key → demo 降级 ──


def test_bailian_fallback(client):
    """TC-M01-004 (L2): 无 API Key → answer_source='demo'"""
    resp_s = client.post("/api/v1/agent/sessions", json={"title": "test"})
    sid = resp_s.get_json()["session"]["id"]
    resp = client.post("/api/v1/agent/ask", json={
        "query": "测试降级",
        "session_id": sid,
    })
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["answer_source"] == "demo"
    assert data["llm_used"] is False


# ── TC-M01-020: GET /sessions → 200，返回 sessions 数组 ──


def test_get_sessions(client):
    """TC-M01-020 (L2): 会话列表"""
    client.post("/api/v1/agent/sessions", json={"title": "会话A"})
    client.post("/api/v1/agent/sessions", json={"title": "会话B"})

    resp = client.get("/api/v1/agent/sessions")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "sessions" in data
    assert "traceId" in data
    assert len(data["sessions"]) >= 2

    for s in data["sessions"]:
        assert "id" in s
        assert "title" in s
        assert "created_at" in s
        assert "query_count" in s


# ── TC-M01-021: POST /sessions → 201 ──


def test_create_session(client):
    """TC-M01-021 (L2): 新建会话"""
    resp = client.post("/api/v1/agent/sessions", json={"title": "我的会话"})
    assert resp.status_code == 201
    data = resp.get_json()
    session = data["session"]
    assert session["title"] == "我的会话"
    assert session["query_count"] == 0
    assert "id" in session
    assert "created_at" in session
    assert "traceId" in data


# ── TC-M01-022: POST /sessions 未传 title → 默认"新会话" ──


def test_create_session_default_title(client):
    """TC-M01-022 (L2): 未传 title 默认为新会话"""
    resp = client.post("/api/v1/agent/sessions", json={})
    assert resp.status_code == 201
    assert resp.get_json()["session"]["title"] == "新会话"


# ── TC-M01-023: DELETE /sessions/<id> → 200 ──


def test_delete_session(client):
    """TC-M01-023 (L2): 删除会话 + 级联删除"""
    resp_s = client.post("/api/v1/agent/sessions", json={"title": "待删除"})
    sid = resp_s.get_json()["session"]["id"]

    # 先加一条记录
    client.post("/api/v1/agent/ask", json={"query": "问题", "session_id": sid})

    resp = client.delete(f"/api/v1/agent/sessions/{sid}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "message" in data
    assert "deleted_records" in data
    assert data["deleted_records"] >= 1


# ── TC-M01-024: DELETE 不存在的 session_id → 404 ──


def test_delete_session_not_found(client):
    """TC-M01-024 (L2): 删除不存在的会话"""
    fake_id = str(uuid.uuid4())
    resp = client.delete(f"/api/v1/agent/sessions/{fake_id}")
    assert resp.status_code == 404
    assert resp.get_json()["error"]["code"] == "SESSION_NOT_FOUND"


# ── TC-M01-025: GET /sessions 响应体字段类型契约 ──


def test_sessions_contract(client):
    """TC-M01-025 (L3): sessions 响应字段类型与 09 §5 一致"""
    client.post("/api/v1/agent/sessions", json={"title": "契约测试"})
    resp = client.get("/api/v1/agent/sessions")
    data = resp.get_json()

    for s in data["sessions"]:
        assert isinstance(s["id"], str)
        assert isinstance(s["title"], str)
        assert isinstance(s["created_at"], str)
        assert isinstance(s["updated_at"], str)
        assert isinstance(s["query_count"], int)
        assert s["query_count"] >= 0


# ── TC-M01-030: GET /sessions/<id>/records 有记录 → 200 ──


def test_get_records_with_data(client):
    """TC-M01-030 (L2): 问答记录有数据"""
    resp_s = client.post("/api/v1/agent/sessions", json={"title": "测试"})
    sid = resp_s.get_json()["session"]["id"]
    client.post("/api/v1/agent/ask", json={"query": "问题", "session_id": sid})

    resp = client.get(f"/api/v1/agent/sessions/{sid}/records")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "records" in data
    assert "traceId" in data
    assert len(data["records"]) >= 1

    rec = data["records"][0]
    assert "query" in rec
    assert "answer" in rec
    assert "llm_used" in rec
    assert "answer_source" in rec
    assert "timestamp" in rec


# ── TC-M01-031: GET /sessions/<id>/records 无记录 → 200 空数组 ──


def test_get_records_empty(client):
    """TC-M01-031 (L2): 无记录返回空数组"""
    resp_s = client.post("/api/v1/agent/sessions", json={"title": "空会话"})
    sid = resp_s.get_json()["session"]["id"]

    resp = client.get(f"/api/v1/agent/sessions/{sid}/records")
    assert resp.status_code == 200
    assert resp.get_json()["records"] == []


# ── TC-M01-032: GET /capabilities → 200 契约 ──


def test_capabilities_contract(client):
    """TC-M01-032 (L3): capabilities 响应字段"""
    resp = client.get("/api/v1/agent/capabilities")
    assert resp.status_code == 200
    data = resp.get_json()
    assert "copaw_configured" in data
    assert "bailian_configured" in data
    assert "model" in data
    assert isinstance(data["copaw_configured"], bool)
    assert isinstance(data["bailian_configured"], bool)
    assert "traceId" in data


# ── TC-M01-033: GET /health → 200 目录可写时 status=healthy ──


def test_health_healthy(client):
    """TC-M01-033 (L2): 健康检查 — healthy"""
    resp = client.get("/api/v1/agent/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert "uptime" in data
    assert "components" in data
    assert data["components"]["storage"] == "ok"


# ── TC-M01-034: GET /health 目录不可写 → degraded ──


def test_health_degraded(client, app, monkeypatch):
    """TC-M01-034 (L2): 健康检查 — degraded"""
    monkeypatch.setattr(app.storage, "is_data_dir_writable", lambda: False)
    resp = client.get("/api/v1/agent/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "degraded"
    assert data["components"]["storage"] == "error"

"""
M1-QA 投研问答助手 — Route 层（7 个 API 端点）
对齐: 09 §1~§9 API 接口规格
"""
import uuid
import re

from flask import Blueprint, current_app, g, jsonify, request
from wsgi import make_error

agent_bp = Blueprint("agent", __name__, url_prefix="/api/v1/agent")

UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.I
)


# ── 1. GET /capabilities — 能力探测（对齐 09 §1 端点 1, 05 US-005）──


@agent_bp.route("/capabilities", methods=["GET"])
def get_capabilities():
    caps = current_app.agent.get_capabilities()
    caps["traceId"] = g.trace_id
    return jsonify(caps), 200


# ── 2. POST /ask — 问答提交（对齐 09 §3）──


@agent_bp.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True, silent=True) or {}
    query = data.get("query", "")
    session_id = data.get("session_id", "")
    # 新增：研报知识库增强参数（默认 false，保持向后兼容）
    use_reports = data.get("use_reports", False)
    report_ids = data.get("report_ids", None)

    # 参数校验（对齐 09 §8）
    if not query or not str(query).strip():
        return make_error("EMPTY_QUERY", "请输入问题", 400)

    query = str(query)
    if len(query) > 500:
        return make_error("INVALID_QUERY", "问题过长，最多 500 字符", 400, {"max_length": 500})

    if not session_id:
        return make_error("INVALID_QUERY", "缺少 session_id", 400)

    # 校验 session 存在性
    storage = current_app.storage
    session = storage._get_session(session_id)
    if session is None:
        return make_error("SESSION_NOT_FOUND", "会话不存在", 404, {"session_id": session_id})

    # 校验 report_ids 参数
    if use_reports and report_ids is not None:
        if not isinstance(report_ids, list):
            return make_error("INVALID_QUERY", "report_ids 必须为数组", 400)
        # 校验每个 ID 的格式
        for rid in report_ids:
            if not isinstance(rid, str) or not rid.startswith("rpt_"):
                return make_error(
                    "INVALID_REPORT_ID", "report_id 格式不合法", 400, {"report_id": rid}
                )

    # Agent 编排
    try:
        # 获取研报存储实例（如果启用研报知识库）
        report_storage = None
        if use_reports:
            report_storage = getattr(current_app, "report_storage", None)

        result = current_app.agent.ask(
            query,
            session_id,
            use_reports=use_reports,
            report_ids=report_ids,
            report_storage=report_storage,
        )
    except Exception:
        return make_error("SERVER_ERROR", "服务器繁忙，请稍后重试", 500)

    # 存储记录
    record_dict = {
        "query": query,
        "answer": result["answer"],
        "llm_used": result["llm_used"],
        "model": result.get("model"),
        "response_time_ms": result["response_time_ms"],
        "answer_source": result["answer_source"],
    }
    try:
        storage.add_record(session_id, record_dict)
    except Exception:
        pass  # 记录写入失败不影响返回

    result["traceId"] = g.trace_id
    return jsonify(result), 200


# ── 3. GET /sessions — 会话列表（对齐 09 §5）──


@agent_bp.route("/sessions", methods=["GET"])
def get_sessions():
    sessions = current_app.storage.get_sessions()
    # 映射字段名: session_id -> id（对齐 09 §5 sessions[].id）
    items = []
    for s in sessions:
        items.append({
            "id": s["session_id"],
            "title": s["title"],
            "created_at": s["created_at"],
            "updated_at": s["updated_at"],
            "query_count": s["query_count"],
        })
    return jsonify({"traceId": g.trace_id, "sessions": items}), 200


# ── 4. POST /sessions — 新建会话（对齐 09 §4）──


@agent_bp.route("/sessions", methods=["POST"])
def create_session():
    data = request.get_json(force=True, silent=True) or {}
    title = data.get("title", "新会话")

    if title and len(str(title)) > 100:
        return make_error("INVALID_QUERY", "标题过长，最多 100 字符", 400)

    session_id = str(uuid.uuid4())
    session = current_app.storage.create_session(session_id, str(title) if title else "新会话")

    return jsonify({
        "traceId": g.trace_id,
        "session": {
            "id": session["session_id"],
            "title": session["title"],
            "created_at": session["created_at"],
            "updated_at": session["updated_at"],
            "query_count": session["query_count"],
        },
    }), 201


# ── 5. DELETE /sessions/<id> — 删除会话（对齐 09 §6）──


@agent_bp.route("/sessions/<session_id>", methods=["DELETE"])
def delete_session(session_id):
    # UUID 格式校验
    if not UUID_RE.match(session_id):
        return make_error("INVALID_QUERY", "session_id 格式不合法", 400)

    try:
        deleted_count = current_app.storage.delete_session(session_id)
    except KeyError:
        return make_error(
            "SESSION_NOT_FOUND", "会话不存在", 404, {"session_id": session_id}
        )

    return jsonify({
        "traceId": g.trace_id,
        "message": "会话已删除",
        "deleted_records": deleted_count,
    }), 200


# ── 6. GET /sessions/<id>/records — 问答记录（对齐 09 §7）──


@agent_bp.route("/sessions/<session_id>/records", methods=["GET"])
def get_records(session_id):
    # UUID 格式校验
    if not UUID_RE.match(session_id):
        return make_error("INVALID_QUERY", "session_id 格式不合法", 400)

    # 存在性校验
    session = current_app.storage._get_session(session_id)
    if session is None:
        return make_error(
            "SESSION_NOT_FOUND", "会话不存在", 404, {"session_id": session_id}
        )

    records = current_app.storage.get_records_by_session(session_id)
    return jsonify({"traceId": g.trace_id, "records": records}), 200


# ── 7. GET /health — 健康检查（对齐 09 §9）──


@agent_bp.route("/health", methods=["GET"])
def health():
    result = current_app.agent.get_health(current_app.storage)
    return jsonify(result), 200

"""
M1-QA 投研问答助手 — 研报蓝图（6 个 API 端点）
对齐: report-feature-design.md §2 API 端点设计
"""
import os
import re
import math
import time
from datetime import datetime, timezone

from flask import Blueprint, current_app, g, jsonify, request
from wsgi import make_error

report_bp = Blueprint("report", __name__, url_prefix="/api/v1/agent/reports")

# 研报 ID 格式：rpt_{13位以上时间戳}
REPORT_ID_RE = re.compile(r"^rpt_\d{13,}$")
# 对比 ID 格式：cmp_{13位以上时间戳}
COMPARE_ID_RE = re.compile(r"^cmp_\d{13,}$")
# 允许的状态值
VALID_STATUS = {"ready", "parsing", "error"}
# 关注点最大数量
MAX_FOCUS_AREAS = 5


# ── 工具函数 ──

def _get_report_storage():
    """从应用上下文中获取研报存储实例"""
    return current_app.report_storage


def _sanitize_filename(filename: str) -> str:
    """
    文件名消毒：移除路径分隔符和危险字符，防止路径遍历攻击。
    """
    # 只保留文件名部分（去除路径）
    filename = os.path.basename(filename)
    # 移除非法字符，仅保留字母、数字、下划线、短横线、点
    filename = re.sub(r"[^\w\-.]", "_", filename)
    return filename


def _build_report_upload_dir() -> str:
    """
    按年/月构建研报文件存储子目录并确保目录存在。
    格式：{REPORT_UPLOAD_DIR}/{year}/{month}/
    """
    import config

    now = datetime.now(timezone.utc)
    sub_dir = os.path.join(
        str(config.REPORT_UPLOAD_DIR),
        str(now.year),
        f"{now.month:02d}",
    )
    os.makedirs(sub_dir, exist_ok=True)
    return sub_dir


def _report_to_list_item(report: dict) -> dict:
    """将研报完整记录转换为列表展示字段（不含 text_content）"""
    return {
        "id": report["id"],
        "title": report["title"],
        "filename": report["filename"],
        "file_size": report["file_size"],
        "file_type": report["file_type"],
        "text_length": report["text_length"],
        "upload_time": report["upload_time"],
        "status": report["status"],
    }


# ── 1. POST /upload — 研报文件上传 ──


@report_bp.route("/upload", methods=["POST"])
def upload_report():
    """
    上传研报文件（multipart/form-data）。
    支持 PDF/DOCX，提取文本内容，存储元数据。
    对齐: report-feature-design.md §2.2
    """
    import config
    from report_parser import extract_text

    # ── 文件校验 ──
    if "file" not in request.files:
        return make_error("EMPTY_FILE", "请选择要上传的文件", 400)

    file = request.files["file"]

    if not file or not file.filename:
        return make_error("EMPTY_FILENAME", "文件名不能为空", 400)

    filename = file.filename.strip()
    if not filename:
        return make_error("EMPTY_FILENAME", "文件名不能为空", 400)

    # 校验文件类型（扩展名）
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in config.ALLOWED_REPORT_TYPES:
        return make_error(
            "INVALID_FILE_TYPE",
            f"不支持的文件类型，仅支持 {'/'.join(t.upper() for t in config.ALLOWED_REPORT_TYPES)}",
            400,
        )

    # 校验 MIME Type（双重校验）
    mime_whitelist = {
        "pdf": ["application/pdf"],
        "docx": [
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            "application/octet-stream",
        ],
    }
    content_type = file.content_type or ""
    allowed_mimes = mime_whitelist.get(ext, [])
    # 若 MIME 不在白名单且不为空（宽松校验，允许浏览器传 octet-stream）
    if content_type and allowed_mimes and content_type not in allowed_mimes:
        # 特殊情况：某些浏览器对 PDF 传 application/octet-stream，允许通过
        if content_type != "application/octet-stream":
            return make_error(
                "INVALID_FILE_TYPE",
                f"不支持的文件类型，仅支持 {'/'.join(t.upper() for t in config.ALLOWED_REPORT_TYPES)}",
                400,
            )

    # 校验文件大小（先读取到内存检查，超限报错）
    file_bytes = file.read()
    file_size = len(file_bytes)
    if file_size > config.MAX_REPORT_SIZE:
        return make_error(
            "FILE_TOO_LARGE",
            f"文件大小超过限制（最大 {config.MAX_REPORT_SIZE // 1024 // 1024}MB）",
            400,
            {"max_size": config.MAX_REPORT_SIZE, "actual_size": file_size},
        )

    # ── 生成研报 ID 和文件路径 ──
    ts_ms = int(time.time() * 1000)
    report_id = f"rpt_{ts_ms}"
    safe_filename = _sanitize_filename(filename)
    upload_sub_dir = _build_report_upload_dir()
    physical_path = os.path.join(upload_sub_dir, f"{report_id}.{ext}")

    # 计算相对路径（相对于 data 目录，用于存储在 JSON 中）
    now = datetime.now(timezone.utc)
    relative_path = os.path.join(
        "report_files", str(now.year), f"{now.month:02d}", f"{report_id}.{ext}"
    ).replace("\\", "/")  # 统一使用正斜杠

    # ── 写入物理文件 ──
    try:
        with open(physical_path, "wb") as f:
            f.write(file_bytes)
    except Exception:
        return make_error("SERVER_ERROR", "服务器繁忙，请稍后重试", 500)

    # ── 文本提取 ──
    try:
        text_content, meta = extract_text(physical_path, ext)
    except Exception:
        # 解析失败：删除已保存的文件，返回错误
        try:
            os.remove(physical_path)
        except Exception:
            pass
        return make_error("PARSE_ERROR", "文件解析失败，请检查文件是否损坏", 500)

    # ── 获取研报标题 ──
    title = (request.form.get("title", "") or "").strip()
    if not title:
        # 默认使用文件名（去掉扩展名）
        title = safe_filename.rsplit(".", 1)[0] if "." in safe_filename else safe_filename
    title = title[: config.MAX_REPORT_TITLE_LENGTH]  # 截断超长标题

    # ── 构建元数据 ──
    upload_time = datetime.now(timezone.utc).isoformat()
    word_count = len(text_content)
    report_record = {
        "id": report_id,
        "title": title,
        "filename": safe_filename,
        "file_path": relative_path,
        "file_size": file_size,
        "file_type": ext,
        "text_content": text_content,
        "text_length": word_count,
        "upload_time": upload_time,
        "status": "ready",
        "metadata": {
            "pages": meta.get("pages"),
            "author": meta.get("author"),
            "word_count": word_count,
        },
    }

    # ── 持久化元数据 ──
    try:
        _get_report_storage().create_report(report_record)
    except Exception:
        # 持久化失败：删除物理文件，返回错误
        try:
            os.remove(physical_path)
        except Exception:
            pass
        return make_error("SERVER_ERROR", "服务器繁忙，请稍后重试", 500)

    return jsonify({"traceId": g.trace_id, "report": report_record}), 201


# ── 2. GET / — 研报列表 ──


@report_bp.route("/", methods=["GET"])
def list_reports():
    """
    获取研报列表，支持分页和状态过滤。
    对齐: report-feature-design.md §2.3
    """
    # 解析分页参数
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 20))
    except (ValueError, TypeError):
        return make_error("INVALID_QUERY", "page 和 page_size 必须为整数", 400)

    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    # 状态过滤参数
    status = request.args.get("status", "").strip() or None
    if status and status not in VALID_STATUS:
        return make_error(
            "INVALID_QUERY",
            f"status 参数无效，可选值：{'/'.join(VALID_STATUS)}",
            400,
        )

    result = _get_report_storage().get_reports(status=status, page=page, page_size=page_size)
    total = result["total"]

    total_pages = math.ceil(total / page_size) if page_size > 0 else 0

    # 列表字段不含 text_content（节省流量）
    items = [_report_to_list_item(r) for r in result["items"]]

    return jsonify({
        "traceId": g.trace_id,
        "reports": items,
        "pagination": {
            "page": page,
            "page_size": page_size,
            "total": total,
            "total_pages": total_pages,
        },
    }), 200


# ── 3. GET /<id> — 研报详情 ──


@report_bp.route("/<report_id>", methods=["GET"])
def get_report(report_id):
    """
    获取单份研报详情（含 text_content）。
    对齐: report-feature-design.md §2.4
    """
    # ID 格式校验
    if not REPORT_ID_RE.match(report_id):
        return make_error("INVALID_REPORT_ID", "report_id 格式不合法", 400)

    report = _get_report_storage().get_report_by_id(report_id)
    if report is None:
        return make_error("REPORT_NOT_FOUND", "研报不存在", 404, {"report_id": report_id})

    return jsonify({"traceId": g.trace_id, "report": report}), 200


# ── 4. DELETE /<id> — 删除研报 ──


@report_bp.route("/<report_id>", methods=["DELETE"])
def delete_report(report_id):
    """
    删除研报：同步删除物理文件和 JSON 元数据。
    对齐: report-feature-design.md §2.5
    """
    import config

    # ID 格式校验
    if not REPORT_ID_RE.match(report_id):
        return make_error("INVALID_REPORT_ID", "report_id 格式不合法", 400)

    try:
        deleted = _get_report_storage().delete_report(report_id)
    except KeyError:
        return make_error("REPORT_NOT_FOUND", "研报不存在", 404, {"report_id": report_id})

    # 同步删除物理文件
    file_path = deleted.get("file_path", "")
    if file_path:
        physical_path = os.path.join(str(config.DATA_DIR), file_path)
        try:
            if os.path.exists(physical_path):
                os.remove(physical_path)
        except Exception:
            pass  # 文件删除失败不影响元数据删除结果

    return jsonify({
        "traceId": g.trace_id,
        "message": "研报已删除",
        "deleted_id": report_id,
    }), 200


# ── 5. POST /compare — 对比分析 ──


@report_bp.route("/compare", methods=["POST"])
def compare_reports():
    """
    对比两份研报，调用 LLM 生成分析报告。
    对齐: report-feature-design.md §2.6
    """
    data = request.get_json(force=True, silent=True) or {}
    report_ids = data.get("report_ids", [])
    focus_areas = data.get("focus_areas") or []

    # ── 参数校验 ──
    if not isinstance(report_ids, list) or len(report_ids) != 2:
        return make_error("INVALID_REPORT_COUNT", "需要且仅需要两份研报进行对比", 400)

    for rid in report_ids:
        if not isinstance(rid, str) or not REPORT_ID_RE.match(rid):
            return make_error(
                "INVALID_REPORT_ID", "report_id 格式不合法", 400, {"report_id": rid}
            )

    if report_ids[0] == report_ids[1]:
        return make_error("DUPLICATE_REPORT", "不能对比同一份研报", 400)

    if not isinstance(focus_areas, list):
        focus_areas = []
    # 限制最多 5 个关注点
    focus_areas = [str(f).strip() for f in focus_areas if str(f).strip()][:MAX_FOCUS_AREAS]

    # ── 查找研报 ──
    report_storage = _get_report_storage()
    report_a = report_storage.get_report_by_id(report_ids[0])
    if report_a is None:
        return make_error(
            "REPORT_NOT_FOUND", "研报不存在", 404, {"report_id": report_ids[0]}
        )
    report_b = report_storage.get_report_by_id(report_ids[1])
    if report_b is None:
        return make_error(
            "REPORT_NOT_FOUND", "研报不存在", 404, {"report_id": report_ids[1]}
        )

    # ── 调用 LLM 对比分析（三级降级）──
    try:
        compare_result_data = current_app.agent.compare_reports(report_a, report_b, focus_areas)
    except Exception:
        return make_error("SERVER_ERROR", "服务器繁忙，请稍后重试", 500)

    # ── 构建并存储对比报告 ──
    ts_ms = int(time.time() * 1000)
    compare_id = f"cmp_{ts_ms}"
    create_time = datetime.now(timezone.utc).isoformat()

    compare_record = {
        "id": compare_id,
        "report_ids": report_ids,
        "report_titles": [report_a["title"], report_b["title"]],
        "focus_areas": focus_areas,
        "compare_result": compare_result_data["compare_result"],
        "llm_used": compare_result_data["llm_used"],
        "model": compare_result_data.get("model"),
        "response_time_ms": compare_result_data["response_time_ms"],
        "create_time": create_time,
    }

    try:
        report_storage.create_compare(compare_record)
    except Exception:
        pass  # 存储失败不影响本次返回

    return jsonify({"traceId": g.trace_id, "compare": compare_record}), 200


# ── 6. GET /compare/<id> — 对比报告详情 ──


@report_bp.route("/compare/<compare_id>", methods=["GET"])
def get_compare(compare_id):
    """
    获取对比报告详情。
    对齐: report-feature-design.md §2.7
    """
    # ID 格式校验
    if not COMPARE_ID_RE.match(compare_id):
        return make_error("INVALID_COMPARE_ID", "compare_id 格式不合法", 400)

    compare = _get_report_storage().get_compare_by_id(compare_id)
    if compare is None:
        return make_error(
            "COMPARE_NOT_FOUND", "对比报告不存在", 404, {"compare_id": compare_id}
        )

    return jsonify({"traceId": g.trace_id, "compare": compare}), 200

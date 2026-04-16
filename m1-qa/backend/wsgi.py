"""
M1-QA 投研问答助手 — Flask 应用工厂 + 启动入口
对齐: 08 §2 分层架构, 09 §2 统一响应规范
"""
import time
import uuid

from flask import Flask, g, request
from flask_cors import CORS

import config

# 应用启动时间（用于 /health uptime 计算）
_start_time = time.time()


def get_start_time():
    return _start_time


def generate_trace_id():
    """生成 traceId，优先复用请求头 X-Trace-Id（对齐 07 §3.1）"""
    return request.headers.get("X-Trace-Id") or f"tr_{uuid.uuid4().hex[:16]}"


def make_error(code: str, message: str, http_status: int, details: dict | None = None):
    """统一错误响应工厂（对齐 09 §2 错误码清单）"""
    return {
        "error": {
            "code": code,
            "message": message,
            "details": details or {},
            "traceId": g.get("trace_id", f"tr_{uuid.uuid4().hex[:16]}"),
        }
    }, http_status


def create_app(data_dir=None):
    """Flask 应用工厂"""
    app = Flask(__name__)
    CORS(app)

    # 初始化 Storage
    from storage import Storage
    storage_dir = data_dir or config.DATA_DIR
    app.storage = Storage(str(storage_dir))

    # 初始化研报存储
    from report_storage import ReportStorage
    app.report_storage = ReportStorage(str(storage_dir))

    # 确保研报文件目录存在
    import os
    os.makedirs(str(config.REPORT_UPLOAD_DIR), exist_ok=True)

    # 初始化 Agent
    from agent import CoPawAgent
    app.agent = CoPawAgent()

    @app.before_request
    def inject_trace_id():
        g.trace_id = generate_trace_id()

    # 注册 Blueprint
    from agent_bp import agent_bp
    app.register_blueprint(agent_bp)

    # 注册研报蓝图
    from report_bp import report_bp
    app.register_blueprint(report_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=config.FLASK_PORT, debug=config.FLASK_DEBUG)

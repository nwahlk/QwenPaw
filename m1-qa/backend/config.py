"""
M1-QA 投研问答助手 — 配置管理
对齐: 08 §2 后端分层, 07 §4.1 敏感数据保护
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── 数据目录 ──
DATA_DIR = Path(os.getenv("DATA_DIR", os.path.join(os.path.dirname(__file__), "data")))

# ── CoPaw 桥接 ──
COPAW_APP_URL = os.getenv("IRA_COPAW_APP_URL", "")
COPAW_API_KEY = os.getenv("IRA_COPAW_API_KEY", "")
COPAW_TIMEOUT = int(os.getenv("IRA_COPAW_TIMEOUT", "20"))

# ── 百炼 DashScope ──
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_MODEL = os.getenv("DASHSCOPE_MODEL", "qwen-turbo")
DASHSCOPE_TIMEOUT = int(os.getenv("DASHSCOPE_TIMEOUT", "120"))

# ── Flask ──
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "false").lower() == "true"

# ── 研报上传配置 ──
REPORT_UPLOAD_DIR = Path(os.getenv("REPORT_UPLOAD_DIR", os.path.join(str(DATA_DIR), "report_files")))
MAX_REPORT_SIZE = int(os.getenv("MAX_REPORT_SIZE", "10485760"))  # 默认 10MB
ALLOWED_REPORT_TYPES = os.getenv("ALLOWED_REPORT_TYPES", "pdf,docx").split(",")
MAX_REPORT_TITLE_LENGTH = int(os.getenv("MAX_REPORT_TITLE_LENGTH", "200"))  # 标题最大长度
MAX_COMPARE_TEXT_LENGTH = int(os.getenv("MAX_COMPARE_TEXT_LENGTH", "30000"))  # Prompt 截断阈值（约 2 万字中文）

# ── 研报知识库检索配置 ──
# 问答时注入研报上下文的最大总字符数，防止超出 LLM 上下文窗口
MAX_REPORT_CONTEXT_LENGTH = int(os.getenv("MAX_REPORT_CONTEXT_LENGTH", "5000"))
# 默认检索研报数量（top-k）
REPORT_SEARCH_TOP_K = int(os.getenv("REPORT_SEARCH_TOP_K", "3"))
# 每份研报最多提取的段落字符数
REPORT_EXCERPT_MAX_LENGTH = int(os.getenv("REPORT_EXCERPT_MAX_LENGTH", "1000"))

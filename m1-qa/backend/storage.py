"""
M1-QA 投研问答助手 — Storage 层（JSON 文件 CRUD）
对齐: 10 §2~§6 数据模型与存储规格
"""
import json
import os
import time
from datetime import datetime, timezone


class Storage:
    """JSON 文件存储引擎 — RMW 模式（全量读入 → 修改 → 全量写回）"""

    def __init__(self, data_dir: str):
        """
        初始化存储，自动创建数据目录和空 JSON 文件。
        对齐: 10 §2 存储引擎, TC-M01-040
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

        self._sessions_path = os.path.join(data_dir, "sessions.json")
        self._records_path = os.path.join(data_dir, "qa_records.json")

        # 初始化空文件
        if not os.path.exists(self._sessions_path):
            self._write_json(self._sessions_path, [])
        if not os.path.exists(self._records_path):
            self._write_json(self._records_path, [])

    # ── 内部 IO ──

    @staticmethod
    def _read_json(path: str) -> list:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def _write_json(path: str, data: list):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ── 5.1 会话管理 ──

    def create_session(self, session_id: str, title: str = "新会话") -> dict:
        """
        创建新会话。
        对齐: 10 §5.1, TC-M01-041
        """
        now = datetime.now(timezone.utc).isoformat()
        session = {
            "session_id": session_id,
            "title": title,
            "created_at": now,
            "updated_at": now,
            "query_count": 0,
        }
        sessions = self._read_json(self._sessions_path)
        sessions.append(session)
        self._write_json(self._sessions_path, sessions)
        return session

    def get_sessions(self) -> list:
        """
        返回全部会话列表，按 created_at 倒序。
        对齐: 10 §5.1, TC-M01-042
        """
        sessions = self._read_json(self._sessions_path)
        sessions.sort(key=lambda s: s["created_at"], reverse=True)
        return sessions

    def delete_session(self, session_id: str) -> int:
        """
        删除会话 + 级联删除关联记录，返回删除的记录条数。
        对齐: 10 §5.1, TC-M01-043
        """
        sessions = self._read_json(self._sessions_path)
        new_sessions = [s for s in sessions if s["session_id"] != session_id]
        if len(new_sessions) == len(sessions):
            raise KeyError(f"Session {session_id} not found")
        self._write_json(self._sessions_path, new_sessions)

        # 级联删除关联记录
        deleted_count = self.delete_records_by_session(session_id)
        return deleted_count

    def update_session(self, session_id: str, **kwargs) -> dict:
        """
        按 session_id 更新指定字段（如 title、updated_at）。
        对齐: 10 §5.1, TC-M01-046
        """
        sessions = self._read_json(self._sessions_path)
        for session in sessions:
            if session["session_id"] == session_id:
                for key, value in kwargs.items():
                    if key in session:
                        session[key] = value
                session["updated_at"] = datetime.now(timezone.utc).isoformat()
                self._write_json(self._sessions_path, sessions)
                return session
        raise KeyError(f"Session {session_id} not found")

    def _get_session(self, session_id: str) -> dict | None:
        """内部方法：按 session_id 查找单个会话"""
        sessions = self._read_json(self._sessions_path)
        for s in sessions:
            if s["session_id"] == session_id:
                return s
        return None

    # ── 5.2 问答记录管理 ──

    def add_record(self, session_id: str, record_dict: dict) -> dict:
        """
        写入问答记录 + 更新 session query_count + 首次自动重命名。
        对齐: 10 §5.2 + §6 关键业务逻辑, TC-M01-044/048/049

        record_dict 必须包含: query, answer, llm_used, model, response_time_ms, answer_source
        """
        query = record_dict.get("query", "")

        # 输入校验（对齐 10 §6, 09 §8）
        if not query or not query.strip():
            raise ValueError("query 不能为空")
        if len(query) > 500:
            raise ValueError("query 超过 500 字符限制")

        # 检查 session 存在性
        sessions = self._read_json(self._sessions_path)
        target = None
        for s in sessions:
            if s["session_id"] == session_id:
                target = s
                break
        if target is None:
            raise KeyError(f"Session {session_id} not found")

        # 构建记录
        now = datetime.now(timezone.utc).isoformat()
        record = {
            "id": f"rec_{int(time.time() * 1000)}",
            "session_id": session_id,
            "query": query,
            "answer": record_dict.get("answer", ""),
            "llm_used": record_dict.get("llm_used", False),
            "model": record_dict.get("model"),
            "response_time_ms": record_dict.get("response_time_ms", 0),
            "answer_source": record_dict.get("answer_source"),
            "timestamp": now,
        }

        # 写入记录
        records = self._read_json(self._records_path)
        records.append(record)
        self._write_json(self._records_path, records)

        # 更新 session: query_count +1, updated_at
        target["query_count"] += 1
        target["updated_at"] = now

        # 首次问答自动重命名（对齐 10 §6）
        if target["query_count"] == 1:
            target["title"] = query[:20] + ("..." if len(query) > 20 else "")

        self._write_json(self._sessions_path, sessions)
        return record

    def get_records_by_session(self, session_id: str) -> list:
        """
        按 session_id 过滤，返回该会话全部记录，按 timestamp 正序。
        对齐: 10 §5.2, TC-M01-045
        """
        records = self._read_json(self._records_path)
        filtered = [r for r in records if r["session_id"] == session_id]
        filtered.sort(key=lambda r: r["timestamp"])
        return filtered

    def delete_records_by_session(self, session_id: str) -> int:
        """
        删除指定 session_id 下所有记录，返回删除条数。
        对齐: 10 §5.2, TC-M01-047
        """
        records = self._read_json(self._records_path)
        remaining = [r for r in records if r["session_id"] != session_id]
        deleted_count = len(records) - len(remaining)
        self._write_json(self._records_path, remaining)
        return deleted_count

    def is_data_dir_writable(self) -> bool:
        """检查数据目录是否可写（用于 /health）"""
        try:
            test_file = os.path.join(self.data_dir, ".write_test")
            with open(test_file, "w") as f:
                f.write("ok")
            os.remove(test_file)
            return True
        except (IOError, OSError):
            return False

"""
M1-QA Storage 层单元测试 — TC-M01-040~049 (L1 Unit)
对齐: 13 §3.3
"""
import uuid
import time
import pytest


class TestStorageInit:
    """TC-M01-040: Storage.__init__ 目录自动创建"""

    def test_auto_create_dir(self, tmp_path):
        from storage import Storage
        data_dir = str(tmp_path / "nonexistent" / "data")
        s = Storage(data_dir)
        assert (tmp_path / "nonexistent" / "data" / "sessions.json").exists()
        assert (tmp_path / "nonexistent" / "data" / "qa_records.json").exists()

    def test_init_empty_json(self, tmp_storage):
        import json
        with open(tmp_storage._sessions_path) as f:
            assert json.load(f) == []
        with open(tmp_storage._records_path) as f:
            assert json.load(f) == []


class TestCreateSession:
    """TC-M01-041: create_session 返回完整 dict"""

    def test_returns_complete_dict(self, tmp_storage):
        sid = str(uuid.uuid4())
        result = tmp_storage.create_session(sid, "测试会话")
        assert result["session_id"] == sid
        assert result["title"] == "测试会话"
        assert result["query_count"] == 0
        assert "created_at" in result
        assert "updated_at" in result

    def test_default_title(self, tmp_storage):
        sid = str(uuid.uuid4())
        result = tmp_storage.create_session(sid)
        assert result["title"] == "新会话"


class TestGetSessions:
    """TC-M01-042: get_sessions 按 created_at 倒序"""

    def test_order_by_created_at_desc(self, tmp_storage):
        sid1 = str(uuid.uuid4())
        sid2 = str(uuid.uuid4())
        tmp_storage.create_session(sid1, "第一个")
        time.sleep(0.01)
        tmp_storage.create_session(sid2, "第二个")

        sessions = tmp_storage.get_sessions()
        assert len(sessions) == 2
        assert sessions[0]["title"] == "第二个"
        assert sessions[1]["title"] == "第一个"


class TestDeleteSession:
    """TC-M01-043: delete_session 级联删除关联记录"""

    def test_cascade_delete(self, seeded_storage):
        storage, sid1, sid2 = seeded_storage
        deleted = storage.delete_session(sid1)
        assert deleted >= 1  # sid1 有 1 条记录

        # 会话已删除
        sessions = storage.get_sessions()
        ids = [s["session_id"] for s in sessions]
        assert sid1 not in ids
        assert sid2 in ids

        # 关联记录已清除
        records = storage.get_records_by_session(sid1)
        assert len(records) == 0

    def test_delete_nonexistent_raises(self, tmp_storage):
        with pytest.raises(KeyError):
            tmp_storage.delete_session("nonexistent-id")


class TestAddRecord:
    """TC-M01-044: add_record 写入后 query_count +1"""

    def test_query_count_increment(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid, "测试")

        tmp_storage.add_record(sid, {
            "query": "问题1",
            "answer": "回答1",
            "llm_used": False,
            "model": None,
            "response_time_ms": 5,
            "answer_source": "demo",
        })

        session = tmp_storage._get_session(sid)
        assert session["query_count"] == 1

    def test_record_fields(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid)
        record = tmp_storage.add_record(sid, {
            "query": "问题",
            "answer": "回答",
            "llm_used": True,
            "model": "qwen-turbo",
            "response_time_ms": 100,
            "answer_source": "bailian",
        })
        assert record["query"] == "问题"
        assert record["answer"] == "回答"
        assert record["llm_used"] is True
        assert record["model"] == "qwen-turbo"
        assert record["answer_source"] == "bailian"
        assert "id" in record
        assert "timestamp" in record


class TestGetRecordsBySession:
    """TC-M01-045: get_records_by_session 按 timestamp 正序"""

    def test_order_by_timestamp_asc(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid)

        for i in range(3):
            tmp_storage.add_record(sid, {
                "query": f"问题{i}",
                "answer": f"回答{i}",
                "llm_used": False,
                "model": None,
                "response_time_ms": 1,
                "answer_source": "demo",
            })
            time.sleep(0.01)

        records = tmp_storage.get_records_by_session(sid)
        assert len(records) == 3
        assert records[0]["query"] == "问题0"
        assert records[2]["query"] == "问题2"
        # 确认正序
        for i in range(len(records) - 1):
            assert records[i]["timestamp"] <= records[i + 1]["timestamp"]


class TestUpdateSession:
    """TC-M01-046: update_session title 变更"""

    def test_update_title(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid, "原标题")
        updated = tmp_storage.update_session(sid, title="新标题")
        assert updated["title"] == "新标题"

    def test_update_nonexistent_raises(self, tmp_storage):
        with pytest.raises(KeyError):
            tmp_storage.update_session("nonexistent", title="x")


class TestDeleteRecordsBySession:
    """TC-M01-047: delete_records_by_session 仅删目标 session 记录"""

    def test_only_deletes_target(self, seeded_storage):
        storage, sid1, sid2 = seeded_storage
        # 给 sid2 也加一条记录
        storage.add_record(sid2, {
            "query": "另一个问题",
            "answer": "另一个回答",
            "llm_used": False,
            "model": None,
            "response_time_ms": 5,
            "answer_source": "demo",
        })

        deleted = storage.delete_records_by_session(sid1)
        assert deleted >= 1

        # sid2 的记录不受影响
        records_2 = storage.get_records_by_session(sid2)
        assert len(records_2) == 1


class TestAutoRename:
    """TC-M01-048: 首次问答 query_count 0→1 时自动重命名 title"""

    def test_first_query_renames(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid, "新会话")

        long_query = "这是一个非常长的问题，用来测试自动重命名功能是否正常工作？"
        tmp_storage.add_record(sid, {
            "query": long_query,
            "answer": "回答",
            "llm_used": False,
            "model": None,
            "response_time_ms": 1,
            "answer_source": "demo",
        })

        session = tmp_storage._get_session(sid)
        assert session["title"] == long_query[:20] + "..."

    def test_second_query_no_rename(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid)

        # 第一次
        tmp_storage.add_record(sid, {
            "query": "第一个问题",
            "answer": "回答",
            "llm_used": False,
            "model": None,
            "response_time_ms": 1,
            "answer_source": "demo",
        })
        title_after_first = tmp_storage._get_session(sid)["title"]

        # 第二次
        tmp_storage.add_record(sid, {
            "query": "完全不同的第二个问题",
            "answer": "回答",
            "llm_used": False,
            "model": None,
            "response_time_ms": 1,
            "answer_source": "demo",
        })
        title_after_second = tmp_storage._get_session(sid)["title"]
        assert title_after_first == title_after_second


class TestInputValidation:
    """TC-M01-049: query 为空/超长抛 ValueError"""

    def test_empty_query_raises(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid)
        with pytest.raises(ValueError):
            tmp_storage.add_record(sid, {
                "query": "",
                "answer": "x",
                "llm_used": False,
                "model": None,
                "response_time_ms": 0,
                "answer_source": "demo",
            })

    def test_whitespace_query_raises(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid)
        with pytest.raises(ValueError):
            tmp_storage.add_record(sid, {
                "query": "   ",
                "answer": "x",
                "llm_used": False,
                "model": None,
                "response_time_ms": 0,
                "answer_source": "demo",
            })

    def test_long_query_raises(self, tmp_storage):
        sid = str(uuid.uuid4())
        tmp_storage.create_session(sid)
        with pytest.raises(ValueError):
            tmp_storage.add_record(sid, {
                "query": "x" * 501,
                "answer": "x",
                "llm_used": False,
                "model": None,
                "response_time_ms": 0,
                "answer_source": "demo",
            })

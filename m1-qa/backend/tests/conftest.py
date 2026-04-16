"""
M1-QA pytest fixtures
"""
import sys
import os
import pytest

# 确保 backend 目录在 sys.path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture
def tmp_storage(tmp_path):
    """使用临时目录创建 Storage 实例"""
    from storage import Storage
    return Storage(str(tmp_path / "data"))


@pytest.fixture
def app(tmp_path):
    """Flask test app，使用临时数据目录"""
    from wsgi import create_app
    app = create_app(data_dir=str(tmp_path / "data"))
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def seeded_storage(tmp_storage):
    """预置种子数据的 Storage"""
    import uuid
    sid1 = str(uuid.uuid4())
    sid2 = str(uuid.uuid4())
    tmp_storage.create_session(sid1, "会话一")
    tmp_storage.create_session(sid2, "会话二")

    # 给会话一添加一条记录
    tmp_storage.add_record(sid1, {
        "query": "测试问题",
        "answer": "测试回答",
        "llm_used": False,
        "model": None,
        "response_time_ms": 10,
        "answer_source": "demo",
    })
    return tmp_storage, sid1, sid2

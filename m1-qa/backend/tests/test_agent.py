"""
M1-QA Agent 降级测试 — TC-M01-004 扩展
对齐: 13 §三 示例, 08 §4
"""
from unittest.mock import patch


def test_agent_demo_fallback():
    """Agent 降级链: CoPaw/百炼均未配置时，返回 demo"""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    with patch.dict(os.environ, {
        "IRA_COPAW_APP_URL": "",
        "IRA_COPAW_API_KEY": "",
        "DASHSCOPE_API_KEY": "",
    }):
        # 重载配置
        import importlib
        import config
        importlib.reload(config)
        from agent import CoPawAgent

        agent = CoPawAgent()
        result = agent.ask("测试问题", "fake-session-id")

        assert result["answer_source"] == "demo"
        assert result["llm_used"] is False
        assert result["model"] is None
        assert "测试问题" in result["answer"]
        assert result["response_time_ms"] >= 0


def test_agent_capabilities_no_config():
    """能力探测: 无配置时返回 False"""
    import sys, os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    with patch.dict(os.environ, {
        "IRA_COPAW_APP_URL": "",
        "IRA_COPAW_API_KEY": "",
        "DASHSCOPE_API_KEY": "",
    }):
        import importlib
        import config
        importlib.reload(config)
        from agent import CoPawAgent

        agent = CoPawAgent()
        caps = agent.get_capabilities()
        assert caps["copaw_configured"] is False
        assert caps["bailian_configured"] is False
